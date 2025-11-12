// components/ElbowMethodModal.tsx

import React, { useMemo } from 'react';
import { GenericLinePlot } from './ElbowPlot';

interface ElbowMethodModalProps {
  data: { k: number; inertia: number; silhouette: number }[];
  onApply: (k: number) => void;
  onClose: () => void;
}

export const ElbowMethodModal: React.FC<ElbowMethodModalProps> = ({ data, onApply, onClose }) => {

  const optimalK = useMemo(() => {
    if (!data || data.length === 0) return 3; // Default
    // Find the K with the maximum silhouette score
    const bestK = data.reduce((max, p) => p.silhouette > max.silhouette ? p : max, data[0]);
    return bestK.k;
  }, [data]);

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center animate-fade-in">
      <div className="bg-gray-800 rounded-lg shadow-xl p-6 border border-gray-700 w-full max-w-4xl">
        <h2 className="text-xl font-bold text-white mb-2">Análisis para Selección de K Óptimo</h2>
        <p className="text-slate-400 mb-4 text-sm">
          Usa estos gráficos para elegir el mejor número de clusters (K). El **Método del Codo** busca donde la inercia deja de bajar drásticamente. El **Score de Silueta** mide qué tan bien definidos están los clústeres (más alto es mejor).
        </p>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 h-72 bg-gray-900/50 rounded-lg p-4 border border-gray-700">
            <GenericLinePlot 
                data={data}
                dataKey="inertia"
                name="Inercia"
                color="#22d3ee"
                xAxisLabel="Número de Clústeres (K)"
                yAxisLabel="Inercia (SSE)"
            />
            <GenericLinePlot 
                data={data}
                dataKey="silhouette"
                name="Silhouette Score"
                color="#a78bfa"
                xAxisLabel="Número de Clústeres (K)"
                yAxisLabel="Score de Silueta"
                optimalK={optimalK}
            />
        </div>

        <div className="mt-4 bg-emerald-900/50 p-3 rounded-lg border border-emerald-500/30 text-center">
            <p className="text-sm text-slate-300">Basado en el score de silueta más alto, el número óptimo de clusters sugerido es:</p>
            <p className="text-4xl font-bold text-emerald-400 my-2">{optimalK}</p>
        </div>

        <div className="mt-6 flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-md text-slate-300 bg-gray-600 hover:bg-gray-500 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400"
          >
            Cerrar
          </button>
           <button
            onClick={() => onApply(optimalK)}
            className="px-4 py-2 rounded-md text-white font-semibold bg-cyan-600 hover:bg-cyan-700 transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-400"
          >
            Aplicar K = {optimalK} y Cerrar
          </button>
        </div>
      </div>
    </div>
  );
};