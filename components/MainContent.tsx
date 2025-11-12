import React from 'react';
import { State, Action } from '../types';
import { DataPreview } from './DataPreview';
import { ExploratoryDataView } from './ExploratoryDataView';
import { DataPreparationView } from './DataPreparationView';
import { GuidedExercise } from './GuidedExercise';
import { exerciseNotebook } from '../data/exerciseData';
import { ClusteringView } from './ClusteringView';
import { ClassificationReport } from './ClassificationReport';
import { RegressionReport } from './RegressionReport';
import { ModelComparisonView } from './ModelComparisonView';
import { ProblemContext } from './ProblemContext';
import { DatasetMetadata } from './DatasetMetadata';
import { ApiKeyManager } from './ApiKeyManager';
import {
    TableIcon, 
    WandIcon, TargetIcon, TrendingUpIcon, CheckCircleIcon, InfoIcon, BroomIcon, UploadIcon, ProfileIcon
} from './icons';

interface MainContentProps {
  state: State;
  dispatch: React.Dispatch<Action>;
  runAnalysis: (type: 'clustering' | 'classification' | 'regression' | 'model-comparison' | 'pca', params: any) => void;
  addNotification: (message: string, type: 'success' | 'error' | 'info') => void;
  isKeyReady: boolean;
  setIsKeyReady: (isReady: boolean) => void;
}

const EmptyState: React.FC<{ icon: React.ReactNode, title: string, message: string }> = ({ icon, title, message }) => (
    <div className="flex flex-col items-center justify-center h-full text-center text-slate-500 p-8">
        <div className="mb-4">{icon}</div>
        <h3 className="text-xl font-semibold text-slate-300 mb-2">{title}</h3>
        <p className="max-w-md">{message}</p>
    </div>
);

const WelcomeView: React.FC<{ isKeyReady: boolean; setIsKeyReady: (isReady: boolean) => void }> = ({ isKeyReady, setIsKeyReady }) => (
    <div className="flex flex-col items-center justify-center h-full text-center p-4 sm:p-8 animate-fade-in">
        <div className="flex-grow flex flex-col items-center justify-center">
            <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4">¡Bienvenido a AnálisisData!</h1>
            <p className="text-lg text-slate-400 mb-10 max-w-2xl mx-auto">
            Tu herramienta interactiva para transformar datos en conocimiento. Sigue estos simples pasos para comenzar.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left mb-10 w-full max-w-4xl">
                <div className="bg-gray-800/50 p-6 rounded-lg border border-gray-700">
                    <div className="flex items-center mb-3">
                        <UploadIcon className="w-7 h-7 mr-4 text-cyan-400"/>
                        <h2 className="text-xl font-semibold text-white">1. Carga</h2>
                    </div>
                    <p className="text-sm text-slate-300">
                        Usa el botón en la barra lateral para subir tu conjunto de datos en formato CSV, JSON, Excel o DB.
                    </p>
                </div>
                <div className="bg-gray-800/50 p-6 rounded-lg border border-gray-700">
                    <div className="flex items-center mb-3">
                        <BroomIcon className="w-7 h-7 mr-4 text-cyan-400"/>
                        <h2 className="text-xl font-semibold text-white">2. Prepara</h2>
                    </div>
                    <p className="text-sm text-slate-300">
                        Explora y limpia tus datos. Rellena nulos, normaliza columnas y prepáralos para el análisis.
                    </p>
                </div>
                <div className="bg-gray-800/50 p-6 rounded-lg border border-gray-700">
                    <div className="flex items-center mb-3">
                        <WandIcon className="w-7 h-7 mr-4 text-cyan-400"/>
                        <h2 className="text-xl font-semibold text-white">3. Analiza</h2>
                    </div>
                    <p className="text-sm text-slate-300">
                        Aplica modelos de Machine Learning, visualiza los resultados y obtén análisis generados por IA.
                    </p>
                </div>
            </div>
            
            <div className="relative">
                <p className="text-slate-300 animate-pulse">← Comienza cargando un archivo</p>
            </div>
        </div>
        <div className="w-full max-w-2xl mt-10">
            <ApiKeyManager isKeyReady={isKeyReady} setIsKeyReady={setIsKeyReady} />
        </div>
    </div>
);

const DataHealthSummary: React.FC<{ 
    qualityReport: State['qualityReport'], 
    outlierReport: State['outlierReport'],
    dispatch: React.Dispatch<Action> 
}> = ({ qualityReport, outlierReport, dispatch }) => {
    
    type QualityMetric = { nulls: number; type: string };
    type OutlierMetric = { count: number };

    const totalNulls = Object.values(qualityReport).reduce((sum: number, col) => sum + (col as QualityMetric).nulls, 0);
    const totalOutliers = Object.values(outlierReport).reduce((sum: number, col) => sum + (col as OutlierMetric).count, 0);
    const numericCols = Object.values(qualityReport).filter(q => (q as QualityMetric).type === 'numeric').length;
    const categoricalCols = Object.values(qualityReport).filter(q => (q as QualityMetric).type === 'categorical').length;

    const isDataClean = totalNulls === 0 && totalOutliers === 0;

    const StatCard: React.FC<{ icon: React.ReactNode; value: string | number; label: string; }> = ({ icon, value, label }) => (
        <div className="bg-gray-900/50 p-4 rounded-lg flex items-center">
            {icon}
            <div className="ml-3">
                <p className="text-xl font-bold text-white">{value}</p>
                <p className="text-xs text-slate-400">{label}</p>
            </div>
        </div>
    );

    return (
        <div className="bg-gray-800/50 backdrop-blur-sm p-4 rounded-lg border border-gray-700 mb-6">
            <h3 className="text-lg font-semibold mb-4 text-white">Diagnóstico Rápido de Datos</h3>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                <StatCard 
                    icon={totalNulls === 0 ? <CheckCircleIcon className="w-8 h-8 text-emerald-500" /> : <InfoIcon className="w-8 h-8 text-amber-400" />}
                    value={totalNulls}
                    label="Valores Nulos"
                />
                <StatCard 
                    icon={totalOutliers === 0 ? <CheckCircleIcon className="w-8 h-8 text-emerald-500" /> : <InfoIcon className="w-8 h-8 text-amber-400" />}
                    value={totalOutliers}
                    label="Outliers Potenciales"
                />
                 <StatCard 
                    icon={<div className="w-8 h-8 flex items-center justify-center text-sky-400 font-mono text-lg bg-sky-500/10 rounded-full">#</div>}
                    value={numericCols}
                    label="Columnas Numéricas"
                />
                 <StatCard 
                    icon={<div className="w-8 h-8 flex items-center justify-center text-fuchsia-400 font-mono text-lg bg-fuchsia-500/10 rounded-full">A</div>}
                    value={categoricalCols}
                    label="Columnas Categóricas"
                />
            </div>
            <div className="text-center p-3 bg-gray-900/50 rounded-md">
                {isDataClean ? (
                     <div className="flex items-center justify-center">
                        <p className="text-sm text-emerald-300 mr-4">¡Tus datos están listos para el análisis!</p>
                        <button 
                            onClick={() => dispatch({ type: 'SET_VIEW', payload: 'clustering'})}
                            className="bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-2 px-4 rounded transition-colors text-sm flex items-center"
                        >
                           <TargetIcon className="w-4 h-4 mr-2"/> Ir a Modelado
                        </button>
                     </div>
                ) : (
                    <div className="flex items-center justify-center">
                        <p className="text-sm text-amber-300 mr-4">Se recomienda limpiar los datos antes de modelar.</p>
                         <button 
                            onClick={() => dispatch({ type: 'SET_VIEW', payload: 'data-preparation'})}
                            className="bg-amber-600 hover:bg-amber-700 text-white font-bold py-2 px-4 rounded transition-colors text-sm flex items-center"
                        >
                           <BroomIcon className="w-4 h-4 mr-2"/> Ir a Preparación de Datos
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export const MainContent: React.FC<MainContentProps> = ({ state, dispatch, runAnalysis, addNotification, isKeyReady, setIsKeyReady }) => {
    const { currentView, originalData, processedData } = state;

    if (originalData.length === 0 && currentView !== 'exercise') {
        return <WelcomeView isKeyReady={isKeyReady} setIsKeyReady={setIsKeyReady} />;
    }
    
    switch (currentView) {
        case 'data-preview':
            return (
                <div className="p-4 sm:p-6">
                    <h2 className="text-2xl font-bold mb-4">Vista Previa de Datos</h2>
                    <DataHealthSummary 
                        qualityReport={state.qualityReport} 
                        outlierReport={state.outlierReport} 
                        dispatch={dispatch} 
                    />
                    <ProblemContext problemContext={state.problemContext} dispatch={dispatch} />
                    <DatasetMetadata datasetMetadata={state.datasetMetadata} dispatch={dispatch} />
                    <DataPreview data={processedData} />
                </div>
            );
        case 'exploratory-data':
            return <ExploratoryDataView state={state} />;
        case 'data-preparation':
            return <DataPreparationView state={state} dispatch={dispatch} runAnalysis={runAnalysis} addNotification={addNotification} />;
        case 'clustering':
            return <ClusteringView state={state} setIsKeyReady={setIsKeyReady} />;
        case 'classification':
             if (!state.classificationResults) {
                return <EmptyState 
                    icon={<WandIcon className="w-16 h-16 text-slate-700"/>}
                    title="Análisis de Clasificación"
                    message="Selecciona una variable objetivo y las características en la barra lateral, luego ejecuta el análisis para clasificar tus datos."
                />;
            }
            return <ClassificationReport 
                        result={state.classificationResults} 
                        problemContext={state.problemContext}
                        datasetMetadata={state.datasetMetadata}
                        setIsKeyReady={setIsKeyReady} 
                    />;
        case 'regression':
             if (!state.regressionResults) {
                return <EmptyState 
                    icon={<TrendingUpIcon className="w-16 h-16 text-slate-700"/>}
                    title="Análisis de Regresión"
                    message="Selecciona las variables dependiente e independiente en la barra lateral y ejecuta el análisis para predecir valores continuos."
                />;
            }
            return <RegressionReport 
                        result={state.regressionResults} 
                        problemContext={state.problemContext}
                        datasetMetadata={state.datasetMetadata}
                        setIsKeyReady={setIsKeyReady} 
                    />;
        case 'model-comparison':
            if (!state.modelComparisonResults) {
                return <EmptyState 
                    icon={<ProfileIcon className="w-16 h-16 text-slate-700"/>}
                    title="Comparación de Modelos"
                    message="Selecciona al menos dos algoritmos en la barra lateral y ejecuta la comparación para ver sus rendimientos lado a lado."
                />;
            }
            return <ModelComparisonView 
                        results={state.modelComparisonResults} 
                        problemContext={state.problemContext}
                        datasetMetadata={state.datasetMetadata}
                        setIsKeyReady={setIsKeyReady} 
                    />;
        case 'exercise':
            return <div className="p-4 sm:p-6"><GuidedExercise notebook={exerciseNotebook} /></div>;
        default:
            return <div className="p-6">Vista no encontrada</div>;
    }
};