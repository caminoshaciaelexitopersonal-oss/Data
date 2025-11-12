// reducer.ts
import { State, Action, View } from './types';

export const initialState: State = {
  processedData: [],
  originalData: [],
  fileName: '',
  sheetNames: [],
  isSheetModalOpen: false,
  isElbowModalOpen: false,
  elbowPlotData: null,
  currentView: 'data-preview',
  isLoading: false,
  loadingMessage: '',
  qualityReport: {},
  outlierReport: {},
  clusterResults: null,
  classificationResults: null,
  regressionResults: null,
  modelComparisonResults: null,
  problemContext: '',
  datasetMetadata: '',
  
  clusteringParams: {
    algorithm: 'kmeans',
    features: [],
    k: 3,
    autoK: false, // Default to manual K selection
    maxK: 10,
    eps: 0.5,
    minPts: 5,
    numClusters: 3,
    groundTruthColumn: undefined,
  },
  classificationParams: {
    algorithm: 'naive_bayes',
    target: '',
    features: [],
    testSize: 0.25,
    maxDepth: 5,
    minSamplesSplit: 2,
  },
  regressionParams: {
    target: '',
    features: [],
    testSize: 0.25,
  },
  modelComparisonParams: {
    algorithms: ['naive_bayes', 'decision_tree'],
    target: '',
    features: [],
    testSize: 0.25,
  },
  pcaParams: {
      features: [],
      numComponents: 2,
  },
  fileToProcess: null,
};

export const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload.isLoading, loadingMessage: action.payload.message || '' };

    case 'SET_DATA_LOADED':
      return {
        ...initialState, // Reset everything on new data load
        fileName: action.payload.fileName,
        originalData: action.payload.originalData,
        processedData: [...action.payload.originalData.map(row => ({...row}))], // Create a mutable copy
        qualityReport: action.payload.qualityReport,
        outlierReport: action.payload.outlierReport,
        isLoading: false,
      };

    case 'SET_PROCESSED_DATA':
      return {
        ...state,
        processedData: action.payload.processedData,
        qualityReport: action.payload.qualityReport,
        outlierReport: action.payload.outlierReport,
        isLoading: false,
        clusterResults: null,
        classificationResults: null,
        regressionResults: null,
        modelComparisonResults: null,
      };

    case 'SET_VIEW':
      return { ...state, currentView: action.payload };

    case 'SET_SHEET_MODAL':
      return {
          ...state,
          isSheetModalOpen: action.payload.isOpen,
          sheetNames: action.payload.sheetNames || [],
          fileToProcess: action.payload.file || null,
      };

    case 'SET_ELBOW_MODAL_OPEN':
        return { ...state, isElbowModalOpen: action.payload };

    case 'SET_ELBOW_DATA':
        return { ...state, elbowPlotData: action.payload };
    
    case 'SET_CLUSTER_RESULTS':
      return { ...state, clusterResults: action.payload, isLoading: false, currentView: 'clustering' };

    case 'SET_CLASSIFICATION_RESULTS':
      return { ...state, classificationResults: action.payload, isLoading: false, currentView: 'classification' };
    
    case 'SET_REGRESSION_RESULTS':
        return { ...state, regressionResults: action.payload, isLoading: false, currentView: 'regression' };

    case 'SET_MODEL_COMPARISON_RESULTS':
        return { ...state, modelComparisonResults: action.payload, isLoading: false, currentView: 'model-comparison' };

    case 'SET_PROBLEM_CONTEXT':
        return { ...state, problemContext: action.payload };
    
    case 'SET_DATASET_METADATA':
        return { ...state, datasetMetadata: action.payload };

    case 'UPDATE_CLUSTERING_PARAMS':
      return { ...state, clusteringParams: { ...state.clusteringParams, ...action.payload } };

    case 'UPDATE_CLASSIFICATION_PARAMS':
        return { ...state, classificationParams: { ...state.classificationParams, ...action.payload } };
    
    case 'UPDATE_REGRESSION_PARAMS':
        return { ...state, regressionParams: { ...state.regressionParams, ...action.payload } };
    
    case 'UPDATE_MODEL_COMPARISON_PARAMS':
        return { ...state, modelComparisonParams: { ...state.modelComparisonParams, ...action.payload } };
    
    case 'UPDATE_PCA_PARAMS':
        return { ...state, pcaParams: { ...state.pcaParams, ...action.payload } };

    case 'RESET_STATE':
        const defaultView: View = action.payload?.view || 'data-preview';
        return { 
            ...initialState, 
            currentView: defaultView,
            // Keep user-defined context on reset
            problemContext: state.problemContext, 
            datasetMetadata: state.datasetMetadata,
        };
    
    default:
      return state;
  }
};