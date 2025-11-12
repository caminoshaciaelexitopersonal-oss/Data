import React, { useEffect, useReducer, useRef, useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { MainContent } from './components/MainContent';
import { NotificationCenter } from './components/NotificationCenter';
import { SheetSelectionModal } from './components/SheetSelectionModal';
import { ElbowMethodModal } from './components/ElbowMethodModal';
import { initialState, reducer } from './reducer';
import { Action, Notification, State } from './types';
import { loadDataFromFile, loadSheetFromExcel, analyzeDataQuality, detectOutliers } from './services/dataService';

// --- INLINED WORKER SCRIPT ---
const workerScript = `
// services/analysisWorker.js (Inlined and Complete)

// --- UTILITY FUNCTIONS ---
const euclideanDistance = (point1, point2) => Math.sqrt(point1.reduce((sum, value, index) => sum + (value - point2[index]) ** 2, 0));

// --- SCALING ---
const scaleData = (data) => {
  if (!data || data.length === 0) return { scaledData: [], means: [], stdDevs: [] };
  const numFeatures = data[0].length;
  const means = [];
  const stdDevs = [];
  for (let i = 0; i < numFeatures; i++) {
    const featureValues = data.map(row => row[i]);
    const mean = featureValues.reduce((a, b) => a + b, 0) / featureValues.length;
    const stdDev = Math.sqrt(featureValues.map(x => (x - mean) ** 2).reduce((a, b) => a + b, 0) / featureValues.length);
    means.push(mean);
    stdDevs.push(stdDev || 1);
  }
  const scaledData = data.map(row => row.map((value, index) => (value - means[index]) / stdDevs[index]));
  return { scaledData, means, stdDevs };
};

// --- CLUSTERING METRICS ---
const combinations = (n, k) => {
    if (k < 0 || k > n) return 0;
    if (k === 0 || k === n) return 1;
    if (k > n / 2) k = n - k;
    let res = 1;
    for (let i = 1; i <= k; i++) {
        res = res * (n - i + 1) / i;
    }
    return res;
};

const calculateAdjustedRandIndex = (contingencyTable) => {
    const a = Object.values(contingencyTable).map(row => Object.values(row).reduce((s, v) => s + v, 0));
    const b = Object.keys(Object.values(contingencyTable)[0] || {}).map(label => 
        Object.values(contingencyTable).reduce((s, row) => s + (row[label] || 0), 0)
    );
    const n = a.reduce((s, v) => s + v, 0);
    if (n < 2) return 1.0;

    const sumNij2 = Object.values(contingencyTable).flatMap(Object.values).reduce((s, v) => s + combinations(v, 2), 0);
    const sumA2 = a.reduce((s, v) => s + combinations(v, 2), 0);
    const sumB2 = b.reduce((s, v) => s + combinations(v, 2), 0);
    
    const index = sumNij2;
    const expectedIndex = (sumA2 * sumB2) / combinations(n, 2);
    const maxIndex = (sumA2 + sumB2) / 2;
    const denominator = (maxIndex - expectedIndex);

    return denominator === 0 ? 1.0 : (index - expectedIndex) / denominator;
};

const calculateSilhouetteScore = (data, assignments) => {
    if (data.length < 2) return 1.0;
    const uniqueClusters = [...new Set(assignments)];
    if (uniqueClusters.length < 2) return 0.0; // Cannot be calculated for a single cluster

    let totalSilhouette = 0;
    for (let i = 0; i < data.length; i++) {
        const myCluster = assignments[i];
        if (myCluster === -1) continue; // Noise points don't get a score

        let a_i = 0, sameClusterCount = 0;
        const otherClusterDistances = {};

        for (let j = 0; j < data.length; j++) {
            if (i === j) continue;
            const dist = euclideanDistance(data[i], data[j]);
            if (assignments[j] === myCluster) {
                a_i += dist;
                sameClusterCount++;
            } else if (assignments[j] !== -1) {
                if (!otherClusterDistances[assignments[j]]) otherClusterDistances[assignments[j]] = { sum: 0, count: 0 };
                otherClusterDistances[assignments[j]].sum += dist;
                otherClusterDistances[assignments[j]].count++;
            }
        }

        a_i = sameClusterCount > 0 ? a_i / sameClusterCount : 0;
        
        let b_i = Infinity;
        for (const clusterId in otherClusterDistances) {
            const avgDist = otherClusterDistances[clusterId].sum / otherClusterDistances[clusterId].count;
            if (avgDist < b_i) b_i = avgDist;
        }

        if (b_i === Infinity) b_i = 0; // Only one cluster found

        totalSilhouette += (Math.max(a_i, b_i) === 0) ? 0 : (b_i - a_i) / Math.max(a_i, b_i);
    }
    
    const validPoints = assignments.filter(a => a !== -1).length;
    return validPoints > 0 ? totalSilhouette / validPoints : 0;
};


// --- CLUSTERING ALGORITHMS ---
const runKMeans = (data, k, maxIterations = 100) => {
  if (data.length < k) throw new Error("Cannot have more clusters than data points.");
  let centroids = [];
  const usedIndices = new Set();
  while (centroids.length < k) {
      const randomIndex = Math.floor(Math.random() * data.length);
      if (!usedIndices.has(randomIndex)) {
          centroids.push(data[randomIndex]);
          usedIndices.add(randomIndex);
      }
  }
  let assignments = new Array(data.length).fill(0);
  for (let iter = 0; iter < maxIterations; iter++) {
    let changed = false;
    data.forEach((point, pointIndex) => {
      let minDistance = Infinity, closestCentroidIndex = 0;
      centroids.forEach((centroid, centroidIndex) => {
        const distance = euclideanDistance(point, centroid);
        if (distance < minDistance) { minDistance = distance; closestCentroidIndex = centroidIndex; }
      });
      if (assignments[pointIndex] !== closestCentroidIndex) { assignments[pointIndex] = closestCentroidIndex; changed = true; }
    });
    if (!changed) break;
    const newCentroids = Array(k).fill(0).map(() => Array(data[0].length).fill(0));
    const clusterCounts = Array(k).fill(0);
    data.forEach((point, pointIndex) => {
      const clusterIndex = assignments[pointIndex];
      clusterCounts[clusterIndex]++;
      point.forEach((value, featureIndex) => newCentroids[clusterIndex][featureIndex] += value);
    });
    newCentroids.forEach((sum, clusterIndex) => {
      if(clusterCounts[clusterIndex] > 0) newCentroids[clusterIndex] = sum.map(v => v / clusterCounts[clusterIndex]);
      else newCentroids[clusterIndex] = data[Math.floor(Math.random() * data.length)];
    });
    centroids = newCentroids;
  }
  let inertia = 0;
  data.forEach((point, pointIndex) => {
    const centroid = centroids[assignments[pointIndex]];
    if (centroid) inertia += euclideanDistance(point, centroid) ** 2;
  });
  return { assignments, centroids, inertia };
};

const calculateElbowCurve = (scaledData, maxK) => {
    const elbowData = [];
    const upperK = Math.min(maxK, scaledData.length -1, 15);
    for (let k = 2; k <= upperK; k++) {
        self.postMessage({ type: 'ANALYSIS_PROGRESS', payload: 'Calculando codo para K=' + k + '...' });
        const { assignments, inertia } = runKMeans(scaledData, k, 100);
        const silhouette = calculateSilhouetteScore(scaledData, assignments);
        elbowData.push({ k, inertia, silhouette });
    }
    return elbowData;
}

const runDBSCAN = (data, eps, minPts) => {
    const UNCLASSIFIED = 0, NOISE = -1;
    const regionQuery = (pointIndex) => {
        const neighbors = [];
        for (let i = 0; i < data.length; i++) if (pointIndex !== i && euclideanDistance(data[pointIndex], data[i]) < eps) neighbors.push(i);
        return neighbors;
    }
    const expandCluster = (assignments, pointIndex, neighbors, clusterId) => {
        assignments[pointIndex] = clusterId;
        let i = 0;
        while(i < neighbors.length) {
            const currentPointIndex = neighbors[i];
            if (assignments[currentPointIndex] === UNCLASSIFIED) {
                assignments[currentPointIndex] = clusterId;
                const currentNeighbors = regionQuery(currentPointIndex);
                if (currentNeighbors.length >= minPts) neighbors = neighbors.concat(currentNeighbors.filter(p => !neighbors.includes(p)));
            } else if (assignments[currentPointIndex] === NOISE) assignments[currentPointIndex] = clusterId;
            i++;
        }
        return assignments;
    }
    if(data.length === 0) return { assignments: [] };
    let assignments = new Array(data.length).fill(UNCLASSIFIED), clusterId = 0;
    for (let i = 0; i < data.length; i++) {
        if (assignments[i] === UNCLASSIFIED) {
            const neighbors = regionQuery(i);
            if (neighbors.length < minPts) assignments[i] = NOISE;
            else { assignments = expandCluster(assignments, i, neighbors, clusterId); clusterId++; }
        }
    }
    return { assignments };
};

const runHierarchicalClustering = (data, numClusters) => {
    if (data.length === 0 || numClusters < 1) return { assignments: [], clusters: [] };
    if (numClusters > data.length) throw new Error("Number of clusters cannot be greater than the number of data points.");
    let clusters = data.map((_, i) => [i]);
    while (clusters.length > numClusters) {
        let closestPair = { i: -1, j: -1, dist: Infinity };
        for (let i = 0; i < clusters.length; i++) {
            for (let j = i + 1; j < clusters.length; j++) {
                let totalDist = 0, pairCount = 0;
                clusters[i].forEach(p1Idx => clusters[j].forEach(p2Idx => { totalDist += euclideanDistance(data[p1Idx], data[p2Idx]); pairCount++; }));
                const avgDist = totalDist / (pairCount || 1);
                if (avgDist < closestPair.dist) closestPair = { i, j, dist: avgDist };
            }
        }
        const { i, j } = closestPair;
        const [clusterIdx1, clusterIdx2] = [i,j].sort((a,b) => a-b);
        const mergedClusters = clusters[clusterIdx1].concat(clusters[clusterIdx2]);
        clusters.splice(clusterIdx2, 1);
        clusters.splice(clusterIdx1, 1);
        clusters.push(mergedClusters);
    }
    const assignments = new Array(data.length).fill(-1);
    clusters.forEach((cluster, clusterId) => cluster.forEach(pointIndex => assignments[pointIndex] = clusterId));
    return { assignments };
};

// --- CLASSIFICATION/REGRESSION UTILS ---
const trainTestSplit = (data, testSize = 0.25) => {
    const shuffled = [...data].sort(() => 0.5 - Math.random());
    const splitIndex = Math.floor(shuffled.length * (1 - testSize));
    return { train: shuffled.slice(0, splitIndex), test: shuffled.slice(splitIndex) };
};

const encodeLabels = (data, columns) => {
    const encoders = {}, decoders = {};
    const encodedData = JSON.parse(JSON.stringify(data));
    columns.forEach(col => {
        if (!encodedData.length || encodedData.every(r => typeof r[col] === 'number' || r[col] === null)) return;
        encoders[col] = {}, decoders[col] = {};
        const uniqueValues = [...new Set(encodedData.map(r => r[col]))].filter(v => v !== null && v !== undefined);
        uniqueValues.forEach((val, i) => { encoders[col][String(val)] = i; decoders[col][i] = String(val); });
        encodedData.forEach(row => { if (row[col] !== null && row[col] !== undefined) row[col] = encoders[col][String(row[col])]; });
    });
    return { encodedData, encoders, decoders };
};

const calculateMetrics = (predictions, classLabels, targetVariable, decoders) => {
    let correct = 0;
    const decodedClassLabels = classLabels.map(c => decoders[targetVariable][c]);
    const confusionMatrix = Array(classLabels.length).fill(0).map(() => Array(classLabels.length).fill(0));
    predictions.forEach(({ actual, predicted }) => {
        if (actual === predicted) correct++;
        if (confusionMatrix[actual] && confusionMatrix[actual][predicted] !== undefined) confusionMatrix[actual][predicted]++;
    });
    const report = {};
    classLabels.forEach(c => {
        const classIndex = c;
        const tp = confusionMatrix[classIndex][classIndex] || 0;
        const fp = confusionMatrix.reduce((sum, row, i) => sum + (i !== classIndex ? (row[classIndex] || 0) : 0), 0);
        const fn = (confusionMatrix[classIndex] || []).reduce((sum, val, i) => sum + (i !== classIndex ? (val || 0) : 0), 0);
        const precision = tp / (tp + fp) || 0, recall = tp / (tp + fn) || 0, f1Score = 2 * (precision * recall) / (precision + recall) || 0;
        report[decodedClassLabels[classIndex]] = { precision, recall, f1Score, support: tp + fn };
    });
    return { accuracy: predictions.length > 0 ? correct / predictions.length : 0, confusionMatrix, report, classLabels: decodedClassLabels };
};

const prepareClassificationData = (data, target, features, testSize) => {
    const { encodedData, decoders } = encodeLabels(data, [target, ...features]);
    const { train, test } = trainTestSplit(encodedData, testSize);
    const classLabels = [...new Set(encodedData.map(d => d[target]))].filter(v => v !== null).sort((a,b) => a - b);
    return { train, test, decoders, classLabels, encodedData };
}

// --- CLASSIFICATION/REGRESSION ALGORITHMS ---
const runNaiveBayes = (data, params, precomputed = null) => {
    const { target, features, testSize } = params;
    const { train, test, decoders, classLabels } = precomputed || prepareClassificationData(data, target, features, testSize);
    const classPriors = {}, featureLikelihoods = {};
    classLabels.forEach(c => {
        const classData = train.filter(d => d[target] === c);
        classPriors[c] = classData.length / train.length;
        features.forEach(feature => {
            if (!featureLikelihoods[feature]) featureLikelihoods[feature] = {};
            const featureValues = classData.map(d => d[feature]).filter(v => typeof v === 'number');
            if (featureValues.length === 0) { featureLikelihoods[feature][c] = { mean: 0, std: 1e-9 }; return; }
            const mean = featureValues.reduce((a, b) => a + b, 0) / featureValues.length;
            const std = Math.sqrt(featureValues.map(x => (x - mean) ** 2).reduce((a, b) => a + b, 0) / featureValues.length) || 1e-9;
            featureLikelihoods[feature][c] = { mean, std };
        });
    });
    const predictions = test.map(row => {
        let bestClass = -1, maxPosterior = -Infinity;
        classLabels.forEach(c => {
            let posterior = Math.log(classPriors[c] || 1e-9);
            features.forEach(feature => {
                const likelihood = featureLikelihoods[feature]?.[c];
                if(likelihood) {
                    const { mean, std } = likelihood;
                    const val = row[feature];
                    if (typeof val === 'number') {
                        const exponent = -((val - mean) ** 2) / (2 * std ** 2);
                        posterior += exponent - Math.log(Math.sqrt(2 * Math.PI) * std);
                    }
                }
            });
            if (posterior > maxPosterior) { maxPosterior = posterior; bestClass = c; }
        });
        return { actual: row[target], predicted: bestClass };
    });
    const metrics = calculateMetrics(predictions, classLabels, target, decoders);
    return { ...metrics, targetVariable: target, algorithm: 'naive_bayes' };
};

const runLogisticRegression = (data, params, precomputed = null, learningRate = 0.01, iterations = 100) => {
    const { target, features, testSize } = params;
    const { train, test, decoders, classLabels } = precomputed || prepareClassificationData(data, target, features, testSize);
    if (classLabels.length !== 2) throw new Error("Logistic Regression currently supports only binary classification.");
    const X_train = train.map(row => features.map(f => row[f] ?? 0));
    const y_train = train.map(row => row[target]);
    let weights = new Array(features.length).fill(0), bias = 0;
    for (let i = 0; i < iterations; i++) {
        let grad_w = new Array(features.length).fill(0), grad_b = 0;
        for (let j = 0; j < X_train.length; j++) {
            const linear_model = X_train[j].reduce((acc, val, idx) => acc + val * weights[idx], 0) + bias;
            const y_pred = 1 / (1 + Math.exp(-linear_model));
            const error = y_pred - y_train[j];
            for (let k = 0; k < weights.length; k++) grad_w[k] += X_train[j][k] * error;
            grad_b += error;
        }
        weights = weights.map((w, k) => w - learningRate * (grad_w[k] / X_train.length));
        bias -= learningRate * (grad_b / X_train.length);
    }
    const predictions = test.map(row => {
        const linear_model = features.reduce((acc, val, idx) => acc + (row[val] ?? 0) * weights[idx], 0) + bias;
        const prob = 1 / (1 + Math.exp(-linear_model));
        return { actual: row[target], predicted: prob > 0.5 ? classLabels[1] : classLabels[0] };
    });
    const metrics = calculateMetrics(predictions, classLabels, target, decoders);
    return { ...metrics, targetVariable: target, algorithm: 'logistic_regression' };
};

const runDecisionTree = (data, params, precomputed = null) => {
    const { target, features, testSize, maxDepth, minSamplesSplit } = params;
    const { train, test, decoders, classLabels } = precomputed || prepareClassificationData(data, target, features, testSize);
    const gini = (groups) => {
        let gini = 0.0;
        const totalSize = groups.reduce((sum, g) => sum + g.length, 0);
        for (const group of groups) {
            const size = group.length;
            if (size === 0) continue;
            let score = 0.0;
            const classCounts = [...new Set(group.map(r => r[target]))].map(c => group.filter(r => r[target] === c).length);
            for (const count of classCounts) score += (count / size) ** 2;
            gini += (1.0 - score) * (size / totalSize);
        }
        return gini;
    }
    const testSplit = (index, value, dataset) => {
        const left = [], right = [];
        for (const row of dataset) (row[features[index]] < value ? left : right).push(row);
        return [left, right];
    }
    const getSplit = (dataset) => {
        let b_index = 999, b_value = 999, b_score = 999, b_groups = null;
        for (let i = 0; i < features.length; i++) {
            for (const row of dataset) {
                const groups = testSplit(i, row[features[i]], dataset);
                const gini_val = gini(groups);
                if (gini_val < b_score) { b_index = i; b_value = row[features[i]]; b_score = gini_val; b_groups = groups; }
            }
        }
        return { index: b_index, value: b_value, groups: b_groups };
    }
    const toTerminal = (group) => {
        const outcomes = group.map(r => r[target]);
        return outcomes.sort((a, b) => outcomes.filter(v => v === a).length - outcomes.filter(v => v === b).length).pop();
    }
    const split = (node, depth) => {
        const [left, right] = node.groups;
        delete node.groups;
        if (!left.length || !right.length) { node.left = node.right = toTerminal(left.concat(right)); return; }
        if (depth >= maxDepth) { node.left = toTerminal(left); node.right = toTerminal(right); return; }
        if (left.length <= minSamplesSplit) node.left = toTerminal(left);
        else { node.left = getSplit(left); split(node.left, depth + 1); }
        if (right.length <= minSamplesSplit) node.right = toTerminal(right);
        else { node.right = getSplit(right); split(node.right, depth + 1); }
    }
    const buildTree = (train) => { const root = getSplit(train); split(root, 1); return root; }
    const predict = (node, row) => {
        if (row[features[node.index]] < node.value) {
            if (typeof node.left === 'object') return predict(node.left, row); else return node.left;
        } else {
            if (typeof node.right === 'object') return predict(node.right, row); else return node.right;
        }
    }
    const tree = buildTree(train);
    const predictions = test.map(row => ({ actual: row[target], predicted: predict(tree, row) }));
    const metrics = calculateMetrics(predictions, classLabels, target, decoders);
    return { ...metrics, targetVariable: target, algorithm: 'decision_tree' };
};

const runLinearRegression = (data, params) => {
    const { target, features } = params;
    const feature = features[0];
    const numericData = data.map(r => ({x: r[feature], y: r[target]})).filter(p => typeof p.x === 'number' && typeof p.y === 'number' && isFinite(p.x) && isFinite(p.y));
    if (numericData.length < 2) throw new Error("Not enough valid numeric data points for regression.");
    const n = numericData.length;
    const sumX = numericData.reduce((s, p) => s + p.x, 0), sumY = numericData.reduce((s, p) => s + p.y, 0);
    const sumXY = numericData.reduce((s, p) => s + p.x * p.y, 0), sumX2 = numericData.reduce((s, p) => s + p.x * p.x, 0);
    const meanY = sumY / n;
    const denominator = (n * sumX2 - sumX * sumX);
    if(denominator === 0) throw new Error("Cannot perform linear regression, feature variable has zero variance.");
    const m = (n * sumXY - sumX * sumY) / denominator, b = (sumY - m * sumX) / n;
    const predictions = numericData.map(p => ({ actual: p.y, predicted: m * p.x + b }));
    let ssTotal = 0, ssResidual = 0, mse = 0;
    predictions.forEach(({ actual, predicted }) => {
        ssTotal += (actual - meanY) ** 2;
        ssResidual += (actual - predicted) ** 2;
        mse += (actual-predicted) ** 2;
    });
    return { rSquared: ssTotal === 0 ? 1 : 1 - (ssResidual / ssTotal), mse: mse / predictions.length, predictions, targetVariable: target, featureVariables: [feature] };
};

// --- PCA SERVICE ---
const transpose = (matrix) => matrix[0].map((_, i) => matrix.map(row => row[i]));
const multiply = (A, B) => A.map((row, i) => B[0].map((_, j) => row.reduce((sum, _, k) => sum + A[i][k] * B[k][j], 0)));
const covariance = (matrix) => {
    const n = matrix.length;
    const means = transpose(matrix).map(col => col.reduce((s, v) => s + v, 0) / n);
    const centered = matrix.map(row => row.map((v, i) => v - means[i]));
    return multiply(transpose(centered), centered).map(row => row.map(v => v / (n - 1)));
};
const jacobi = (matrix, maxIter = 100, tolerance = 1e-9) => {
    let A = JSON.parse(JSON.stringify(matrix));
    const n = A.length;
    let V = Array(n).fill(0).map((_, i) => Array(n).fill(0).map((_, j) => i === j ? 1 : 0));
    for (let iter = 0; iter < maxIter; iter++) {
        let maxVal = 0, p = 0, q = 1;
        for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) if (Math.abs(A[i][j]) > maxVal) { maxVal = Math.abs(A[i][j]); p = i; q = j; }
        if (maxVal < tolerance) break;
        const theta = Math.abs(A[p][p] - A[q][q]) < tolerance ? (A[p][p] > A[q][q] ? Math.PI / 4 : -Math.PI / 4) : 0.5 * Math.atan(2 * A[p][q] / (A[p][p] - A[q][q]));
        const c = Math.cos(theta), s = Math.sin(theta);
        const A_pp = A[p][p], A_qq = A[q][q];
        A[p][p] = c * c * A_pp - 2 * s * c * A[p][q] + s * s * A_qq;
        A[q][q] = s * s * A_pp + 2 * s * c * A[p][q] + c * c * A_qq;
        A[p][q] = A[q][p] = 0;
        for (let i = 0; i < n; i++) if (i !== p && i !== q) { const A_ip = A[i][p]; A[i][p] = A[p][i] = c * A_ip - s * A[i][q]; A[i][q] = A[q][i] = s * A_ip + c * A[i][q]; }
        for (let i = 0; i < n; i++) { const V_ip = V[i][p]; V[i][p] = c * V_ip - s * V[i][q]; V[i][q] = s * V_ip + c * V[i][q]; }
    }
    return { eigenvalues: A.map((row, i) => row[i]), eigenvectors: transpose(V) };
};
const runPCA = (data, numComponents) => {
    const { scaledData } = scaleData(data);
    const covMatrix = covariance(scaledData);
    const { eigenvalues, eigenvectors } = jacobi(covMatrix);
    const pairs = eigenvalues.map((val, i) => ({ eigenvalue: val, eigenvector: eigenvectors[i] }));
    pairs.sort((a, b) => b.eigenvalue - a.eigenvalue);
    const totalVariance = eigenvalues.reduce((a, b) => a + b, 0);
    const explainedVariance = pairs.slice(0, numComponents).map(p => p.eigenvalue / totalVariance);
    const projectionMatrix = transpose(pairs.slice(0, numComponents).map(p => p.eigenvector));
    const pcaData = multiply(scaledData, projectionMatrix);
    const newData = pcaData.map(row => row.reduce((obj, val, i) => ({ ...obj, ['Componente_' + (i + 1)]: val }), {}));
    self.postMessage({ type: 'PCA_COMPLETE', payload: { data: newData, explainedVariance } });
};

// --- WORKER MESSAGE HANDLER ---
self.onmessage = (event) => {
    const { type, payload } = event.data;
    try {
        const { data, params } = payload;
        const numericHeaders = params.features;
        // FIX: Robustly parse numeric data, handling non-numeric values gracefully to prevent calculation errors.
        const numericData = data.map(row => 
            numericHeaders.map(header => {
                const val = parseFloat(row[header]);
                return isNaN(val) ? 0 : val;
            })
        );
        
        if (type === 'CALCULATE_ELBOW' || type === 'RUN_CLUSTERING') {
            const { scaledData } = scaleData(numericData);
            if (type === 'CALCULATE_ELBOW') {
                if (numericHeaders.length < 2) throw new Error("El método del codo requiere al menos dos características.");
                const elbowData = calculateElbowCurve(scaledData, params.maxK);
                self.postMessage({ type: 'ELBOW_DATA_COMPLETE', payload: elbowData });
            } else { // RUN_CLUSTERING
                 if (params.algorithm === 'hierarchical' && numericHeaders.length < 1) throw new Error("Clustering Jerárquico requiere al menos una característica.");
                 if (params.algorithm !== 'hierarchical' && numericHeaders.length < 2) throw new Error("Este algoritmo requiere al menos dos características.");
                let result;
                let assignments;
                if (params.algorithm === 'kmeans') {
                    if (params.autoK) {
                        const elbowData = calculateElbowCurve(scaledData, params.maxK);
                        let bestK = 3; 
                        if(elbowData.length > 0) {
                            bestK = elbowData.reduce((max, p) => p.silhouette > max.silhouette ? p : max, elbowData[0]).k;
                        }
                        const kmeansResult = runKMeans(scaledData, bestK, 100);
                        assignments = kmeansResult.assignments;
                        result = { ...kmeansResult, elbowData, inertia: elbowData.find(d=>d.k === bestK)?.inertia };
                    } else {
                         const kmeansResult = runKMeans(scaledData, params.k, 100);
                         assignments = kmeansResult.assignments;
                         result = kmeansResult;
                    }
                } else if (params.algorithm === 'dbscan' || params.algorithm === 'hierarchical') {
                    const clusteringResult = params.algorithm === 'dbscan' ? runDBSCAN(scaledData, params.eps, params.minPts) : runHierarchicalClustering(scaledData, params.numClusters);
                    assignments = clusteringResult.assignments;
                    const clusterIds = [...new Set(assignments)].filter(id => id !== -1);
                    const centroids = clusterIds.map(id => {
                        const clusterPoints = scaledData.filter((_, i) => assignments[i] === id);
                        if (clusterPoints.length === 0) return Array(scaledData[0].length).fill(0);
                        return clusterPoints[0].map((_, fIdx) => clusterPoints.reduce((sum, p) => sum + p[fIdx], 0) / clusterPoints.length);
                    });
                    result = { assignments, centroids };
                }

                // --- Calculate advanced metrics if ground truth is provided ---
                if (params.groundTruthColumn && assignments) {
                    const trueLabels = data.map(row => row[params.groundTruthColumn]);
                    const uniqueTrueLabels = [...new Set(trueLabels)];
                    const uniqueClusterLabels = [...new Set(assignments)];

                    const contingencyTable = {};
                    uniqueClusterLabels.forEach(c => contingencyTable['Cluster ' + (c === -1 ? 'Ruido' : c)] = {});

                    for (let i = 0; i < assignments.length; i++) {
                        const cluster = 'Cluster ' + (assignments[i] === -1 ? 'Ruido' : assignments[i]);
                        const label = String(trueLabels[i]);
                         if (!contingencyTable[cluster][label]) contingencyTable[cluster][label] = 0;
                        contingencyTable[cluster][label]++;
                    }
                    result.contingencyTable = contingencyTable;
                    result.adjustedRandIndex = calculateAdjustedRandIndex(contingencyTable);
                    result.silhouetteScore = calculateSilhouetteScore(scaledData, assignments);
                }

                self.postMessage({ type: 'CLUSTERING_COMPLETE', payload: { ...result, algorithm: params.algorithm, featureNames: numericHeaders } });
            }
        } else if (type === 'RUN_CLASSIFICATION') {
             const precomputed = prepareClassificationData(data, params.target, params.features, params.testSize);
             let result;
             if (params.algorithm === 'logistic_regression') result = runLogisticRegression(data, params, precomputed);
             else if (params.algorithm === 'decision_tree') result = runDecisionTree(data, params, precomputed);
             else result = runNaiveBayes(data, params, precomputed);
             self.postMessage({ type: 'CLASSIFICATION_COMPLETE', payload: result });
        } else if (type === 'RUN_REGRESSION') {
            self.postMessage({ type: 'REGRESSION_COMPLETE', payload: runLinearRegression(payload.data, payload.params) });
        } else if (type === 'RUN_MODEL_COMPARISON') {
            const precomputed = prepareClassificationData(data, params.target, params.features, params.testSize);
            const comparisonResults = [];
            for (let i = 0; i < params.algorithms.length; i++) {
                const algo = params.algorithms[i];
                const algoName = { 'naive_bayes': 'Naive Bayes', 'logistic_regression': 'Regresión Logística', 'decision_tree': 'Árbol de Decisión' }[algo] || algo;
                self.postMessage({ type: 'ANALYSIS_PROGRESS', payload: 'Ejecutando ' + (i + 1) + ' de ' + params.algorithms.length + ': ' + algoName + '...' });
                try {
                    let result;
                    if (algo === 'logistic_regression') result = runLogisticRegression(data, params, precomputed);
                    else if (algo === 'decision_tree') result = runDecisionTree(data, params, precomputed);
                    else result = runNaiveBayes(data, params, precomputed);
                    const reportValues = Object.values(result.report);
                    comparisonResults.push({
                        algorithm: algoName,
                        accuracy: result.accuracy,
                        precision: reportValues.reduce((s, m) => s + m.precision, 0) / reportValues.length,
                        recall: reportValues.reduce((s, m) => s + m.recall, 0) / reportValues.length,
                        f1Score: reportValues.reduce((s, m) => s + m.f1Score, 0) / reportValues.length,
                    });
                } catch (e) { comparisonResults.push({ algorithm: algoName, error: e.message }); }
            }
            self.postMessage({ type: 'MODEL_COMPARISON_COMPLETE', payload: comparisonResults });
        } else if (type === 'RUN_PCA') {
            runPCA(numericData, params.numComponents);
        }
    } catch (error) {
        self.postMessage({ type: 'ANALYSIS_ERROR', payload: { message: error.message, stack: error.stack } });
    }
};
`;

// Assume window.aistudio is available in the environment
// FIX: The AIStudio interface was moved to types.ts to avoid global scope conflicts.

const App: React.FC = () => {
    const [state, dispatch] = useReducer(reducer, initialState);
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [isKeyReady, setIsKeyReady] = useState(false);
    const notificationId = useRef(0);
    const workerRef = useRef<Worker | null>(null);

    const addNotification = (message: string, type: 'success' | 'error' | 'info') => {
        const id = notificationId.current++;
        setNotifications(prev => [...prev, { id, message, type }]);
    };

    const removeNotification = (id: number) => {
        setNotifications(prev => prev.filter(n => n.id !== id));
    };

    useEffect(() => {
        const checkApiKey = async () => {
            if (window.aistudio && typeof window.aistudio.hasSelectedApiKey === 'function') {
                try {
                    const hasKey = await window.aistudio.hasSelectedApiKey();
                    setIsKeyReady(hasKey);
                } catch (error) {
                    console.error("Error checking for API key:", error);
                    setIsKeyReady(false); // Assume not ready on error
                }
            } else {
                console.warn("window.aistudio API not found. API key status check is disabled.");
                setIsKeyReady(true); // Assume ready to avoid blocking UI if the API doesn't exist.
            }
        };
        checkApiKey();
    }, []);

    useEffect(() => {
        let worker: Worker | null = null;
        let objectURL: string | null = null;

        try {
            const blob = new Blob([workerScript], { type: 'application/javascript' });
            objectURL = URL.createObjectURL(blob);
            worker = new Worker(objectURL);
            workerRef.current = worker;

            worker.onmessage = (event) => {
                const { type, payload } = event.data;
                dispatch({ type: 'SET_LOADING', payload: { isLoading: false } });
                switch (type) {
                    case 'ELBOW_DATA_COMPLETE':
                        dispatch({ type: 'SET_ELBOW_DATA', payload });
                        dispatch({ type: 'SET_ELBOW_MODAL_OPEN', payload: true });
                        addNotification('Análisis del codo completado.', 'success');
                        break;
                    case 'CLUSTERING_COMPLETE':
                        dispatch({ type: 'SET_CLUSTER_RESULTS', payload });
                        addNotification('Análisis de clustering completado.', 'success');
                        break;
                    case 'CLASSIFICATION_COMPLETE':
                        dispatch({ type: 'SET_CLASSIFICATION_RESULTS', payload });
                        addNotification('Clasificación completada.', 'success');
                        break;
                    case 'REGRESSION_COMPLETE':
                        dispatch({ type: 'SET_REGRESSION_RESULTS', payload });
                        addNotification('Regresión completada.', 'success');
                        break;
                    case 'PCA_COMPLETE': {
                        const { data: pcaData, explainedVariance } = payload;
                        const newQualityReport = analyzeDataQuality(pcaData);
                        const newOutlierReport = detectOutliers(pcaData, newQualityReport);
                        dispatch({ type: 'SET_PROCESSED_DATA', payload: { processedData: pcaData, qualityReport: newQualityReport, outlierReport: newOutlierReport }});
                        addNotification('PCA completado. Varianza explicada: ' + (explainedVariance.reduce((a:number, b:number) => a + b, 0) * 100).toFixed(1) + '%', 'success');
                        break;
                    }
                    case 'ANALYSIS_PROGRESS':
                        dispatch({ type: 'SET_LOADING', payload: { isLoading: true, message: payload } });
                        break;
                    case 'MODEL_COMPARISON_COMPLETE':
                        dispatch({ type: 'SET_MODEL_COMPARISON_RESULTS', payload });
                        addNotification('Comparación de modelos completada.', 'success');
                        break;
                    case 'ANALYSIS_ERROR':
                        addNotification(`Error en el análisis: ${payload.message}`, 'error');
                        console.error('Worker Error:', payload);
                        break;
                }
            };
            
            worker.onerror = (event) => {
                console.error("Worker loading error:", event);
                addNotification(`Error al inicializar el worker: ${event.message}`, 'error');
                dispatch({ type: 'SET_LOADING', payload: { isLoading: false } });
            };

        } catch (error) {
            const err = error as Error;
            console.error("Failed to initialize worker:", err);
            addNotification(`No se pudo cargar el worker de análisis: ${err.message}`, 'error');
            dispatch({ type: 'SET_LOADING', payload: { isLoading: false } });
        }

        return () => {
            workerRef.current?.terminate();
            if (objectURL) {
                URL.revokeObjectURL(objectURL);
            }
        };
    }, []);

    const runAnalysis = (type: 'clustering' | 'classification' | 'regression' | 'model-comparison' | 'pca' | 'elbow', params: any) => {
        dispatch({ type: 'SET_LOADING', payload: { isLoading: true, message: `Ejecutando ${type}...` } });
        let workerPayloadType: string;
        switch (type) {
            case 'clustering': workerPayloadType = 'RUN_CLUSTERING'; break;
            case 'classification': workerPayloadType = 'RUN_CLASSIFICATION'; break;
            case 'regression': workerPayloadType = 'RUN_REGRESSION'; break;
            case 'model-comparison': workerPayloadType = 'RUN_MODEL_COMPARISON'; break;
            case 'pca': workerPayloadType = 'RUN_PCA'; break;
            case 'elbow': workerPayloadType = 'CALCULATE_ELBOW'; break;
            default:
                addNotification('Tipo de análisis desconocido.', 'error');
                dispatch({ type: 'SET_LOADING', payload: { isLoading: false } });
                return;
        }

        workerRef.current?.postMessage({
            type: workerPayloadType,
            payload: { data: state.processedData, params },
        });
    };
    
    const handleFileLoad = async (file: File, secondaryIdentifier?: string, type?: 'sheet') => {
        dispatch({ type: 'SET_LOADING', payload: { isLoading: true, message: 'Cargando datos...' } });
        try {
            if (secondaryIdentifier && type === 'sheet') {
                const data = await loadSheetFromExcel(file, secondaryIdentifier);

                const qualityReport = analyzeDataQuality(data);
                const outlierReport = detectOutliers(data, qualityReport);
                dispatch({ type: 'SET_DATA_LOADED', payload: { data, originalData: [...data.map(row => ({...row}))], fileName: file.name, qualityReport, outlierReport } });
                dispatch({ type: 'SET_VIEW', payload: 'data-preview' });
                addNotification(`Hoja '${secondaryIdentifier}' cargada correctamente.`, 'success');
            } else {
                const { data, fileName, sheetNames } = await loadDataFromFile(file);
                if (sheetNames && sheetNames.length > 1) {
                    dispatch({ type: 'SET_SHEET_MODAL', payload: { isOpen: true, sheetNames, file } });
                }
                else {
                    const qualityReport = analyzeDataQuality(data);
                    const outlierReport = detectOutliers(data, qualityReport);
                    dispatch({ type: 'SET_DATA_LOADED', payload: { data, originalData: [...data.map(row => ({...row}))], fileName, qualityReport, outlierReport } });
                    dispatch({ type: 'SET_VIEW', payload: 'data-preview' });
                    addNotification(`Archivo '${fileName}' cargado correctamente.`, 'success');
                }
            }
        } catch (error) {
            const err = error as Error;
            addNotification(`Error al cargar el archivo: ${err.message}`, 'error');
        } finally {
            dispatch({ type: 'SET_LOADING', payload: { isLoading: false } });
        }
    };

    const handleSheetSelect = (sheetName: string) => {
        if (state.fileToProcess) {
            handleFileLoad(state.fileToProcess, sheetName, 'sheet');
        }
        dispatch({ type: 'SET_SHEET_MODAL', payload: { isOpen: false } });
    };

    const LoadingSpinner = () => (
      <div className="fixed inset-0 bg-black/70 z-50 flex flex-col items-center justify-center">
        <svg className="animate-spin h-16 w-16 text-cyan-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 * 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p className="mt-4 text-lg text-white">{state.loadingMessage}</p>
      </div>
    );

    return (
        <div className="bg-gray-900 text-slate-200 flex h-screen font-sans">
            {state.isLoading && <LoadingSpinner />}
            
            {state.isSheetModalOpen && (
                <SheetSelectionModal
                    sheetNames={state.sheetNames}
                    onSelect={handleSheetSelect}
                    onCancel={() => dispatch({ type: 'SET_SHEET_MODAL', payload: { isOpen: false } })}
                    fileName={state.fileToProcess?.name || ''}
                />
            )}
            
            {state.isElbowModalOpen && state.elbowPlotData && (
                <ElbowMethodModal
                    data={state.elbowPlotData}
                    onApply={(k) => {
                        dispatch({ type: 'UPDATE_CLUSTERING_PARAMS', payload: { k, autoK: false } });
                        dispatch({ type: 'SET_ELBOW_MODAL_OPEN', payload: false });
                        addNotification(`Número de clusters (K) actualizado a ${k}.`, 'info');
                    }}
                    onClose={() => dispatch({ type: 'SET_ELBOW_MODAL_OPEN', payload: false })}
                />
            )}

            
            <NotificationCenter notifications={notifications} onRemove={removeNotification} />
            
            <Sidebar 
                state={state} 
                dispatch={dispatch as React.Dispatch<Action>} 
                onFileLoad={(file) => handleFileLoad(file)}
                runAnalysis={runAnalysis}
            />

            <main className="flex-1 overflow-y-auto bg-gray-800/30">
                <MainContent 
                    state={state} 
                    dispatch={dispatch as React.Dispatch<Action>} 
                    runAnalysis={runAnalysis} 
                    addNotification={addNotification}
                    isKeyReady={isKeyReady}
                    setIsKeyReady={setIsKeyReady}
                />
            </main>
        </div>
    );
};

export default App;