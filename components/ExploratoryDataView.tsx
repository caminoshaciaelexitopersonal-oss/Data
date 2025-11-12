

// components/ExploratoryDataView.tsx

import React, { useMemo } from 'react';
import { State, DataPoint } from '../types';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LabelList } from 'recharts';

interface ExploratoryDataViewProps {
  state: State;
}

type NumericStats = {
    type: 'numeric';
    count: number;
    mean?: string;
    std?: string;
    min?: string;
    p25?: string;
    median?: string;
    p75?: string;
    max?: string;
};

type CategoricalStats = {
    type: 'categorical';
    count: number;
    unique?: number;
    top?: string;
    freq?: number;
};

type StatsInfo = NumericStats | CategoricalStats;

const calculateStats = (data: DataPoint[], qualityReport: State['qualityReport']): Record<string, StatsInfo> => {
    const stats: Record<string, StatsInfo> = {};
    const headers = Object.keys(qualityReport);

    headers.forEach(header => {
        const type = qualityReport[header].type as 'numeric' | 'categorical';
        const values = data.map(row => row[header]).filter(v => v !== null && v !== undefined && v !== '');
        
        if (type === 'numeric') {
            const numericValues = values.map(Number).filter(v => !isNaN(v) && isFinite(v));
            if(numericValues.length === 0) {
                 stats[header] = { type, count: 0 };
                 return;
            }
            const sum = numericValues.reduce((a, b) => a + b, 0);
            const mean = sum / numericValues.length;
            const sorted = [...numericValues].sort((a, b) => a - b);
            const mid = Math.floor(sorted.length / 2);
            const median = sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
            const std = Math.sqrt(numericValues.map(x => (x - mean) ** 2).reduce((a, b) => a + b, 0) / numericValues.length);
            
            stats[header] = {
                type,
                count: numericValues.length,
                mean: mean.toFixed(2),
                std: std.toFixed(2),
                min: Math.min(...numericValues).toFixed(2),
                p25: sorted[Math.floor(sorted.length * 0.25)].toFixed(2),
                median: median.toFixed(2),
                p75: sorted[Math.floor(sorted.length * 0.75)].toFixed(2),
                max: Math.max(...numericValues).toFixed(2),
            };

        } else { // categorical
            const categoricalValues = values.map(String);
             if(categoricalValues.length === 0) {
                 stats[header] = { type, count: 0 };
                 return;
            }
            const counts: Record<string, number> = {};
            categoricalValues.forEach(val => { counts[val] = (counts[val] || 0) + 1; });
            const mode = Object.keys(counts).reduce((a, b) => counts[a] > counts[b] ? a : b, '');

            stats[header] = {
                type,
                count: categoricalValues.length,
                unique: Object.keys(counts).length,
                top: mode,
                freq: counts[mode]
            };
        }
    });

    return stats;
};

const createHistogramData = (numericValues: number[], numBins = 10): { bin: string, count: number }[] => {
    if (numericValues.length === 0) return [];

    const min = Math.min(...numericValues);
    const max = Math.max(...numericValues);
    
    if (min === max) {
        return [{ bin: `${min}`, count: numericValues.length }];
    }

    const range = max - min;
    const binSize = range / numBins;

    const bins = new Array(numBins).fill(0).map((_, i) => {
        const binStart = min + i * binSize;
        const binEnd = min + (i + 1) * binSize;
        return {
            bin: `${binStart.toFixed(1)}-${binEnd.toFixed(1)}`,
            count: 0
        };
    });

    numericValues.forEach(value => {
        let binIndex = Math.floor((value - min) / binSize);
        if (value === max) { // Handle max value edge case
            binIndex = numBins - 1;
        }
        if (bins[binIndex]) {
            bins[binIndex].count++;
        }
    });

    return bins;
};


const NumericDistributionChart: React.FC<{ data: { bin: string, count: number }[] }> = ({ data }) => {
    return (
        <ResponsiveContainer width="100%" height={200}>
            <BarChart data={data} margin={{ top: 20, right: 10, left: -20, bottom: 35 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151"/>
                <XAxis dataKey="bin" stroke="#9ca3af" tick={{ fontSize: 8 }} angle={-45} textAnchor="end" height={50} interval="preserveStartEnd" />
                <YAxis stroke="#9ca3af" tick={{ fontSize: 10 }} allowDecimals={false}/>
                <Tooltip
                    cursor={{fill: 'rgba(148, 163, 184, 0.1)'}}
                    contentStyle={{
                        backgroundColor: 'rgba(31, 41, 55, 0.5)',
                        backdropFilter: 'blur(4px)',
                        borderColor: '#4b5563',
                        color: '#d1d5db'
                    }}
                />
                <Bar dataKey="count" fill="#22d3ee" fillOpacity={0.7} />
            </BarChart>
        </ResponsiveContainer>
    );
};

const CategoricalDistributionChart: React.FC<{ data: { name: string, count: number }[] }> = ({ data }) => {
     return (
        <ResponsiveContainer width="100%" height={200}>
            <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                 <CartesianGrid strokeDasharray="3 3" stroke="#374151"/>
                 <XAxis type="number" stroke="#9ca3af" tick={{ fontSize: 10 }} />
                 <YAxis type="category" dataKey="name" stroke="#9ca3af" width={80} tick={{ fontSize: 10 }} />
                 <Tooltip
                    cursor={{fill: 'rgba(148, 163, 184, 0.1)'}}
                    contentStyle={{
                        backgroundColor: 'rgba(31, 41, 55, 0.5)',
                        backdropFilter: 'blur(4px)',
                        borderColor: '#4b5563',
                        color: '#d1d5db'
                    }}
                 />
                 <Bar dataKey="count" fill="#a78bfa" fillOpacity={0.7}>
                    <LabelList dataKey="count" position="right" style={{ fill: '#d1d5db', fontSize: 10 }} />
                 </Bar>
            </BarChart>
        </ResponsiveContainer>
    );
}

export const ExploratoryDataView: React.FC<ExploratoryDataViewProps> = ({ state }) => {
    const { processedData, fileName, qualityReport } = state;

    const stats = useMemo(() => calculateStats(processedData, qualityReport), [processedData, qualityReport]);

    const numericHeaders = Object.keys(qualityReport).filter(h => qualityReport[h].type === 'numeric');
    const categoricalHeaders = Object.keys(qualityReport).filter(h => qualityReport[h].type === 'categorical');

    return (
        <div className="p-4 sm:p-6 text-slate-200 animate-fade-in">
            <h2 className="text-2xl font-bold mb-1">Análisis Exploratorio de Datos</h2>
            <p className="text-slate-400 mb-6">Un resumen de las características y distribuciones de <strong className="text-cyan-300">{fileName}</strong>.</p>
            
            <div className="bg-gray-800/50 backdrop-blur-sm p-4 rounded-lg border border-gray-700 mb-6">
                 <h3 className="text-lg font-semibold mb-4 text-white">Estadísticas Descriptivas</h3>
                 <div className="overflow-x-auto">
                     <table className="w-full text-sm text-left text-slate-300">
                         <thead className="text-xs text-slate-400 uppercase bg-gray-700/50">
                             <tr>
                                 <th className="px-4 py-2">Variable</th>
                                 <th className="px-4 py-2">Tipo</th>
                                 <th className="px-4 py-2">Conteo</th>
                                 <th className="px-4 py-2">Media / Únicos</th>
                                 <th className="px-4 py-2">Desv. Est. / Top</th>
                                 <th className="px-4 py-2">Min / Freq.</th>
                                 <th className="px-4 py-2">25%</th>
                                 <th className="px-4 py-2">Mediana</th>
                                 <th className="px-4 py-2">75%</th>
                                 <th className="px-4 py-2">Max</th>
                             </tr>
                         </thead>
                         <tbody className="divide-y divide-gray-700">
                             {Object.entries(stats).map(([header, s]) => {
                                const statsInfo = s as StatsInfo;
                                return (
                                <tr key={header} className="hover:bg-gray-800/60">
                                    <td className="px-4 py-2 font-medium">{header}</td>
                                    <td className="px-4 py-2"><span className={`px-2 py-0.5 rounded text-xs ${statsInfo.type === 'numeric' ? 'bg-sky-500/20 text-sky-300' : 'bg-fuchsia-500/20 text-fuchsia-300'}`}>{statsInfo.type}</span></td>
                                    <td className="px-4 py-2">{statsInfo.count}</td>
                                    <td className="px-4 py-2">{statsInfo.type === 'numeric' ? statsInfo.mean : statsInfo.unique}</td>
                                    <td className="px-4 py-2">{statsInfo.type === 'numeric' ? statsInfo.std : statsInfo.top}</td>
                                    <td className="px-4 py-2">{statsInfo.type === 'numeric' ? statsInfo.min : statsInfo.freq}</td>
                                    <td className="px-4 py-2">{statsInfo.type === 'numeric' ? statsInfo.p25 : '-'}</td>
                                    <td className="px-4 py-2">{statsInfo.type === 'numeric' ? statsInfo.median : '-'}</td>
                                    <td className="px-4 py-2">{statsInfo.type === 'numeric' ? statsInfo.p75 : '-'}</td>
                                    <td className="px-4 py-2">{statsInfo.type === 'numeric' ? statsInfo.max : '-'}</td>
                                </tr>
                                );
                             })}
                         </tbody>
                     </table>
                 </div>
            </div>

            <div className="bg-gray-800/50 backdrop-blur-sm p-4 rounded-lg border border-gray-700">
                 <h3 className="text-lg font-semibold mb-4 text-white">Distribución de Variables</h3>
                 <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {numericHeaders.map(header => {
                        const numericValues = processedData.map(row => row[header] as number).filter(v => v !== null && Number.isFinite(v));
                        const chartData = createHistogramData(numericValues);
                        return (
                            <div key={header} className="bg-gray-900/50 p-2 rounded border border-gray-700">
                                <h4 className="text-sm font-semibold text-center text-slate-300 mb-2">{header}</h4>
                                <NumericDistributionChart data={chartData} />
                            </div>
                        );
                    })}
                     {categoricalHeaders.map(header => {
                        const counts: Record<string, number> = {};
                        processedData.forEach(row => { 
                            const val = row[header];
                            if(val !== null && val !== undefined) counts[String(val)] = (counts[String(val)] || 0) + 1;
                        });
                        const chartData = Object.entries(counts).map(([name, count]) => ({name, count})).sort((a,b) => b.count - a.count).slice(0, 10); // Limit to top 10 for readability
                        return (
                            <div key={header} className="bg-gray-900/50 p-2 rounded border border-gray-700">
                                <h4 className="text-sm font-semibold text-center text-slate-300 mb-2">{header}</h4>
                               <CategoricalDistributionChart data={chartData} />
                            </div>
                        );
                    })}
                 </div>
            </div>

        </div>
    )
}