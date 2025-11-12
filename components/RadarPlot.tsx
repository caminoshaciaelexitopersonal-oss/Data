import React, { useMemo, useRef, useState, useEffect } from 'react';
import { Radar, RadarChart, PolarGrid, Legend, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts';
import { DownloadIcon } from './icons';
import { handleDownloadChart } from '../services/chartUtils';

interface RadarPlotProps {
  centroids: number[][];
  featureNames: string[];
  colors: string[];
  hoveredCluster: number | null;
  onLegendEnter: (id: number) => void;
  onLegendLeave: () => void;
}

export const RadarPlot: React.FC<RadarPlotProps> = ({ centroids, featureNames, colors, hoveredCluster, onLegendEnter, onLegendLeave }) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    const timer = setTimeout(() => setIsLoading(false), 50);
    return () => clearTimeout(timer);
  }, [centroids, featureNames]);

  const chartData = useMemo(() => {
    // Recharts radar chart expects data where each item is a feature/subject
    return featureNames.map((feature, featureIndex) => {
      const featurePoint: { subject: string; [key: string]: string | number } = {
        subject: feature,
      };
      centroids.forEach((centroid, centroidIndex) => {
        featurePoint[`Clúster ${centroidIndex + 1}`] = centroid[featureIndex];
      });
      return featurePoint;
    });
  }, [centroids, featureNames]);

  const handleLegendMouseEnter = (e: any) => {
      const clusterIndex = parseInt(e.value.replace('Clúster ', ''), 10) - 1;
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
            onClick={() => handleDownloadChart(chartRef, 'radar-plot.png')} 
            className="absolute top-0 right-0 z-10 p-1.5 bg-gray-700/50 hover:bg-gray-600 rounded-bl-lg transition-colors"
            title="Descargar como PNG"
        >
            <DownloadIcon className="w-4 h-4 text-slate-300" />
        </button>
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="50%" outerRadius="80%" data={chartData}>
            <PolarGrid stroke="#374151"/>
            <PolarAngleAxis dataKey="subject" tick={{ fill: '#9ca3af', fontSize: 12 }} />
            <PolarRadiusAxis angle={30} domain={['auto', 'auto']} tick={{ fill: '#6b7280' }}/>
            <Tooltip
                contentStyle={{
                    backgroundColor: 'rgba(31, 41, 55, 0.5)',
                    backdropFilter: 'blur(4px)',
                    borderColor: '#4b5563',
                    color: '#d1d5db'
                }}
            />
            <Legend onMouseEnter={handleLegendMouseEnter} onMouseLeave={onLegendLeave} />
            {centroids.map((_, index) => (
              <Radar
                key={index}
                name={`Clúster ${index + 1}`}
                dataKey={`Clúster ${index + 1}`}
                stroke={colors[index % colors.length]}
                fill={colors[index % colors.length]}
                fillOpacity={hoveredCluster === null ? 0.4 : (hoveredCluster === index ? 0.6 : 0.1)}
                strokeOpacity={hoveredCluster === null ? 1 : (hoveredCluster === index ? 1 : 0.2)}
                label={{
                    position: 'outside',
                    offset: 5,
                    formatter: (value: number) => value.toFixed(2),
                    fontSize: 10,
                    fill: '#9ca3af'
                }}
              />
            ))}
          </RadarChart>
        </ResponsiveContainer>
    </div>
  );
};