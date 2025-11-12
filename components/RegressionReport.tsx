import React, { useState, useEffect } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Label, Line } from 'recharts';
import { RegressionResult } from '../types';
import { WandIcon, SparklesIcon, TrendingUpIcon } from './icons';
import { analyzeRegressionResults } from '../services/geminiService';
import { marked } from 'marked';

interface RegressionReportProps {
  result: RegressionResult;
  problemContext: string;
  datasetMetadata: string;
  setIsKeyReady: (isReady: boolean) => void;
}

const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const dataPoint = payload[0].payload;
      return (
        <div className="p-2 bg-gray-800/50 backdrop-blur-sm border border-gray-600 rounded-lg text-white text-sm">
          <p><strong>Actual:</strong> {dataPoint.actual.toFixed(2)}</p>
          <p><strong>Predicho:</strong> {dataPoint.predicted.toFixed(2)}</p>
        </div>
      );
    }
    return null;
};

export const RegressionReport: React.FC<RegressionReportProps> = ({ result, problemContext, datasetMetadata, setIsKeyReady }) => {
  const { rSquared, mse, predictions, targetVariable, featureVariables } = result;
  const [geminiAnalysis, setGeminiAnalysis] = useState('');
  const [isGeminiLoading, setIsGeminiLoading] = useState(false);

  const handleAnalyze = async () => {
    setIsGeminiLoading(true);
    setGeminiAnalysis('');
    try {
      const analysis = await analyzeRegressionResults(result, problemContext, datasetMetadata);
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
  
  const domain = [
    Math.min(...predictions.map(p => p.actual), ...predictions.map(p => p.predicted)),
    Math.max(...predictions.map(p => p.actual), ...predictions.map(p => p.predicted))
  ];

  return (
    <div className="p-4 sm:p-6 text-slate-200 animate-fade-in">
        <h2 className="text-2xl font-bold mb-4 flex items-center">
            <TrendingUpIcon className="w-6 h-6 mr-3 text-emerald-400"/>
            Resultados de Regresión Lineal
        </h2>
        <p className="mb-6 text-slate-400">
            El modelo fue entrenado para predecir <strong className="text-emerald-300">{targetVariable}</strong> usando <strong className="text-emerald-300">{featureVariables.join(', ')}</strong>.
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
             <div className="bg-gray-800/50 backdrop-blur-sm p-6 rounded-lg border border-gray-700">
                <h3 className="text-lg font-semibold mb-4 text-white">Métricas de Rendimiento</h3>
                <div className="space-y-4">
                    <div>
                        <p className="text-sm text-slate-400">R-Cuadrado (R²)</p>
                        <p className="text-3xl font-bold text-emerald-400">{rSquared.toFixed(3)}</p>
                        <p className="text-xs text-slate-500">
                            Porcentaje de la varianza en la variable objetivo que es predecible a partir de las variables independientes.
                        </p>
                    </div>
                     <div>
                        <p className="text-sm text-slate-400">Error Cuadrático Medio (MSE)</p>
                        <p className="text-3xl font-bold text-emerald-400">{mse.toFixed(3)}</p>
                        <p className="text-xs text-slate-500">
                            El promedio de los errores al cuadrado. Un valor más bajo indica un mejor ajuste.
                        </p>
                    </div>
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
             <h3 className="text-lg font-semibold mb-4 text-white">Gráfico de Predicciones vs. Valores Reales</h3>
             <div className="w-full h-80">
                <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                        <XAxis type="number" dataKey="actual" name="Valor Real" stroke="#9ca3af" domain={domain}>
                           <Label value="Valor Real" offset={-15} position="insideBottom" fill="#9ca3af" />
                        </XAxis>
                        <YAxis type="number" dataKey="predicted" name="Valor Predicho" stroke="#9ca3af" domain={domain}>
                           <Label value="Valor Predicho" angle={-90} offset={0} position="insideLeft" fill="#9ca3af" style={{ textAnchor: 'middle' }} />
                        </YAxis>
                        <Tooltip cursor={{ strokeDasharray: '3 3' }} content={<CustomTooltip />} />
                        <Scatter name="Predicciones" data={predictions} fill="#22d3ee" fillOpacity={0.6} shape="circle" />
                        <Line type="monotone" dataKey="actual" stroke="#f43f5e" strokeWidth={2} dot={false} activeDot={false} isAnimationActive={false} name="Línea de Ajuste Perfecto" />
                    </ScatterChart>
                </ResponsiveContainer>
             </div>
        </div>
    </div>
  );
};