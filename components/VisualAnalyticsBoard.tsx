import React, { useEffect, useState } from "react";
import {
    LineChart, Line, BarChart, Bar, ScatterChart, Scatter,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell, ResponsiveContainer
} from "recharts";
import { motion } from "framer-motion";
import { useDashboardStore } from "../store/dashboardStore"; // Ajusta la ruta si es necesario

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-white p-3 border rounded-xl shadow-lg text-gray-800">
                <p className="font-semibold">{label}</p>
                {payload.map((p: any, i: number) => (
                    <p key={i} className="text-sm">{p.name}: <span className="font-bold">{p.value}</span></p>
                ))}
            </div>
        );
    }
    return null;
};

// --- Componentes de Gráficos Individuales ---
const renderChart = (type: string, data: any) => {
    switch(type) {
        case 'etl_summary':
            return <BarChart data={data}><CartesianGrid /><XAxis dataKey="feature" /><YAxis /><Tooltip content={<CustomTooltip />} /><Legend /><Bar dataKey="mean" fill="#2563eb" name="Promedio" /><Bar dataKey="std" fill="#f59e0b" name="Desviación" /></BarChart>;
        case 'kmeans_clusters':
            return <PieChart><Pie data={data} dataKey="count" nameKey="cluster" cx="50%" cy="50%" outerRadius={100} label>{data.map((e:any, i:number) => <Cell key={`cell-${i}`} fill={e.color} />)}</Pie><Tooltip content={<CustomTooltip />} /></PieChart>;
        case 'classification_accuracy':
            return <BarChart data={data}><CartesianGrid /><XAxis dataKey="modelo" /><YAxis domain={[0, 1]} /><Tooltip content={<CustomTooltip />} /><Legend /><Bar dataKey="accuracy" fill="#22c55e" name="Precisión" /></BarChart>;
        case 'regression_plot':
            return <LineChart data={data}><CartesianGrid /><XAxis dataKey="x" name="Observación" /><YAxis /><Tooltip content={<CustomTooltip />} /><Legend /><Line type="monotone" dataKey="y_real" stroke="#f43f5e" name="Valor Real" dot={false} /><Line type="monotone" dataKey="y_pred" stroke="#3b82f6" name="Predicción" dot={false} /></LineChart>;
        case 'pca_explained_variance':
            return <LineChart data={data.map((v:number, i:number) => ({component: i+1, cumulative_variance: v}))}><CartesianGrid /><XAxis dataKey="component" name="Componente" /><YAxis /><Tooltip content={<CustomTooltip />} /><Legend /><Line type="monotone" dataKey="cumulative_variance" stroke="#8b5cf6" name="Varianza Acumulada" /></LineChart>;
        default:
            return <p>Tipo de gráfico desconocido: {type}</p>;
    }
};


export const VisualAnalyticsBoard: React.FC = () => {
    const { visualizations, loading, error, selectedCharts, fetchVisualizations, toggleChartSelection } = useDashboardStore();

    useEffect(() => {
        fetchVisualizations();
    }, [fetchVisualizations]);

    if (loading) return <p className="p-8 text-white">Cargando visualizaciones...</p>;
    if (error) return <p className="p-8 text-red-400">Error: {error}</p>;
    if (!visualizations || Object.keys(visualizations).length === 0) return <p className="p-8 text-white">No hay datos de visualización disponibles.</p>;

    const availableCharts = Object.keys(visualizations);

    return (
        <div className="p-8 space-y-10 bg-gray-900 text-white min-h-full overflow-y-auto">
            <header>
                <h1 className="text-3xl font-bold">Panel de Visualización Avanzado</h1>
                <p className="text-slate-300">Seleccione las visualizaciones que desea mostrar en el panel.</p>
            </header>

            {/* --- Selector de Gráficos --- */}
            <div className="bg-gray-800 p-4 rounded-xl shadow-lg">
                <h2 className="text-lg font-semibold mb-3">Selector de Gráficos</h2>
                <div className="flex flex-wrap gap-3">
                    {availableCharts.map(chartKey => (
                        <button
                            key={chartKey}
                            onClick={() => toggleChartSelection(chartKey)}
                            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                                selectedCharts.includes(chartKey)
                                    ? 'bg-cyan-500 text-white'
                                    : 'bg-gray-700 hover:bg-gray-600 text-slate-200'
                            }`}
                        >
                            {chartKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </button>
                    ))}
                </div>
            </div>

            {/* --- Renderización de Gráficos Seleccionados --- */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {selectedCharts.map(chartKey => (
                    <motion.div key={chartKey} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
                        <div className="bg-gray-800 p-6 rounded-2xl shadow-lg h-[450px]">
                            <h2 className="text-xl font-semibold mb-4 capitalize">{chartKey.replace(/_/g, ' ')}</h2>
                            <ResponsiveContainer width="100%" height="90%">
                                {renderChart(chartKey, (visualizations as any)[chartKey])}
                            </ResponsiveContainer>
                        </div>
                    </motion.div>
                ))}
                 {selectedCharts.length === 0 && (
                    <p className="text-slate-400 col-span-full text-center">Seleccione al menos un gráfico para visualizar.</p>
                )}
            </div>

            {/* --- Botones de Acción --- */}
            <div className="text-center mt-10 flex justify-center gap-4">
                 <a href={`${API_BASE_URL}/download-report?format=docx`} className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">Descargar Informe (.docx)</a>
                 <a href={`${API_BASE_URL}/download-report?format=pdf`} className="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700">Descargar Informe (.pdf)</a>
            </div>
        </div>
    );
};
