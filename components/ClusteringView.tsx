// components/ClusteringView.tsx

import React, { useState, useEffect, useRef } from 'react';
import { State, Action } from '../types';
import { ScatterPlot } from './ClusterPlot';
import { RadarPlot } from './RadarPlot';
import { ProfilePlot } from './ProfilePlot';
import { PieChartPlot } from './PieChartPlot';
import { GenericLinePlot } from './ElbowPlot';
import { BarPlot } from './BarPlot';
import {
    TableIcon, ScatterIcon, RadarIcon, PieChartIcon, ProfileIcon, BarChartIcon, LineChartIcon,
    TargetIcon, SparklesIcon
} from './icons';
import { analyzeClusterResults } from '../services/geminiService';
import { captureChartAsBase64 } from '../services/chartUtils';
import { marked } from 'marked';

interface ClusteringViewProps {
  state: State;
  setIsKeyReady: (isReady: boolean) => void;
}

const EmptyState: React.FC<{ icon: React.ReactNode, title: string, message: string }> = ({ icon, title, message }) => (
    <div className="flex flex-col items-center justify-center h-full text-center text-slate-500 p-8">
        <div className="mb-4">{icon}</div>
        <h3 className="text-xl font-semibold text-slate-300 mb-2">{title}</h3>
        <p className="max-w-md">{message}</p>
    </div>
);

const MetricCard: React.FC<{title: string, value: string, helpText: string}> = ({title, value, helpText}) => (
    <div>
        <h4 className="text-sm text-slate-400">{title}</h4>
        <p className="text-2xl font-bold text-cyan-300">{value}</p>
        <p className="text-xs text-slate-500">{helpText}</p>
    </div>
);

const ContingencyTable: React.FC<{table: {[key: string]: {[key: string]: number}}}> = ({table}) => {
    const clusterNames = Object.keys(table).sort();
    const trueLabels = [...new Set(clusterNames.flatMap(c => Object.keys(table[c])))].sort();

    return (
        <div className="overflow-x-auto">
            <table className="w-full text-sm text-left text-slate-300">
                <thead className="text-xs text-slate-400 uppercase bg-gray-900/50">
                    <tr>
                        <th scope="col" className="px-3 py-2">Clúster</th>
                        {trueLabels.map(label => <th key={label} scope="col" className="px-3 py-2 text-center">{label}</th>)}
                    </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                    {clusterNames.map(cluster => (
                        <tr key={cluster}>
                            <th scope="row" className="px-3 py-2 font-medium">{cluster}</th>
                            {trueLabels.map(label => <td key={label} className="px-3 py-2 text-center">{table[cluster][label] || 0}</td>)}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};


export const ClusteringView: React.FC<ClusteringViewProps> = ({ state, setIsKeyReady }) => {
    const { clusterResults, processedData, problemContext, datasetMetadata } = state;
    const [viewType, setViewType] = useState('scatter');
    const [xAxis, setXAxis] = useState('');
    const [yAxis, setYAxis] = useState('');
    const [barFeatures, setBarFeatures] = useState<string[]>([]);
    const [hoveredCluster, setHoveredCluster] = useState<number | null>(null);
    const [geminiAnalysis, setGeminiAnalysis] = useState('');
    const [isGeminiLoading, setIsGeminiLoading] = useState(false);
    const chartContainerRef = useRef<HTMLDivElement>(null);

    const colors = ["#22d3ee", "#a78bfa", "#f87171", "#4ade80", "#facc15", "#fb923c", "#f472b6", "#60a5fa"];

    useEffect(() => {
        if (clusterResults) {
            setXAxis(clusterResults.featureNames[0] || '');
            setYAxis(clusterResults.featureNames[1] || clusterResults.featureNames[0] || '');
            setBarFeatures(clusterResults.featureNames.slice(0, 3));
        }
    }, [clusterResults]);

    useEffect(() => {
        const handleAnalyze = async () => {
            if (!clusterResults || !chartContainerRef.current) return;
            setIsGeminiLoading(true);
            setGeminiAnalysis('');
            try {
                // Wait a bit for chart to render before capturing
                await new Promise(resolve => setTimeout(resolve, 300));
                
                const imageBase64 = await captureChartAsBase64(chartContainerRef);
                const analysis = await analyzeClusterResults(imageBase64, clusterResults, problemContext, datasetMetadata);
                const htmlAnalysis = await marked.parse(analysis);
                setGeminiAnalysis(htmlAnalysis);
            } catch (error) {
                const message = error instanceof Error ? error.message : "Error desconocido.";
                if (message === 'INVALID_KEY') {
                    setIsKeyReady(false);
                    setGeminiAnalysis(`<p>La clave API seleccionada no es válida.</p><p class="text-xs text-rose-400">Por favor, selecciona una clave válida.</p>`);
                } else {
                    setGeminiAnalysis(`<p>El análisis de IA no pudo ser completado.</p><p class="text-xs text-rose-400">${message}</p>`);
                }
            } finally {
                setIsGeminiLoading(false);
            }
        };

        if (clusterResults) {
            handleAnalyze();
        }
    }, [clusterResults, viewType]); // Re-analyze if the view changes to capture the new chart

    if (!clusterResults) {
        return <EmptyState 
            icon={<TargetIcon className="w-16 h-16 text-slate-700"/>}
            title="Análisis de Clustering"
            message="Configura los parámetros en la barra lateral y ejecuta el análisis para agrupar tus datos y descubrir patrones."
        />;
    }
    
    const dataWithClusters = processedData.map((point, index) => ({
        ...point,
        cluster: clusterResults.assignments[index],
    }));
    
    const featureOptions = clusterResults.featureNames.map(name => <option key={name} value={name}>{name}</option>);

    const renderCurrentView = () => {
        switch (viewType) {
            case 'scatter':
                return <ScatterPlot 
                            data={dataWithClusters} 
                            xAxisKey={xAxis} 
                            yAxisKey={yAxis} 
                            colors={colors} 
                            centroids={clusterResults.centroids}
                            featureNames={clusterResults.featureNames}
                            hoveredCluster={hoveredCluster}
                            onLegendEnter={(id) => setHoveredCluster(id)}
                            onLegendLeave={() => setHoveredCluster(null)}
                        />;
            case 'radar':
                return <RadarPlot 
                            centroids={clusterResults.centroids}
                            featureNames={clusterResults.featureNames}
                            colors={colors}
                            hoveredCluster={hoveredCluster}
                            onLegendEnter={(id) => setHoveredCluster(id)}
                            onLegendLeave={() => setHoveredCluster(null)}
                        />;
            case 'pie':
                return <PieChartPlot 
                            data={dataWithClusters} 
                            colors={colors} 
                            centroids={clusterResults.centroids}
                            featureNames={clusterResults.featureNames}
                            hoveredCluster={hoveredCluster}
                            onLegendEnter={(id) => setHoveredCluster(id)}
                            onLegendLeave={() => setHoveredCluster(null)}
                        />;
            case 'profile':
                 return <ProfilePlot 
                            centroids={clusterResults.centroids}
                            featureNames={clusterResults.featureNames}
                            colors={colors}
                            hoveredCluster={hoveredCluster}
                            onLegendEnter={(id) => setHoveredCluster(id)}
                            onLegendLeave={() => setHoveredCluster(null)}
                        />;
            case 'bar':
                return <BarPlot data={dataWithClusters} featureKeys={barFeatures} colors={colors} />
            case 'elbow':
                return clusterResults.elbowData ? 
                       <GenericLinePlot data={clusterResults.elbowData} dataKey="inertia" name="Inercia" color="#22d3ee" xAxisLabel="K" yAxisLabel="Inercia (SSE)" /> : 
                       <div className="flex items-center justify-center h-full text-slate-500">El método del codo solo está disponible al determinar K automáticamente.</div>;
            default: return null;
        }
    }

    const renderControls = () => {
         if (viewType === 'scatter') {
             return (
                 <>
                    <label className="text-xs mr-2">Eje X:</label>
                    <select value={xAxis} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setXAxis(e.currentTarget.value)} className="bg-gray-700 rounded p-1 text-xs">{featureOptions}</select>
                    <label className="text-xs ml-4 mr-2">Eje Y:</label>
                    <select value={yAxis} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setYAxis(e.currentTarget.value)} className="bg-gray-700 rounded p-1 text-xs">{featureOptions}</select>
                 </>
             );
         }
         if (viewType === 'bar') {
              return (
                 <>
                    <label className="text-xs mr-2">Características:</label>
                    <select multiple value={barFeatures} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setBarFeatures(Array.from(e.currentTarget.selectedOptions, (o: HTMLOptionElement) => o.value))} className="bg-gray-700 rounded p-1 text-xs h-16">{featureOptions}</select>
                 </>
             );
         }
         return null;
    }

    const ViewButton = ({ type, icon, label }: {type: string, icon: React.ReactNode, label: string}) => (
        <button onClick={() => setViewType(type)} title={label} className={`p-2 rounded transition-colors ${viewType === type ? 'bg-cyan-500/20 text-cyan-300' : 'hover:bg-gray-700'}`}>
            {icon}
        </button>
    );

    return (
        <div className="p-4 sm:p-6 h-full flex flex-col animate-fade-in">
            <h2 className="text-2xl font-bold mb-1">Resultados del Clustering ({clusterResults.algorithm})</h2>
            <p className="text-slate-400 mb-4">Visualiza los grupos identificados en tus datos.</p>
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-grow overflow-hidden">
                <div className="lg:col-span-2 flex flex-col h-full">
                    <div className="bg-gray-800/50 backdrop-blur-sm p-2 rounded-t-lg border-b-0 border border-gray-700 flex items-center gap-2">
                        <div className="flex items-center gap-1 border-r border-gray-600 pr-2">
                            <ViewButton type="scatter" icon={<ScatterIcon className="w-5 h-5"/>} label="Gráfico de Dispersión"/>
                            <ViewButton type="radar" icon={<RadarIcon className="w-5 h-5"/>} label="Gráfico de Radar"/>
                            <ViewButton type="pie" icon={<PieChartIcon className="w-5 h-5"/>} label="Gráfico Circular"/>
                            <ViewButton type="profile" icon={<ProfileIcon className="w-5 h-5"/>} label="Perfil de Clústeres"/>
                            <ViewButton type="bar" icon={<BarChartIcon className="w-5 h-5"/>} label="Gráfico de Barras"/>
                            {clusterResults.elbowData && <ViewButton type="elbow" icon={<LineChartIcon className="w-5 h-5"/>} label="Método del Codo"/>}
                        </div>
                        <div className="flex-grow flex items-center text-slate-300">{renderControls()}</div>
                    </div>
                    <div className="flex-grow bg-gray-800/50 backdrop-blur-sm rounded-b-lg border border-t-0 border-gray-700" ref={chartContainerRef}>
                        {renderCurrentView()}
                    </div>
                </div>

                <div className="flex flex-col gap-6 overflow-y-auto">
                    {clusterResults.contingencyTable && (
                        <div className="bg-gray-800/50 backdrop-blur-sm p-4 rounded-lg border border-gray-700">
                             <h3 className="text-lg font-semibold mb-2 text-white">Métricas de Evaluación</h3>
                             <div className="grid grid-cols-2 gap-4 mb-4">
                                <MetricCard title="Silhouette Score" value={clusterResults.silhouetteScore?.toFixed(3) ?? 'N/A'} helpText="Mide la separación de clústeres. (+1 es mejor, -1 es peor)"/>
                                <MetricCard title="Adjusted Rand Index" value={clusterResults.adjustedRandIndex?.toFixed(3) ?? 'N/A'} helpText="Similitud con etiquetas reales. (+1 es perfecto)"/>
                             </div>
                             <h4 className="font-semibold mb-2 text-slate-300">Tabla de Contingencia</h4>
                             <ContingencyTable table={clusterResults.contingencyTable} />
                        </div>
                    )}
                    <div className="bg-gray-800/50 backdrop-blur-sm p-4 rounded-lg border border-gray-700 flex flex-col flex-grow">
                        <h3 className="text-lg font-semibold mb-4 text-white flex items-center"><SparklesIcon className="w-5 h-5 mr-2 text-yellow-400" />Análisis con IA</h3>
                        {isGeminiLoading ? (
                            <div className="flex-grow flex items-center justify-center text-slate-500">
                                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                <span>Analizando resultados...</span>
                            </div>
                        ) : (
                            <div className="prose prose-sm prose-invert max-w-none prose-p:text-slate-300 prose-headings:text-slate-200 prose-strong:text-yellow-300 prose-a:text-cyan-400 overflow-y-auto" dangerouslySetInnerHTML={{ __html: geminiAnalysis }} />
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};