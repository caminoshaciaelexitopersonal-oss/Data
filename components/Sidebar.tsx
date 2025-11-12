import React, { useRef, useState } from 'react';
import { State, Action, QualityReport } from '../types';
import {
  UploadIcon,
  TableIcon,
  ChartIcon,
  BroomIcon,
  TargetIcon,
  WandIcon,
  TrendingUpIcon,
  ProfileIcon,
  BookOpenIcon,
  CogIcon,
  RefreshIcon,
  LineChartIcon
} from './icons';

interface SidebarProps {
  state: State;
  dispatch: React.Dispatch<Action>;
  onFileLoad: (file: File) => void;
  runAnalysis: (type: 'clustering' | 'classification' | 'regression' | 'model-comparison' | 'elbow', params: any) => void;
}

const NavItem: React.FC<{ icon: React.ReactNode; label: string; isActive: boolean; onClick: () => void; disabled?: boolean }> = ({ icon, label, isActive, onClick, disabled }) => (
    <button
        onClick={onClick}
        disabled={disabled}
        className={`w-full flex items-center px-3 py-2.5 text-sm font-medium rounded-md transition-colors ${
            isActive
                ? 'bg-cyan-500/20 text-cyan-300'
                : 'text-slate-400 hover:bg-gray-700/50 hover:text-slate-200'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
        {icon}
        <span className="ml-3">{label}</span>
    </button>
);

const getNumericFeatures = (qualityReport: QualityReport) => Object.keys(qualityReport).filter(key => qualityReport[key].type === 'numeric');
const getAllFeatures = (qualityReport: QualityReport) => Object.keys(qualityReport);

const CustomMultiSelect: React.FC<{
    options: string[];
    selected: string[];
    onChange: (selected: string[]) => void;
}> = ({ options, selected, onChange }) => {
    const toggleOption = (option: string) => {
        const newSelected = selected.includes(option)
            ? selected.filter(item => item !== option)
            : [...selected, option];
        onChange(newSelected);
    };

    const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.checked) {
            onChange(options);
        } else {
            onChange([]);
        }
    };

    const allSelected = options.length > 0 && selected.length === options.length;

    const formatLabel = (option: string) => {
        return option.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    }

    return (
        <div className="bg-gray-900/50 border border-gray-700 rounded mt-1 max-h-48 overflow-y-auto p-2 space-y-1">
            <label className="w-full flex items-center text-left text-sm p-2 rounded cursor-pointer transition-colors hover:bg-gray-700/50 text-slate-300 font-semibold border-b border-gray-700 mb-1">
                <input
                    type="checkbox"
                    checked={allSelected}
                    onChange={handleSelectAll}
                    className="w-4 h-4 rounded bg-gray-700 border-gray-600 text-cyan-500 focus:ring-cyan-500 focus:ring-offset-gray-800 focus:ring-2"
                />
                <span className="ml-2.5 truncate select-none">Seleccionar Todo</span>
            </label>
            {options.map(option => (
                <label
                    key={option}
                    className={`w-full flex items-center text-left text-sm p-2 rounded cursor-pointer transition-colors ${
                        selected.includes(option)
                            ? 'bg-cyan-500/20 text-white font-medium'
                            : 'hover:bg-gray-700/50 text-slate-300'
                    }`}
                >
                    <input
                        type="checkbox"
                        checked={selected.includes(option)}
                        onChange={() => toggleOption(option)}
                        className="w-4 h-4 rounded bg-gray-700 border-gray-600 text-cyan-500 focus:ring-cyan-500 focus:ring-offset-gray-800 focus:ring-2"
                    />
                    <span className="ml-2.5 truncate select-none">{formatLabel(option)}</span>
                </label>
            ))}
        </div>
    );
};


export const Sidebar: React.FC<SidebarProps> = ({ state, dispatch, onFileLoad, runAnalysis }) => {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const { currentView, originalData, qualityReport, clusteringParams, classificationParams, regressionParams, modelComparisonParams } = state;
    const isDataLoaded = originalData.length > 0;
    const numericFeatures = getNumericFeatures(qualityReport);
    const allFeatures = getAllFeatures(qualityReport);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            onFileLoad(file);
        }
        if(fileInputRef.current) fileInputRef.current.value = "";
    };

    const handleClusteringParamChange = (param: string, value: any) => {
        dispatch({ type: 'UPDATE_CLUSTERING_PARAMS', payload: { [param]: value } });
    };
    
    const handleClassificationParamChange = (param: string, value: any) => {
        dispatch({ type: 'UPDATE_CLASSIFICATION_PARAMS', payload: { [param]: value } });
    };

    const handleRegressionParamChange = (param: string, value: any) => {
        dispatch({ type: 'UPDATE_REGRESSION_PARAMS', payload: { [param]: value } });
    };
    
    const handleModelComparisonParamChange = (param: string, value: any) => {
        dispatch({ type: 'UPDATE_MODEL_COMPARISON_PARAMS', payload: { [param]: value } });
    };

    const renderClusteringControls = () => {
        let isExecuteDisabled = true;
        switch (clusteringParams.algorithm) {
            case 'kmeans':
            case 'dbscan':
                isExecuteDisabled = clusteringParams.features.length < 2;
                break;
            case 'hierarchical':
                 isExecuteDisabled = clusteringParams.features.length < 1;
                 break;
        }

        return (
        <>
            <h3 className="text-sm font-semibold text-slate-300 px-3 mt-4 mb-2 flex items-center"><CogIcon className="w-4 h-4 mr-2"/>Parámetros de Clustering</h3>
            <div className="px-3 space-y-3">
                <div>
                    <label className="text-xs text-slate-400">Algoritmo</label>
                    <select value={clusteringParams.algorithm} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleClusteringParamChange('algorithm', e.currentTarget.value as 'kmeans' | 'dbscan' | 'hierarchical')} className="w-full bg-gray-700 border border-gray-600 rounded p-1.5 text-sm mt-1">
                        <option value="kmeans">K-Means</option>
                        <option value="dbscan">DBSCAN</option>
                        <option value="hierarchical">Jerárquico</option>
                    </select>
                </div>
                <div>
                    <label className="text-xs text-slate-400">Características</label>
                    <CustomMultiSelect
                        options={numericFeatures}
                        selected={clusteringParams.features}
                        onChange={(selected) => handleClusteringParamChange('features', selected)}
                    />
                </div>
                 {clusteringParams.algorithm === 'kmeans' && (
                    <>
                         <div>
                            <label className="text-xs text-slate-400">Número de Clusters (K): {clusteringParams.k}</label>
                            <input type="range" min="2" max="15" value={clusteringParams.k} onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleClusteringParamChange('k', parseInt(e.currentTarget.value, 10))} className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer"/>
                        </div>
                        <button onClick={() => runAnalysis('elbow', { maxK: clusteringParams.maxK, features: clusteringParams.features })} disabled={clusteringParams.features.length < 2} className="w-full text-xs bg-gray-600 hover:bg-gray-500 text-white font-semibold py-1.5 px-2 rounded transition-colors disabled:opacity-50 flex items-center justify-center">
                            <LineChartIcon className="w-4 h-4 mr-1.5"/> Analizar Codo / Silueta
                        </button>
                    </>
                )}
                 {clusteringParams.algorithm === 'dbscan' && (
                    <>
                         <div>
                            <label className="text-xs text-slate-400">Epsilon (eps): {clusteringParams.eps}</label>
                            <input type="range" min="0.1" max="2.0" step="0.1" value={clusteringParams.eps} onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleClusteringParamChange('eps', parseFloat(e.currentTarget.value))} className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer"/>
                        </div>
                        <div>
                            <label className="text-xs text-slate-400">Min Puntos: {clusteringParams.minPts}</label>
                            <input type="range" min="2" max="20" value={clusteringParams.minPts} onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleClusteringParamChange('minPts', parseInt(e.currentTarget.value, 10))} className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer"/>
                        </div>
                    </>
                 )}
                 {clusteringParams.algorithm === 'hierarchical' && (
                     <div>
                        <label className="text-xs text-slate-400">Número de Clusters: {clusteringParams.numClusters}</label>
                        <input type="range" min="2" max="15" value={clusteringParams.numClusters} onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleClusteringParamChange('numClusters', parseInt(e.currentTarget.value, 10))} className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer"/>
                    </div>
                 )}
                <button onClick={() => runAnalysis('clustering', clusteringParams)} disabled={isExecuteDisabled} className="w-full bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-2 px-4 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                    Ejecutar
                </button>
            </div>
        </>
        )
    };

     const renderClassificationControls = () => (
        <>
            <h3 className="text-sm font-semibold text-slate-300 px-3 mt-4 mb-2 flex items-center"><CogIcon className="w-4 h-4 mr-2"/>Parámetros de Clasificación</h3>
            <div className="px-3 space-y-3">
                 <div>
                    <label className="text-xs text-slate-400">Algoritmo</label>
                    <select value={classificationParams.algorithm} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleClassificationParamChange('algorithm', e.currentTarget.value as 'naive_bayes' | 'logistic_regression' | 'decision_tree')} className="w-full bg-gray-700 border border-gray-600 rounded p-1.5 text-sm mt-1">
                        <option value="naive_bayes">Naive Bayes</option>
                        <option value="logistic_regression">Regresión Logística</option>
                        <option value="decision_tree">Árbol de Decisión</option>
                    </select>
                </div>
                <div>
                    <label className="text-xs text-slate-400">Variable Objetivo (Target)</label>
                    <select value={classificationParams.target} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleClassificationParamChange('target', e.currentTarget.value)} className="w-full bg-gray-700 border border-gray-600 rounded p-1.5 text-sm mt-1">
                        <option value="">Seleccionar...</option>
                        {allFeatures.map(f => <option key={f} value={f}>{f}</option>)}
                    </select>
                </div>
                <div>
                    <label className="text-xs text-slate-400">Características</label>
                     <CustomMultiSelect
                        options={allFeatures.filter(f => f !== classificationParams.target)}
                        selected={classificationParams.features}
                        onChange={(selected) => handleClassificationParamChange('features', selected)}
                    />
                </div>

                {classificationParams.algorithm === 'decision_tree' && (
                    <>
                        <div>
                            <label className="text-xs text-slate-400">Profundidad Máxima: {classificationParams.maxDepth}</label>
                            <input type="range" min="1" max="15" value={classificationParams.maxDepth} onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleClassificationParamChange('maxDepth', parseInt(e.currentTarget.value, 10))} className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer"/>
                        </div>
                         <div>
                            <label className="text-xs text-slate-400">Muestras Mínimas por División: {classificationParams.minSamplesSplit}</label>
                            <input type="range" min="2" max="20" value={classificationParams.minSamplesSplit} onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleClassificationParamChange('minSamplesSplit', parseInt(e.currentTarget.value, 10))} className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer"/>
                        </div>
                    </>
                )}

                <button onClick={() => runAnalysis('classification', classificationParams)} disabled={!classificationParams.target || classificationParams.features.length === 0} className="w-full bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-2 px-4 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                    Ejecutar
                </button>
            </div>
        </>
    );

    const renderRegressionControls = () => (
        <>
            <h3 className="text-sm font-semibold text-slate-300 px-3 mt-4 mb-2 flex items-center"><CogIcon className="w-4 h-4 mr-2"/>Parámetros de Regresión</h3>
            <div className="px-3 space-y-3">
                <div>
                    <label className="text-xs text-slate-400">Variable Objetivo (Dependiente)</label>
                    <select value={regressionParams.target} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleRegressionParamChange('target', e.currentTarget.value)} className="w-full bg-gray-700 border border-gray-600 rounded p-1.5 text-sm mt-1">
                        <option value="">Seleccionar...</option>
                        {numericFeatures.map(f => <option key={f} value={f}>{f}</option>)}
                    </select>
                </div>
                 <div>
                    <label className="text-xs text-slate-400">Variable Predictora (Independiente)</label>
                    <select value={regressionParams.features[0] || ''} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleRegressionParamChange('features', [e.currentTarget.value])} className="w-full bg-gray-700 border border-gray-600 rounded p-1.5 text-sm mt-1">
                        <option value="">Seleccionar...</option>
                        {numericFeatures.filter(f => f !== regressionParams.target).map(f => <option key={f} value={f}>{f}</option>)}
                    </select>
                </div>
                <button onClick={() => runAnalysis('regression', regressionParams)} disabled={!regressionParams.target || regressionParams.features.length === 0} className="w-full bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-2 px-4 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                    Ejecutar
                </button>
            </div>
        </>
    )

    const renderModelComparisonControls = () => (
        <>
            <h3 className="text-sm font-semibold text-slate-300 px-3 mt-4 mb-2 flex items-center"><CogIcon className="w-4 h-4 mr-2"/>Parámetros de Comparación</h3>
            <div className="px-3 space-y-3">
                 <div>
                    <label className="text-xs text-slate-400">Algoritmos a Comparar</label>
                     <CustomMultiSelect
                        options={['naive_bayes', 'logistic_regression', 'decision_tree']}
                        selected={modelComparisonParams.algorithms}
                        onChange={(selected) => handleModelComparisonParamChange('algorithms', selected)}
                    />
                </div>
                <div>
                    <label className="text-xs text-slate-400">Variable Objetivo (Target)</label>
                    <select value={modelComparisonParams.target} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleModelComparisonParamChange('target', e.currentTarget.value)} className="w-full bg-gray-700 border border-gray-600 rounded p-1.5 text-sm mt-1">
                        <option value="">Seleccionar...</option>
                        {allFeatures.map(f => <option key={f} value={f}>{f}</option>)}
                    </select>
                </div>
                <div>
                    <label className="text-xs text-slate-400">Características</label>
                    <CustomMultiSelect
                        options={allFeatures.filter(f => f !== modelComparisonParams.target)}
                        selected={modelComparisonParams.features}
                        onChange={(selected) => handleModelComparisonParamChange('features', selected)}
                    />
                </div>
                <button onClick={() => runAnalysis('model-comparison', modelComparisonParams)} disabled={!modelComparisonParams.target || modelComparisonParams.features.length === 0 || modelComparisonParams.algorithms.length < 2} className="w-full bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-2 px-4 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                    Ejecutar Comparación
                </button>
            </div>
        </>
    );

    return (
        <aside className="w-64 bg-gray-800 p-4 flex flex-col border-r border-gray-700/50">
            <div className="flex items-center mb-6">
                <ProfileIcon className="w-8 h-8 text-cyan-400"/>
                <h1 className="ml-3 text-xl font-bold text-white">AnálisisData</h1>
            </div>

            <div className="space-y-2">
                <input type="file" ref={fileInputRef} onChange={handleFileChange} accept=".csv, .json, .xlsx, .xls, .txt" className="hidden" />
                <button onClick={() => fileInputRef.current?.click()} className="w-full flex items-center justify-center bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-2 px-4 rounded transition-colors">
                    <UploadIcon className="w-5 h-5 mr-2" />
                    Cargar Datos
                </button>
                 {isDataLoaded && (
                    <button onClick={() => dispatch({ type: 'RESET_STATE', payload: { view: 'data-preview' } })} className="w-full flex items-center justify-center bg-rose-600/50 hover:bg-rose-600/80 text-white font-bold py-2 px-4 rounded transition-colors">
                        <RefreshIcon className="w-5 h-5 mr-2" />
                        Reiniciar
                    </button>
                 )}
            </div>
            
            <nav className="mt-6 flex-grow overflow-y-auto pr-2 space-y-1.5">
                <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider px-3 mb-2">Análisis</h3>
                <NavItem icon={<TableIcon className="w-5 h-5"/>} label="Vista de Datos" isActive={currentView === 'data-preview'} onClick={() => dispatch({type: 'SET_VIEW', payload: 'data-preview'})} disabled={!isDataLoaded} />
                <NavItem icon={<ChartIcon className="w-5 h-5"/>} label="Análisis Exploratorio" isActive={currentView === 'exploratory-data'} onClick={() => dispatch({type: 'SET_VIEW', payload: 'exploratory-data'})} disabled={!isDataLoaded} />
                <NavItem icon={<BroomIcon className="w-5 h-5"/>} label="Preparación de Datos" isActive={currentView === 'data-preparation'} onClick={() => dispatch({type: 'SET_VIEW', payload: 'data-preparation'})} disabled={!isDataLoaded} />
                
                <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider px-3 pt-4 mb-2">Modelos</h3>
                <NavItem icon={<TargetIcon className="w-5 h-5"/>} label="Clustering" isActive={currentView === 'clustering'} onClick={() => dispatch({type: 'SET_VIEW', payload: 'clustering'})} disabled={!isDataLoaded} />
                <NavItem icon={<WandIcon className="w-5 h-5"/>} label="Clasificación" isActive={currentView === 'classification'} onClick={() => dispatch({type: 'SET_VIEW', payload: 'classification'})} disabled={!isDataLoaded} />
                <NavItem icon={<TrendingUpIcon className="w-5 h-5"/>} label="Regresión" isActive={currentView === 'regression'} onClick={() => dispatch({type: 'SET_VIEW', payload: 'regression'})} disabled={!isDataLoaded} />
                 <NavItem icon={<ProfileIcon className="w-5 h-5"/>} label="Comparación" isActive={currentView === 'model-comparison'} onClick={() => dispatch({type: 'SET_VIEW', payload: 'model-comparison'})} disabled={!isDataLoaded} />

                {isDataLoaded && currentView === 'clustering' && renderClusteringControls()}
                {isDataLoaded && currentView === 'classification' && renderClassificationControls()}
                {isDataLoaded && currentView === 'regression' && renderRegressionControls()}
                {isDataLoaded && currentView === 'model-comparison' && renderModelComparisonControls()}
            </nav>

            <div className="mt-auto pt-4 border-t border-gray-700">
                 <NavItem icon={<BookOpenIcon className="w-5 h-5"/>} label="Ejercicio Guiado" isActive={currentView === 'exercise'} onClick={() => dispatch({type: 'SET_VIEW', payload: 'exercise'})} />
            </div>
        </aside>
    );
};