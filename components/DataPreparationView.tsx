// components/DataPreparationView.tsx

import React, { useState } from 'react';
import { State, Transformation, OutlierReport, Action, QualityReport } from '../types';
import { BroomIcon, DownloadIcon, CogIcon, SparklesIcon, CheckCircleIcon, TargetIcon, WandIcon, TrendingUpIcon } from './icons';
import { applyTransformations, exportDataToCsv } from '../services/dataService';
import { analyzeDataQuality, detectOutliers } from '../services/dataService';

interface DataPreparationViewProps {
    state: State;
    dispatch: React.Dispatch<Action>;
    runAnalysis: (type: 'pca', params: any) => void;
    addNotification: (message: string, type: 'success' | 'error' | 'info') => void;
}

const getNumericFeatures = (qualityReport: QualityReport) => Object.keys(qualityReport).filter(key => qualityReport[key].type === 'numeric');

const PCACard: React.FC<{
    state: State;
    dispatch: React.Dispatch<Action>;
    runAnalysis: (type: 'pca', params: any) => void;
}> = ({ state, dispatch, runAnalysis }) => {
    const { pcaParams, qualityReport } = state;
    const numericFeatures = getNumericFeatures(qualityReport);

    const handleParamChange = (param: string, value: any) => {
        dispatch({ type: 'UPDATE_PCA_PARAMS', payload: { [param]: value } });
    };

    return (
        <div className="bg-gray-900/50 p-4 rounded-lg border border-gray-700">
            <h4 className="font-bold text-white mb-2 flex items-center"><CogIcon className="w-4 h-4 mr-2"/>Análisis de Componentes Principales (PCA)</h4>
            <p className="text-xs text-slate-400 mb-3">Reduce la dimensionalidad de tus datos transformando variables correlacionadas en un conjunto más pequeño de componentes no correlacionados.</p>
            <div className="space-y-3">
                 <div>
                    <label className="text-xs text-slate-400">Características a incluir</label>
                    <select multiple value={pcaParams.features} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => handleParamChange('features', Array.from(e.currentTarget.selectedOptions, (option: HTMLOptionElement) => option.value))} className="w-full bg-gray-700 border border-gray-600 rounded p-1.5 text-sm mt-1 h-24">
                        {numericFeatures.map(f => <option key={f} value={f}>{f}</option>)}
                    </select>
                </div>
                 <div>
                    <label className="text-xs text-slate-400">Número de Componentes: {pcaParams.numComponents}</label>
                    <input type="range" min="1" max={Math.max(1, pcaParams.features.length)} value={pcaParams.numComponents} onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleParamChange('numComponents', parseInt(e.currentTarget.value, 10))} className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer"/>
                </div>
                <button 
                    onClick={() => runAnalysis('pca', pcaParams)} 
                    disabled={pcaParams.features.length < 2 || pcaParams.numComponents < 1 || pcaParams.numComponents > pcaParams.features.length}
                    className="w-full bg-violet-600 hover:bg-violet-700 text-white font-bold py-2 px-4 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    Ejecutar PCA
                </button>
            </div>
        </div>
    );
};

const AutomaticPreparationCard: React.FC<{ onApply: () => void; }> = ({ onApply }) => (
    <div className="bg-gray-900/50 p-4 rounded-lg border border-violet-500/50 mb-6">
        <h4 className="font-bold text-white mb-2 flex items-center"><SparklesIcon className="w-5 h-5 mr-2 text-violet-400"/>Preparación Automática (Recomendado)</h4>
        <p className="text-sm text-slate-400 mb-4">
            Aplica un conjunto de transformaciones comunes con un solo clic para limpiar tus datos rápidamente. Esto incluye:
        </p>
        <ul className="list-disc list-inside text-xs text-slate-400 space-y-1 mb-4 pl-2">
            <li>Rellenar valores nulos (mediana para numéricos, moda para categóricos).</li>
            <li>Acotar (capping) de valores atípicos en columnas numéricas.</li>
            <li>Normalización Z-score para todas las columnas numéricas.</li>
        </ul>
        <button
            onClick={onApply}
            className="w-full bg-violet-600 hover:bg-violet-700 text-white font-bold py-2 px-4 rounded transition-colors"
        >
            Ejecutar Preparación Automática
        </button>
    </div>
);


const ColumnCard: React.FC<{
    column: string;
    quality: { nulls: number; type: string };
    outlierInfo: OutlierReport[string] | undefined;
    addTransformation: (t: Transformation) => void;
}> = ({ column, quality, outlierInfo, addTransformation }) => {
    
    const isNumeric = quality.type === 'numeric';

    return (
        <div className="bg-gray-900/50 p-4 rounded-lg border border-gray-700 space-y-3 flex flex-col">
            <div>
                <h4 className="font-bold text-white truncate">{column}</h4>
                <div className="flex items-center flex-wrap gap-x-3 text-xs text-slate-400">
                    <span className={`px-2 py-0.5 rounded ${isNumeric ? 'bg-sky-500/20 text-sky-300' : 'bg-fuchsia-500/20 text-fuchsia-300'}`}>{quality.type}</span>
                    <span>{quality.nulls} nulos</span>
                    {isNumeric && outlierInfo && <span className="text-amber-400">{outlierInfo.count} outliers</span>}
                </div>
            </div>

            <div className="space-y-2">
                <label className="text-sm font-medium text-slate-400 block">Manejar Nulos</label>
                <select 
                    onChange={(e: React.ChangeEvent<HTMLSelectElement>) => addTransformation({ type: 'FILL_NULLS', column, strategy: e.currentTarget.value as 'mean' | 'median' | 'mode' })}
                    className="w-full bg-gray-700 border border-gray-600 rounded p-1.5 text-sm"
                    defaultValue=""
                >
                    <option value="" disabled>Seleccionar estrategia...</option>
                    {isNumeric ? <>
                        <option value="mean">Rellenar con la Media</option>
                        <option value="median">Rellenar con la Mediana</option>
                        <option value="mode">Rellenar con la Moda</option>
                    </> : <option value="mode">Rellenar con la Moda</option>}
                </select>
            </div>
            
            {isNumeric && (
                 <>
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-400 block">Normalizar</label>
                        <select 
                            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => addTransformation({ type: 'NORMALIZE', column, method: e.currentTarget.value as 'z-score' | 'min-max' })}
                            className="w-full bg-gray-700 border border-gray-600 rounded p-1.5 text-sm"
                            defaultValue=""
                        >
                            <option value="" disabled>Seleccionar método...</option>
                            <option value="z-score">Z-score (Estandarización)</option>
                            <option value="min-max">Min-Max</option>
                        </select>
                    </div>
                    {outlierInfo && (
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-400 block">Manejar Outliers</label>
                             <div className="flex flex-col space-y-1 text-sm">
                                 <button onClick={() => addTransformation({ type: 'CAP_OUTLIERS', column })} className="w-full text-left hover:bg-gray-700 p-2 rounded">Acotar (Cap) Valores</button>
                                 <button onClick={() => addTransformation({ type: 'REMOVE_OUTLIERS', column })} className="w-full text-left hover:bg-gray-700 p-2 rounded">Eliminar Filas</button>
                             </div>
                        </div>
                    )}
                </>
            )}
            
            {!isNumeric && (
                 <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-400 block">Codificar</label>
                     <button onClick={() => addTransformation({ type: 'ONE_HOT_ENCODE', column })} className="w-full text-left text-sm hover:bg-gray-700 p-2 rounded">
                        One-Hot Encoding
                    </button>
                </div>
            )}

            <div className="mt-auto pt-3 border-t border-gray-700/50">
                <button
                    onClick={() => addTransformation({ type: 'DROP_COLUMN', column })}
                    className="w-full text-left text-sm text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 p-2 rounded"
                >
                    Eliminar Columna
                </button>
            </div>
        </div>
    );
};

const NextStepView: React.FC<{ dispatch: React.Dispatch<Action> }> = ({ dispatch }) => (
    <div className="bg-emerald-900/50 p-6 rounded-lg border border-emerald-500/50 text-center animate-fade-in flex flex-col items-center justify-center h-full">
        <CheckCircleIcon className="w-16 h-16 text-emerald-400 mb-4"/>
        <h2 className="text-2xl font-bold text-white mb-2">¡Datos Limpios y Listos!</h2>
        <p className="text-slate-300 mb-6 max-w-lg">
            La preparación de datos ha finalizado. Tus datos están limpios, normalizados y listos para ser analizados. ¿Qué quieres hacer ahora?
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-3xl">
            <button 
                onClick={() => dispatch({ type: 'SET_VIEW', payload: 'clustering'})}
                className="p-4 bg-cyan-600 hover:bg-cyan-700 text-white font-bold rounded-lg transition-colors flex flex-col items-center justify-center space-y-2"
            >
                <TargetIcon className="w-8 h-8"/>
                <span>Clustering</span>
            </button>
            <button 
                onClick={() => dispatch({ type: 'SET_VIEW', payload: 'classification'})}
                className="p-4 bg-cyan-600 hover:bg-cyan-700 text-white font-bold rounded-lg transition-colors flex flex-col items-center justify-center space-y-2"
            >
                <WandIcon className="w-8 h-8"/>
                <span>Clasificación</span>
            </button>
            <button 
                onClick={() => dispatch({ type: 'SET_VIEW', payload: 'regression'})}
                className="p-4 bg-cyan-600 hover:bg-cyan-700 text-white font-bold rounded-lg transition-colors flex flex-col items-center justify-center space-y-2"
            >
                <TrendingUpIcon className="w-8 h-8"/>
                <span>Regresión</span>
            </button>
        </div>
    </div>
);


export const DataPreparationView: React.FC<DataPreparationViewProps> = ({ state, dispatch, runAnalysis, addNotification }) => {
    const { processedData, fileName, qualityReport, outlierReport } = state;
    const [transformations, setTransformations] = useState<Transformation[]>([]);

    // FIX: Explicitly type the accumulator in reduce to avoid TS errors.
    const totalNulls = Object.values(qualityReport).reduce((sum: number, col) => sum + (col as { nulls: number }).nulls, 0);
    // FIX: Explicitly type the accumulator in reduce to avoid TS errors.
    const totalOutliers = Object.values(outlierReport).reduce((sum: number, col) => sum + ((col as { count: number })?.count || 0), 0);
    const isDataClean = totalNulls === 0 && totalOutliers === 0;


    const addTransformation = (t: Transformation) => {
        setTransformations(prev => {
            const existingIndex = prev.findIndex(item => item.column === t.column && item.type === t.type);
            if (existingIndex > -1) {
                const updated = [...prev];
                updated[existingIndex] = t;
                return updated;
            }
            return [...prev, t];
        });
    };
    
    const handleApply = () => {
        try {
            const transformedData = applyTransformations(processedData, transformations, outlierReport);
            const newQualityReport = analyzeDataQuality(transformedData);
            const newOutlierReport = detectOutliers(transformedData, newQualityReport);
            dispatch({ type: 'SET_PROCESSED_DATA', payload: { processedData: transformedData, qualityReport: newQualityReport, outlierReport: newOutlierReport } });
            setTransformations([]);
            addNotification('Transformaciones manuales aplicadas.', 'success');
        } catch(error) {
            console.error("Error applying transformations:", error);
            const message = error instanceof Error ? error.message : 'Error desconocido';
            addNotification('Error al aplicar transformaciones: ' + message, 'error');
        }
    }

    const handleAutoApply = () => {
        try {
            const { processedData, qualityReport, outlierReport } = state;
            const autoTransformations: Transformation[] = [];

            for (const column of Object.keys(qualityReport)) {
                const quality = qualityReport[column];
                const outlierInfo = outlierReport[column];

                if (quality.type === 'numeric') {
                    if (quality.nulls > 0) autoTransformations.push({ type: 'FILL_NULLS', column, strategy: 'median' });
                    if (outlierInfo) autoTransformations.push({ type: 'CAP_OUTLIERS', column });
                    autoTransformations.push({ type: 'NORMALIZE', column, method: 'z-score' });
                } else {
                    if (quality.nulls > 0) autoTransformations.push({ type: 'FILL_NULLS', column, strategy: 'mode' });
                }
            }
            
            const transformedData = applyTransformations(processedData, autoTransformations, outlierReport);
            const newQualityReport = analyzeDataQuality(transformedData);
            const newOutlierReport = detectOutliers(transformedData, newQualityReport);
            dispatch({ type: 'SET_PROCESSED_DATA', payload: { processedData: transformedData, qualityReport: newQualityReport, outlierReport: newOutlierReport } });
            setTransformations([]);
            addNotification('Preparación automática completada. Los datos están limpios y listos para modelar.', 'success');
        } catch (error) {
            console.error("Error applying automatic transformations:", error);
            const message = error instanceof Error ? error.message : 'Error desconocido';
            addNotification('Error en la preparación automática: ' + message, 'error');
        }
    };
    
    const getActionDescription = (t: Transformation) => {
        switch(t.type) {
            case 'DROP_COLUMN': return 'Eliminar columna "' + t.column + '"';
            case 'FILL_NULLS': return 'Rellenar nulos en "' + t.column + '" con ' + t.strategy;
            case 'NORMALIZE': return 'Normalizar "' + t.column + '" con ' + t.method;
            case 'REMOVE_OUTLIERS': return 'Eliminar outliers en "' + t.column + '"';
            case 'CAP_OUTLIERS': return 'Acotar outliers en "' + t.column + '"';
            case 'ONE_HOT_ENCODE': return 'Codificar (One-Hot) "' + t.column + '"';
            default: return 'Acción desconocida';
        }
    }

    return (
        <div className="p-4 sm:p-6 text-slate-200 animate-fade-in h-full flex flex-col">
            <div>
                <h2 className="text-2xl font-bold mb-1 flex items-center"><BroomIcon className="w-6 h-6 mr-3 text-cyan-400"/>Preparación de Datos</h2>
                <p className="text-slate-400 mb-6">Limpia, normaliza y transforma tus datos antes de aplicar los modelos.</p>
            </div>
            
            <div className="flex-grow grid grid-cols-1 lg:grid-cols-4 gap-6">
                {isDataClean ? (
                    <div className="lg:col-span-4">
                        <NextStepView dispatch={dispatch} />
                    </div>
                ) : (
                    <>
                        <div className="lg:col-span-3 overflow-y-auto pr-2">
                            <AutomaticPreparationCard onApply={handleAutoApply} />
                            <div className="mb-6">
                                <h3 className="text-lg font-semibold mb-4 text-white">Transformaciones Globales y Avanzadas</h3>
                                <PCACard state={state} dispatch={dispatch} runAnalysis={runAnalysis as any} />
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold mb-4 text-white">Transformaciones Manuales por Columna</h3>
                                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                                    {Object.keys(qualityReport).map(column => (
                                        <ColumnCard
                                            key={column}
                                            column={column}
                                            quality={qualityReport[column]}
                                            outlierInfo={outlierReport[column]}
                                            addTransformation={addTransformation}
                                        />
                                    ))}
                                </div>
                            </div>
                        </div>

                        <div className="bg-gray-800/50 p-4 rounded-lg border border-gray-700 flex flex-col">
                            <h3 className="text-lg font-semibold mb-4 text-white">Cambios Pendientes (Manual)</h3>
                            {transformations.length === 0 ? (
                                <div className="flex-grow flex items-center justify-center text-sm text-slate-500">
                                    <p>Selecciona acciones para preparar tus datos.</p>
                                </div>
                            ) : (
                                <ul className="space-y-2 flex-grow overflow-y-auto text-sm">
                                {transformations.map((t, i) => (
                                    <li key={i} className="bg-gray-700/50 p-2 rounded">
                                        {getActionDescription(t)}
                                    </li>
                                ))}
                                </ul>
                            )}
                            <div className="mt-4 space-y-2">
                                <button 
                                    onClick={handleApply}
                                    disabled={transformations.length === 0}
                                    className="w-full bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-2 px-4 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    Aplicar Transformaciones
                                </button>
                                <button 
                                    onClick={() => exportDataToCsv(processedData, fileName)}
                                    className="w-full flex items-center justify-center bg-gray-600 hover:bg-gray-500 text-white font-bold py-2 px-4 rounded transition-colors"
                                >
                                    <DownloadIcon className="w-4 h-4 mr-2"/>
                                    Descargar Datos Actuales
                                </button>
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};