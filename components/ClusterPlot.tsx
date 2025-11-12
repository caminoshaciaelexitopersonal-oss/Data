import React, { useMemo, useRef, useState, useEffect } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { DataPoint } from '../types';
import { DownloadIcon } from './icons';
import { handleDownloadChart } from '../services/chartUtils';

interface ScatterPlotProps {
  data: (DataPoint & { cluster: number })[];
  xAxisKey: string;
  yAxisKey:string;
  colors: string[];
  centroids: number[][];
  featureNames: string[];
  hoveredCluster: number | null;
  onLegendEnter: (id: number) => void;
  onLegendLeave: () => void;
}

const CustomTooltip = ({ active, payload, centroids, featureNames, xAxisKey, yAxisKey }: any) => {
    if (active && payload && payload.length) {
      const dataPoint = payload[0].payload;
      const clusterId = dataPoint.cluster;
      const isCentroid = !!dataPoint.isCentroid;
      const xVal = (dataPoint[xAxisKey] as number);
      const yVal = (dataPoint[yAxisKey] as number);

      if (isCentroid) {
         return (
            <div className="p-3 bg-gray-800/50 backdrop-blur-sm border border-gray-600 rounded-lg text-white text-sm shadow-lg max-w-xs">
                <p className="font-bold text-white mb-1">{`Centroide del Clúster ${clusterId + 1}`}</p>
                <p className="font-mono text-center text-lg mb-1">{`(${xVal.toFixed(2)}, ${yVal.toFixed(2)})`}</p>
                 <div className="text-xs pl-2 space-y-0.5">
                    <div className="flex justify-between">
                        <span>{xAxisKey}:</span>
                        <span className="font-mono">{xVal.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                        <span>{yAxisKey}:</span>
                        <span className="font-mono">{yVal.toFixed(2)}</span>
                    </div>
                </div>
            </div>
        );
      }

      const clusterLabel = clusterId === -1 ? `Ruido (Noise)` : `Clúster ${clusterId + 1}`;
      const centroid = clusterId !== -1 ? centroids[clusterId] : null;

      return (
        <div className="p-3 bg-gray-800/50 backdrop-blur-sm border border-gray-600 rounded-lg text-white text-sm shadow-lg max-w-xs">
          <p className="font-bold text-cyan-400 mb-2 border-b border-gray-600 pb-1">{clusterLabel}</p>
          
          <p className="font-semibold text-slate-300">Coordenadas del Punto:</p>
          <p className="font-mono text-center text-lg my-2">{`(${xVal.toFixed(2)}, ${yVal.toFixed(2)})`}</p>
          <div className="text-xs pl-2 space-y-0.5 mb-2">
            <div className="flex justify-between">
              <span>{xAxisKey}:</span>
              <span className="font-mono">{xVal.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span>{yAxisKey}:</span>
              <span className="font-mono">{yVal.toFixed(2)}</span>
            </div>
          </div>

          {centroid && (
            <>
              <p className="font-semibold text-slate-300 mb-1 border-t border-gray-600 pt-2">Perfil del Clúster (Promedios):</p>
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

const renderCentroidLabel = (props: any) => {
    const { x, y, payload } = props;
    if (!payload || payload.cluster === undefined) return null;
    return (
        <text x={x} y={y} dy={16} fill="#fff" fontSize={12} textAnchor="middle" fontWeight="bold" style={{textShadow: '0 0 3px black'}}>
            C{payload.cluster + 1}
        </text>
    );
};


export const ScatterPlot: React.FC<ScatterPlotProps> = ({ data, xAxisKey, yAxisKey, colors, centroids, featureNames, hoveredCluster, onLegendEnter, onLegendLeave }) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    const timer = setTimeout(() => setIsLoading(false), 50);
    return () => clearTimeout(timer);
  }, [data, xAxisKey, yAxisKey]);
  
  const { groupedData, noiseData } = useMemo(() => {
    const clusters: { [key: number]: (DataPoint & { cluster: number })[] } = {};
    const noise: (DataPoint & { cluster: number })[] = [];
    
    data.forEach(point => {
      if (point.cluster === -1) {
        noise.push(point);
      } else {
        if (!clusters[point.cluster]) {
          clusters[point.cluster] = [];
        }
        clusters[point.cluster].push(point);
      }
    });

    const grouped = Object.entries(clusters).map(([clusterId, points]) => ({
      id: parseInt(clusterId, 10),
      points: points,
    }));

    return { groupedData: grouped, noiseData: noise };
  }, [data]);
  
  const centroidPoints = useMemo(() => {
    if (!centroids || !featureNames.length || !xAxisKey || !yAxisKey) return [];
    
    const xIndex = featureNames.indexOf(xAxisKey);
    const yIndex = featureNames.indexOf(yAxisKey);

    if (xIndex === -1 || yIndex === -1) return [];

    return centroids.map((centroid, index) => ({
      [xAxisKey]: centroid[xIndex],
      [yAxisKey]: centroid[yIndex],
      cluster: index,
      isCentroid: true,
    }));
  }, [centroids, featureNames, xAxisKey, yAxisKey]);


  const handleLegendMouseEnter = (e: any) => {
      const clusterId = groupedData.find(c => `Clúster ${c.id + 1}` === e.value)?.id;
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
  
  if (!data.length || !xAxisKey || !yAxisKey) {
    return (
      <div className="flex items-center justify-center h-full text-slate-500">
        <p>Selecciona los ejes X e Y para mostrar el gráfico.</p>
      </div>
    );
  }
  
  return (
    <div className="w-full h-full relative" ref={chartRef}>
        <button 
            onClick={() => handleDownloadChart(chartRef, 'scatter-plot.png')} 
            className="absolute top-0 right-0 z-10 p-1.5 bg-gray-700/50 hover:bg-gray-600 rounded-bl-lg transition-colors"
            title="Descargar como PNG"
        >
            <DownloadIcon className="w-4 h-4 text-slate-300" />
        </button>
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 30, bottom: 20, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis type="number" dataKey={xAxisKey} name={xAxisKey} unit="" stroke="#9ca3af" />
            <YAxis type="number" dataKey={yAxisKey} name={yAxisKey} unit="" stroke="#9ca3af" />
            <Tooltip cursor={{ strokeDasharray: '3 3' }} content={<CustomTooltip centroids={centroids} featureNames={featureNames} xAxisKey={xAxisKey} yAxisKey={yAxisKey} />} />
            <Legend 
                onMouseEnter={handleLegendMouseEnter} 
                onMouseLeave={onLegendLeave} 
                formatter={(value) => <span title={value}>{value}</span>}
            />
            {groupedData.map(cluster => (
              <Scatter 
                key={cluster.id}
                name={`Clúster ${cluster.id + 1}`} 
                data={cluster.points} 
                fill={colors[cluster.id % colors.length]} 
                fillOpacity={hoveredCluster === null || hoveredCluster === cluster.id ? 0.7 : 0.1}
                shape="circle"
              />
            ))}
             {noiseData.length > 0 && (
                <Scatter
                    name="Ruido"
                    data={noiseData}
                    fill="#6b7280"
                    fillOpacity={0.3}
                    shape="cross"
                    legendType='none'
                />
            )}
            
            <Scatter name="Centroides" data={[]} shape="star" fill="#ffffff" stroke="#000000" />
            
            {centroidPoints.map(point => {
                const isHovered = point.cluster === hoveredCluster;
                const isDimmed = hoveredCluster !== null && !isHovered;
            
                return (
                    <Scatter
                        key={`centroid-${point.cluster}`}
                        data={[point]}
                        fill={isHovered ? '#fde047' : '#ffffff'}
                        stroke={isHovered ? '#fde047' : '#000000'}
                        strokeWidth={isHovered ? 2 : 1}
                        fillOpacity={isDimmed ? 0.2 : 1}
                        strokeOpacity={isDimmed ? 0.2 : 1}
                        shape="star"
                        size={isHovered ? 150 : 80}
                        zIndex={100 + (isHovered ? 1 : 0)}
                        label={renderCentroidLabel}
                        legendType="none"
                    />
                );
            })}
          </ScatterChart>
        </ResponsiveContainer>
    </div>
  );
};