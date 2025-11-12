import React, { useMemo, useRef, useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LabelList } from 'recharts';
import { DataPoint } from '../types';
import { DownloadIcon } from './icons';
import { handleDownloadChart } from '../services/chartUtils';

interface BarPlotProps {
  data: (DataPoint & { cluster: number })[];
  featureKeys: string[];
  colors: string[];
}

export const BarPlot: React.FC<BarPlotProps> = ({ data, featureKeys, colors }) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    const timer = setTimeout(() => setIsLoading(false), 50);
    return () => clearTimeout(timer);
  }, [data, featureKeys]);

  const chartData = useMemo(() => {
    if (!featureKeys || featureKeys.length === 0) return [];

    const clusterAverages: { [clusterId: string]: { name: string; [featureKey: string]: string | number } } = {};

    // Initialize with all cluster names
    const clusterIds = [...new Set(data.map(p => p.cluster))];
    clusterIds.forEach((id: number) => {
        const name = id === -1 ? 'Ruido' : `Clúster ${id + 1}`;
        clusterAverages[String(id)] = { name };
    });

    // Calculate average for each selected feature within each cluster
    featureKeys.forEach(key => {
        const averages: { [clusterId: number]: number } = {};
        const counts: { [clusterId: number]: number } = {};

        data.forEach(point => {
            if (typeof point[key] === 'number') {
                averages[point.cluster] = (averages[point.cluster] || 0) + (point[key] as number);
                counts[point.cluster] = (counts[point.cluster] || 0) + 1;
            }
        });

        Object.keys(averages).forEach(clusterIdStr => {
            const clusterId = parseInt(clusterIdStr, 10);
            const avg = counts[clusterId] > 0 ? averages[clusterId] / counts[clusterId] : 0;
            if (clusterAverages[String(clusterId)]) {
                clusterAverages[String(clusterId)][key] = avg;
            }
        });
    });
    
    return Object.values(clusterAverages).sort((a,b) => a.name.localeCompare(b.name));
    
  }, [data, featureKeys]);

  if (isLoading) {
    return (
        <div className="flex items-center justify-center h-full text-slate-500">
            <svg className="animate-spin -ml-1 mr-3 h-8 w-8 text-cyan-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Renderizando gráfico...</span>
        </div>
    );
  }

  if (!featureKeys || featureKeys.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-slate-500">
        <p>Selecciona una o más características para mostrar el perfil del clúster.</p>
      </div>
    );
  }

  return (
    <div className="w-full h-full relative" ref={chartRef}>
        <button 
            onClick={() => handleDownloadChart(chartRef, 'bar-plot.png')} 
            className="absolute top-0 right-0 z-10 p-1.5 bg-gray-700/50 hover:bg-gray-600 rounded-bl-lg transition-colors"
            title="Descargar como PNG"
        >
            <DownloadIcon className="w-4 h-4 text-slate-300" />
        </button>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="name" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip
                cursor={{fill: 'rgba(148, 163, 184, 0.1)'}}
                contentStyle={{
                    backgroundColor: 'rgba(31, 41, 55, 0.5)',
                    backdropFilter: 'blur(4px)',
                    borderColor: '#4b5563',
                    color: '#d1d5db'
                }}
            />
            <Legend />
            {featureKeys.map((key, index) => (
                 <Bar key={key} dataKey={key} fill={colors[index % colors.length]} fillOpacity={0.7}>
                    <LabelList 
                        dataKey={key} 
                        position="top" 
                        formatter={(value: number) => value.toFixed(2)} 
                        style={{ fill: '#d1d5db', fontSize: 10 }} 
                    />
                 </Bar>
            ))}
          </BarChart>
        </ResponsiveContainer>
    </div>
  );
};