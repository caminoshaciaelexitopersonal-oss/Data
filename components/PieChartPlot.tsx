import React, { useMemo, useRef, useState, useEffect } from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { DataPoint } from '../types';
import { DownloadIcon } from './icons';
import { handleDownloadChart } from '../services/chartUtils';

interface PieChartProps {
  data: (DataPoint & { cluster: number })[];
  colors: string[];
  centroids: number[][];
  featureNames: string[];
  hoveredCluster: number | null;
  onLegendEnter: (id: number) => void;
  onLegendLeave: () => void;
}


const CustomTooltip = ({ active, payload, centroids, featureNames }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload; // FIX: The data object for the pie slice is in payload[0].payload, not payload[0].payload.payload
    if (!data) return null; // Safety check

    const clusterId = data.clusterId;
    const centroid = centroids[clusterId];

    return (
      <div className="p-3 bg-gray-800/50 backdrop-blur-sm border border-gray-600 rounded-lg text-white text-sm shadow-lg max-w-xs">
        <p className="font-bold text-cyan-400 mb-2 border-b border-gray-600 pb-1">{data.name}</p>
        <p className="text-xs mb-2"><strong>Tamaño:</strong> {data.value} puntos ({(payload[0].percent * 100).toFixed(1)}%)</p>
        
        {centroid && (
          <>
            <p className="font-semibold text-slate-300 mb-1">Perfil del Clúster (Promedios):</p>
            <div className="text-xs pl-2 space-y-0.5 max-h-40 overflow-y-auto">
              {featureNames.map((name: string, index: number) => (
                <div key={name} className="flex justify-between">
                  <span>{name}:</span>
                  <span className="font-mono">{centroid[index].toFixed(2)}</span>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    );
  }

  return null;
};


export const PieChartPlot: React.FC<PieChartProps> = ({ data, colors, centroids, featureNames, hoveredCluster, onLegendEnter, onLegendLeave }) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    const timer = setTimeout(() => setIsLoading(false), 50);
    return () => clearTimeout(timer);
  }, [data]);

  const chartData = useMemo(() => {
    const clusterCounts: Record<string, number> = {};
    const clusterIdMap: Record<string, number> = {};
    
    data.forEach((point) => {
      const clusterName = point.cluster === -1 ? 'Ruido' : `Clúster ${point.cluster + 1}`;
      clusterCounts[clusterName] = (clusterCounts[clusterName] || 0) + 1;
      clusterIdMap[clusterName] = point.cluster;
    });

    return Object.entries(clusterCounts).map(([name, value]) => ({
        name,
        value,
        clusterId: clusterIdMap[name],
    }));
  }, [data]);
  
  const handleLegendMouseEnter = (e: any) => {
      const clusterId = chartData.find(c => c.name === e.value)?.clusterId;
      if (clusterId !== undefined) onLegendEnter(clusterId);
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
            onClick={() => handleDownloadChart(chartRef, 'pie-chart.png')} 
            className="absolute top-0 right-0 z-10 p-1.5 bg-gray-700/50 hover:bg-gray-600 rounded-bl-lg transition-colors"
            title="Descargar como PNG"
        >
            <DownloadIcon className="w-4 h-4 text-slate-300" />
        </button>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Tooltip
              content={<CustomTooltip centroids={centroids} featureNames={featureNames} />}
            />
            <Legend onMouseEnter={handleLegendMouseEnter} onMouseLeave={onLegendLeave}/>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, value, percent }) => `${value} (${(percent * 100).toFixed(0)}%)`}
              outerRadius="80%"
              innerRadius="50%"
              fill="#8884d8"
              dataKey="value"
              paddingAngle={2}
            >
              {chartData.map((entry, index) => (
                <Cell 
                    key={`cell-${entry.clusterId}`} 
                    fill={entry.clusterId === -1 ? '#6b7280' : colors[entry.clusterId % colors.length]} 
                    fillOpacity={hoveredCluster === null || hoveredCluster === entry.clusterId ? 0.8 : 0.2}
                    stroke={entry.clusterId === -1 ? '#6b7280' : colors[entry.clusterId % colors.length]}
                    strokeOpacity={hoveredCluster === entry.clusterId ? 1 : 0}
                    strokeWidth={2}
                />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
    </div>
  );
};