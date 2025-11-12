import React, { useState, useEffect, useMemo } from 'react';
import { ModelComparisonResultItem } from '../types';
import { ProfileIcon, SparklesIcon, TrophyIcon, XCircleIcon } from './icons';
import { analyzeModelComparison } from '../services/geminiService';
import { marked } from 'marked';

interface ModelComparisonViewProps {
  results: ModelComparisonResultItem[];
  problemContext: string;
  datasetMetadata: string;
  setIsKeyReady: (isReady: boolean) => void;
}

type BestMetrics = {
    accuracy: string | null;
    precision: string | null;
    recall: string | null;
    f1Score: string | null;
}

export const ModelComparisonView: React.FC<ModelComparisonViewProps> = ({ results, problemContext, datasetMetadata, setIsKeyReady }) => {
  const [geminiAnalysis, setGeminiAnalysis] = useState('');
  const [isGeminiLoading, setIsGeminiLoading] = useState(false);

  useEffect(() => {
    const handleAnalyze = async () => {
      setIsGeminiLoading(true);
      setGeminiAnalysis('');
      try {
        const analysis = await analyzeModelComparison(results, problemContext, datasetMetadata);
        const htmlAnalysis = await marked.parse(analysis);
        setGeminiAnalysis(htmlAnalysis);
      } catch (error) {
        const message = error instanceof Error ? error.message : "Error desconocido.";
        if (message === 'INVALID_KEY') {
            setIsKeyReady(false);
            setGeminiAnalysis(`<p>La clave API seleccionada no es válida.</p><p class="text-xs text-rose-400">Por favor, selecciona una clave válida desde la barra lateral.</p>`);
        } else {
            setGeminiAnalysis(`<p>El análisis de IA no pudo ser completado.</p><p class="text-xs text-rose-400">${message}</p>`);
        }
      } finally {
        setIsGeminiLoading(false);
      }
    };
    if (results && results.length > 0) {
        handleAnalyze();
    }
  }, [results]);

  const bestMetrics = useMemo<BestMetrics>(() => {
    const validResults = results.filter(r => !r.error);
    if(validResults.length === 0) return { accuracy: null, precision: null, recall: null, f1Score: null };
    
    const findBest = (metric: keyof Omit<ModelComparisonResultItem, 'algorithm' | 'error'>) => {
        return validResults.reduce((best, current) => {
            const bestValue = best[metric];
            const currentValue = current[metric];
            if (bestValue === undefined && currentValue !== undefined) return current;
            if (bestValue !== undefined && currentValue !== undefined && currentValue > bestValue) return current;
            return best;
        }).algorithm;
    };
    
    return {
        accuracy: findBest('accuracy'),
        precision: findBest('precision'),
        recall: findBest('recall'),
        f1Score: findBest('f1Score'),
    }
  }, [results]);

  return (
    <div className="p-4 sm:p-6 text-slate-200 animate-fade-in">
      <h2 className="text-2xl font-bold mb-4 flex items-center">
        <ProfileIcon className="w-6 h-6 mr-3 text-cyan-400"/>
        Comparación de Modelos de Clasificación
      </h2>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
            <div className="bg-gray-800/50 backdrop-blur-sm p-6 rounded-lg border border-gray-700">
                 <h3 className="text-lg font-semibold mb-4 text-white">Tabla de Rendimiento</h3>
                 <div className="overflow-x-auto">
                     <table className="w-full text-sm text-left text-slate-300">
                         <thead className="text-xs text-slate-400 uppercase bg-gray-700/50">
                             <tr>
                                 <th scope="col" className="px-4 py-2">Algoritmo</th>
                                 <th scope="col" className="px-4 py-2 text-center">Accuracy</th>
                                 <th scope="col" className="px-4 py-2 text-center">Precisión (Macro)</th>
                                 <th scope="col" className="px-4 py-2 text-center">Recall (Macro)</th>
                                 <th scope="col" className="px-4 py-2 text-center">F1-Score (Macro)</th>
                             </tr>
                         </thead>
                         <tbody className="divide-y divide-gray-700">
                             {results.map((result) => (
                                 <tr key={result.algorithm} className="hover:bg-gray-800/60">
                                     <th scope="row" className="px-4 py-3 font-medium">{result.algorithm}</th>
                                     {result.error ? (
                                        <td colSpan={4} className="px-4 py-3 text-rose-400">
                                            <div className="flex items-center justify-center">
                                               <XCircleIcon className="w-4 h-4 mr-2"/> Error: {result.error}
                                            </div>
                                        </td>
                                     ) : (
                                        <>
                                            <td className={`px-4 py-3 text-center font-mono ${result.algorithm === bestMetrics.accuracy ? 'bg-emerald-500/10 text-emerald-300' : ''}`}>
                                                <div className="flex items-center justify-center">
                                                    {result.algorithm === bestMetrics.accuracy && <TrophyIcon className="w-4 h-4 mr-2 text-yellow-400"/>}
                                                    {result.accuracy?.toFixed(3)}
                                                </div>
                                            </td>
                                            <td className={`px-4 py-3 text-center font-mono ${result.algorithm === bestMetrics.precision ? 'bg-emerald-500/10 text-emerald-300' : ''}`}>
                                                <div className="flex items-center justify-center">
                                                    {result.algorithm === bestMetrics.precision && <TrophyIcon className="w-4 h-4 mr-2 text-yellow-400"/>}
                                                    {result.precision?.toFixed(3)}
                                                </div>
                                            </td>
                                            <td className={`px-4 py-3 text-center font-mono ${result.algorithm === bestMetrics.recall ? 'bg-emerald-500/10 text-emerald-300' : ''}`}>
                                                 <div className="flex items-center justify-center">
                                                    {result.algorithm === bestMetrics.recall && <TrophyIcon className="w-4 h-4 mr-2 text-yellow-400"/>}
                                                    {result.recall?.toFixed(3)}
                                                </div>
                                            </td>
                                            <td className={`px-4 py-3 text-center font-mono ${result.algorithm === bestMetrics.f1Score ? 'bg-emerald-500/10 text-emerald-300' : ''}`}>
                                                 <div className="flex items-center justify-center">
                                                    {result.algorithm === bestMetrics.f1Score && <TrophyIcon className="w-4 h-4 mr-2 text-yellow-400"/>}
                                                    {result.f1Score?.toFixed(3)}
                                                </div>
                                            </td>
                                        </>
                                     )}
                                 </tr>
                             ))}
                         </tbody>
                     </table>
                 </div>
            </div>
        </div>
        <div className="bg-gray-800/50 backdrop-blur-sm p-6 rounded-lg border border-gray-700">
            <h3 className="text-lg font-semibold mb-4 text-white flex items-center"><SparklesIcon className="w-5 h-5 mr-2 text-yellow-400" />Resumen y Recomendación con IA</h3>
             {isGeminiLoading ? (
                 <div className="flex items-center justify-center h-full text-slate-500">
                     <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                         <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                         <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                     </svg>
                     <span>Analizando resultados...</span>
                 </div>
             ) : (
                <div className="prose prose-sm prose-invert max-w-none prose-p:text-slate-300 prose-headings:text-slate-200 prose-strong:text-yellow-300 prose-a:text-cyan-400" dangerouslySetInnerHTML={{ __html: geminiAnalysis }} />
             )}
        </div>
      </div>
    </div>
  );
};