// components/ClassificationReport.tsx

import React, { useState, useEffect } from 'react';
import { ClassificationResult } from '../types';
import { WandIcon, CheckCircleIcon, XCircleIcon, SparklesIcon } from './icons';
import { analyzeClassificationResults } from '../services/geminiService';
import { marked } from 'marked';


interface ClassificationReportProps {
  result: ClassificationResult;
  problemContext: string;
  datasetMetadata: string;
  setIsKeyReady: (isReady: boolean) => void;
}

const ConfusionMatrix: React.FC<{ matrix: number[][]; labels: string[] }> = ({ matrix, labels }) => {
    return (
        <div className="overflow-x-auto">
            <table className="w-full text-sm text-left text-slate-300">
                <thead className="text-xs text-slate-400 uppercase bg-gray-700/50">
                    <tr>
                        <th scope="col" className="px-4 py-2"></th>
                        <th scope="col" colSpan={labels.length} className="px-4 py-2 text-center">Clase Predicha</th>
                    </tr>
                    <tr>
                        <th scope="col" className="px-4 py-2">Clase Real</th>
                        {labels.map(label => <th key={label} className="px-4 py-2 text-center">{label}</th>)}
                    </tr>
                </thead>
                <tbody>
                    {matrix.map((row, i) => (
                        <tr key={i} className="border-b border-gray-700">
                            <th scope="row" className="px-4 py-2 font-medium text-slate-300 whitespace-nowrap">{labels[i]}</th>
                            {row.map((val, j) => {
                                const isDiagonal = i === j;
                                const total = row.reduce((a, b) => a + b, 0);
                                const intensity = total > 0 ? Math.min(val / total, 1) : 0;
                                const bgColor = isDiagonal 
                                    ? `rgba(34, 197, 94, ${intensity * 0.5 + 0.1})` 
                                    : `rgba(244, 63, 94, ${intensity * 0.5 + 0.1})`;

                                return (
                                    <td key={j} className="px-4 py-2 text-center" style={{ backgroundColor: bgColor }}>
                                        {val}
                                    </td>
                                );
                            })}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export const ClassificationReport: React.FC<ClassificationReportProps> = ({ result, problemContext, datasetMetadata, setIsKeyReady }) => {
  const { accuracy, confusionMatrix, report, classLabels, targetVariable, algorithm } = result;
  const [geminiAnalysis, setGeminiAnalysis] = useState('');
  const [isGeminiLoading, setIsGeminiLoading] = useState(false);

  const getAlgorithmName = (algo: string) => {
    switch(algo) {
        case 'naive_bayes': return 'Naive Bayes';
        case 'logistic_regression': return 'Regresión Logística';
        case 'decision_tree': return 'Árbol de Decisión';
        default: return 'Clasificación';
    }
  }

  const handleAnalyze = async () => {
    setIsGeminiLoading(true);
    setGeminiAnalysis('');
    try {
      const analysis = await analyzeClassificationResults(result, problemContext, datasetMetadata);
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

  useEffect(() => {
    handleAnalyze();
  }, [result]);

  return (
    <div className="p-4 sm:p-6 text-slate-200 animate-fade-in">
        <h2 className="text-2xl font-bold mb-4 flex items-center">
            <WandIcon className="w-6 h-6 mr-3 text-violet-400"/>
            Resultados de Clasificación ({getAlgorithmName(algorithm)})
        </h2>
        <p className="mb-6 text-slate-400">
            El modelo fue entrenado para predecir la clase de <strong className="text-violet-300">{targetVariable}</strong>.
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
                <div className="bg-gray-800/50 backdrop-blur-sm p-6 rounded-lg border border-gray-700 mb-6">
                    <h3 className="text-lg font-semibold mb-4 text-white">Exactitud (Accuracy) General</h3>
                    <div className="flex justify-between items-center">
                        <span className="text-4xl font-bold text-violet-400">{(accuracy * 100).toFixed(2)}%</span>
                        {accuracy > 0.8 ? <CheckCircleIcon className="w-10 h-10 text-emerald-500" /> : <XCircleIcon className="w-10 h-10 text-rose-500" />}
                    </div>
                    <p className="text-sm text-slate-500 mt-2">
                        Porcentaje de predicciones correctas sobre el total de casos de prueba.
                    </p>
                </div>

                <div className="bg-gray-800/50 backdrop-blur-sm p-6 rounded-lg border border-gray-700 mb-6">
                    <h3 className="text-lg font-semibold mb-4 text-white">Matriz de Confusión</h3>
                    <p className="text-sm text-slate-500 mb-4">
                        Muestra dónde se está equivocando el modelo. La diagonal verde representa las predicciones correctas.
                    </p>
                    <ConfusionMatrix matrix={confusionMatrix} labels={classLabels} />
                </div>
            </div>
             <div className="bg-gray-800/50 backdrop-blur-sm p-6 rounded-lg border border-gray-700">
                <h3 className="text-lg font-semibold mb-4 text-white flex items-center"><SparklesIcon className="w-5 h-5 mr-2 text-yellow-400" />Análisis con IA</h3>
                 {isGeminiLoading ? (
                     <div className="flex items-center justify-center h-full text-slate-500">
                         <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                             <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                             <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                         </svg>
                         <span>Analizando resultados...</span>
                     </div>
                 ) : (
                    <div className="prose prose-sm prose-invert max-w-none prose-p:text-slate-300 prose-headings:text-slate-200 prose-strong:text-yellow-300" dangerouslySetInnerHTML={{ __html: geminiAnalysis }} />
                 )}
            </div>
        </div>

        <div className="bg-gray-800/50 backdrop-blur-sm p-6 rounded-lg border border-gray-700 mt-6">
             <h3 className="text-lg font-semibold mb-4 text-white">Métricas por Clase</h3>
             <div className="overflow-x-auto">
                 <table className="w-full text-sm text-left text-slate-300">
                     <thead className="text-xs text-slate-400 uppercase bg-gray-700/50">
                         <tr>
                             <th scope="col" className="px-4 py-2">Clase</th>
                             <th scope="col" className="px-4 py-2">Precisión</th>
                             <th scope="col" className="px-4 py-2">Recall (Sensibilidad)</th>
                             <th scope="col" className="px-4 py-2">F1-Score</th>
                             <th scope="col" className="px-4 py-2">Soporte</th>
                         </tr>
                     </thead>
                     <tbody className="divide-y divide-gray-700">
                         {Object.entries(report).map(([className, metrics]) => {
                             const typedMetrics = metrics as { precision: number; recall: number; f1Score: number; support: number };
                             return (
                             <tr key={className} className="hover:bg-gray-800/60">
                                 <th scope="row" className="px-4 py-2 font-medium">{className}</th>
                                 <td className="px-4 py-2">{typedMetrics.precision.toFixed(2)}</td>
                                 <td className="px-4 py-2">{typedMetrics.recall.toFixed(2)}</td>
                                 <td className="px-4 py-2">{typedMetrics.f1Score.toFixed(2)}</td>
                                 <td className="px-4 py-2">{typedMetrics.support}</td>
                             </tr>
                             );
                         })}
                     </tbody>
                 </table>
             </div>
        </div>
    </div>
  );
};