import React, { useMemo, useRef, useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LabelList } from 'recharts';
import { DownloadIcon } from './icons';
import { handleDownloadChart } from '../services/chartUtils';

interface ProfilePlotProps {
  centroids: number[][];
  featureNames: string[];
  colors: string[];
  hoveredCluster: number | null;
  onLegendEnter: (id: number) => void;
  onLegendLeave: () => void;
}

export const ProfilePlot: React.FC<ProfilePlotProps> = ({ centroids, featureNames, colors, hoveredCluster, onLegendEnter, onLegendLeave }) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    const timer = setTimeout(() => setIsLoading(false), 50);
    return () => clearTimeout(timer);
  }, [centroids, featureNames]);

  const chartData = useMemo(() => {
    return featureNames.map((feature, featureIndex) => {
      const dataPoint: { feature: string; [key:string]: string | number } = {
        feature: feature,
      };
      centroids.forEach((centroid, centroidIndex) => {
        dataPoint[`Clúster ${centroidIndex + 1}`] = centroid[featureIndex];
      });
      return dataPoint;
    });
  }, [centroids, featureNames]);

  const handleLegendMouseEnter = (e: any) => {
      const clusterIndex = parseInt(e.dataKey.replace('Clúster ', ''), 10) - 1;
      if (!isNaN(clusterIndex)) onLegendEnter(clusterIndex);
  }

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

  return (
    <div className="w-full h-full relative" ref={chartRef}>
        <button 
            onClick={() => handleDownloadChart(chartRef, 'profile-plot.png')} 
            className="absolute top-0 right-0 z-10 p-1.5 bg-gray-700/50 hover:bg-gray-600 rounded-bl-lg transition-colors"
            title="Descargar como PNG"
        >
            <DownloadIcon className="w-4 h-4 text-slate-300" />
        </button>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart 
            data={chartData} 
            margin={{ top: 20, right: 40, left: 20, bottom: 5 }}
            layout="vertical"
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis type="number" stroke="#9ca3af" />
            <YAxis type="category" dataKey="feature" stroke="#9ca3af" width={120} tick={{ fontSize: 12 }}/>
            <Tooltip
                cursor={{fill: 'rgba(148, 163, 184, 0.1)'}}
                contentStyle={{
                    backgroundColor: 'rgba(31, 41, 55, 0.5)',
                    backdropFilter: 'blur(4px)',
                    borderColor: '#4b5563',
                    color: '#d1d5db'
                }}
                labelStyle={{ fontWeight: 'bold', color: '#94a3b8' }}
            />
            <Legend onMouseEnter={handleLegendMouseEnter} onMouseLeave={onLegendLeave} />
            {centroids.map((_, index) => (
              <Bar 
                key={`bar-${index}`} 
                dataKey={`Clúster ${index + 1}`} 
                fill={colors[index % colors.length]}
                fillOpacity={hoveredCluster === null || hoveredCluster === index ? 0.7 : 0.2}
              >
                <LabelList 
                    dataKey={`Clúster ${index + 1}`} 
                    position="right" 
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