// The AIStudio interface is defined in the global scope below to avoid module conflicts.

export type DataPoint = { [key: string]: string | number | null };

export type View = 'data-preview' | 'exploratory-data' | 'data-preparation' | 'clustering' | 'classification' | 'regression' | 'model-comparison' | 'exercise';

export interface Notification {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info';
}

export type Transformation =
  | { type: 'DROP_COLUMN'; column: string }
  | { type: 'FILL_NULLS'; column: string; strategy: 'mean' | 'median' | 'mode' }
  | { type: 'NORMALIZE'; column: string; method: 'z-score' | 'min-max' }
  | { type: 'REMOVE_OUTLIERS'; column: string }
  | { type: 'CAP_OUTLIERS'; column: string }
  | { type: 'ONE_HOT_ENCODE'; column: string };

export type QualityReport = { [key: string]: { nulls: number; type: string } };

export type OutlierReport = { [key: string]: { count: number; lowerBound: number; upperBound: number; } };

export interface ClusterResult {
  assignments: number[];
  centroids: number[][];
  featureNames: string[];
  algorithm: string;
  elbowData?: { k: number; inertia: number; silhouette: number }[];
  inertia?: number;
  silhouetteScore?: number;
  adjustedRandIndex?: number;
  contingencyTable?: { [cluster: string]: { [label: string]: number } };
}

export interface ClassificationMetric {
    precision: number;
    recall: number;
    f1Score: number;
    support: number;
}

export interface ClassificationResult {
  accuracy: number;
  confusionMatrix: number[][];
  report: { [className: string]: ClassificationMetric };
  classLabels: string[];
  targetVariable: string;
  algorithm: string;
}

export interface RegressionResult {
  rSquared: number;
  mse: number;
  predictions: { actual: number; predicted: number }[];
  targetVariable: string;
  featureVariables: string[];
}

export interface PCAResult {
    data: DataPoint[];
    explainedVariance: number[];
}

export interface ModelComparisonResultItem { 
    algorithm: string;
    accuracy?: number;
    precision?: number; // Macro-averaged
    recall?: number;    // Macro-averaged
    f1Score?: number;   // Macro-averaged
    error?: string;
}

export interface ClusteringParams {
  algorithm: 'kmeans' | 'dbscan' | 'hierarchical';
  features: string[];
  k: number;
  autoK: boolean;
  maxK: number;
  eps: number;
  minPts: number;
  numClusters: number;
  groundTruthColumn?: string;
}

export interface ClassificationParams {
  algorithm: 'naive_bayes' | 'logistic_regression' | 'decision_tree';
  target: string;
  features: string[];
  testSize: number;
  maxDepth: number;
  minSamplesSplit: number;
}

export interface RegressionParams {
  target: string;
  features: string[];
  testSize: number;
}

export interface ModelComparisonParams {
  algorithms: string[];
  target: string;
  features: string[];
  testSize: number;
}

export interface PCAParams {
    features: string[];
    numComponents: number;
}


export interface State {
  processedData: DataPoint[];
  originalData: DataPoint[];
  fileName: string;
  sheetNames: string[];
  isSheetModalOpen: boolean;
  isElbowModalOpen: boolean;
  elbowPlotData: { k: number, inertia: number, silhouette: number }[] | null;
  currentView: View;
  isLoading: boolean;
  loadingMessage: string;
  qualityReport: QualityReport;
  outlierReport: OutlierReport;
  healthReport?: any; // Consider creating a specific type for the health report
  clusterResults: ClusterResult | null;
  classificationResults: ClassificationResult | null;
  regressionResults: RegressionResult | null;
  modelComparisonResults: ModelComparisonResultItem[] | null;
  problemContext: string;
  datasetMetadata: string;
  clusteringParams: ClusteringParams;
  classificationParams: ClassificationParams;
  regressionParams: RegressionParams;
  modelComparisonParams: ModelComparisonParams;
  pcaParams: PCAParams;
  fileToProcess: File | null;
}

export type Action =
  | { type: 'SET_LOADING'; payload: { isLoading: boolean; message?: string } }
  | { type: 'SET_DATA_LOADED'; payload: { data: DataPoint[]; originalData: DataPoint[]; fileName: string; qualityReport: QualityReport; outlierReport: OutlierReport } }
  | { type: 'SET_DATA_HEALTH_REPORT'; payload: { healthReport: any } }
  | { type: 'SET_PROCESSED_DATA'; payload: { processedData: DataPoint[]; qualityReport: QualityReport; outlierReport: OutlierReport } }
  | { type: 'SET_VIEW'; payload: View }
  | { type: 'SET_SHEET_MODAL'; payload: { isOpen: boolean; sheetNames?: string[]; file?: File | null } }
  | { type: 'SET_ELBOW_MODAL_OPEN'; payload: boolean }
  | { type: 'SET_ELBOW_DATA'; payload: { k: number, inertia: number, silhouette: number }[] | null }
  | { type: 'SET_CLUSTER_RESULTS'; payload: ClusterResult | null }
  | { type: 'SET_CLASSIFICATION_RESULTS'; payload: ClassificationResult | null }
  | { type: 'SET_REGRESSION_RESULTS'; payload: RegressionResult | null }
  | { type: 'SET_MODEL_COMPARISON_RESULTS'; payload: ModelComparisonResultItem[] | null }
  | { type: 'SET_PROBLEM_CONTEXT'; payload: string }
  | { type: 'SET_DATASET_METADATA'; payload: string }
  | { type: 'UPDATE_CLUSTERING_PARAMS'; payload: Partial<ClusteringParams> }
  | { type: 'UPDATE_CLASSIFICATION_PARAMS'; payload: Partial<ClassificationParams> }
  | { type: 'UPDATE_REGRESSION_PARAMS'; payload: Partial<RegressionParams> }
  | { type: 'UPDATE_MODEL_COMPARISON_PARAMS'; payload: Partial<ModelComparisonParams> }
  | { type: 'UPDATE_PCA_PARAMS'; payload: Partial<PCAParams> }
  | { type: 'RESET_STATE'; payload?: { view?: View } };

// Fix: The AIStudio interface was causing type conflicts across modules.
// Inlining the type definition directly into the global scope resolves the issue.
declare global {
  // FIX: Moved AIStudio interface into declare global to make it a global type
  // and resolve "Subsequent property declarations must have the same type" error.
  interface AIStudio {
    hasSelectedApiKey: () => Promise<boolean>;
    openSelectKey: () => Promise<void>;
  }
  interface Window {
    // Use the AIStudio interface to ensure type consistency.
    aistudio?: AIStudio;
  }
}