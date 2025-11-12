import React, { useRef } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Dot } from 'recharts';
import { DownloadIcon } from './icons';
import { handleDownloadChart } from '../services/chartUtils';

interface GenericPlotProps {
  data: any[];
  dataKey: string;
  name: string;
  color: string;
  xAxisLabel: string;
  yAxisLabel: string;
  optimalK?: number;
}

// Custom dot to highlight the optimal K
const CustomizedDot = (props: any) => {
    const { cx, cy, stroke, payload, optimalK } = props;
  
    if (payload.k === optimalK) {
      return (
        <g>
          <Dot cx={cx} cy={cy} r={8} fill={stroke} stroke="#fff" strokeWidth={2} />
          <text x={cx} y={cy - 15} textAnchor="middle" fill={stroke} fontSize="12" fontWeight="bold">
            Óptimo
          </text>
        </g>
      );
    }
  
    return <Dot cx={cx} cy={cy} r={4} fill={stroke} />;
};


export const GenericLinePlot: React.FC<GenericPlotProps> = ({ data, dataKey, name, color, xAxisLabel, yAxisLabel, optimalK }) => {
  const chartRef = useRef<HTMLDivElement>(null);
  return (
    <div className="w-full h-full relative" ref={chartRef}>
        <button 
            onClick={() => handleDownloadChart(chartRef, `${name.toLowerCase()}-plot.png`)} 
            className="absolute top-0 right-0 z-10 p-1.5 bg-gray-700/50 hover:bg-gray-600 rounded-bl-lg transition-colors"
            title="Descargar como PNG"
        >
            <DownloadIcon className="w-4 h-4 text-slate-300" />
        </button>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={data}
            margin={{
              top: 5,
              right: 20,
              left: 20,
              bottom: 20,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#374151"/>
            <XAxis dataKey="k" stroke="#9ca3af" label={{ value: xAxisLabel, position: 'insideBottom', offset: -10, fill: '#9ca3af' }}/>
            <YAxis stroke="#9ca3af" label={{ value: yAxisLabel, angle: -90, position: 'insideLeft', offset: -5, fill: '#9ca3af' }}/>
            <Tooltip 
                contentStyle={{
                    backgroundColor: 'rgba(31, 41, 55, 0.5)',
                    backdropFilter: 'blur(4px)',
                    borderColor: '#4b5563',
                    color: '#d1d5db'
                }}
            />
            <Legend verticalAlign="top" height={30} />
            <Line type="monotone" dataKey={dataKey} name={name} stroke={color} strokeWidth={2} dot={<CustomizedDot optimalK={optimalK} />}/>
          </LineChart>
        </ResponsiveContainer>
    </div>
  );
};