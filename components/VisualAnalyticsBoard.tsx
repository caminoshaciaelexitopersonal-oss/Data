import React, { useEffect, useState } from "react";
import {
    LineChart, Line, BarChart, Bar, ScatterChart, Scatter,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell, ResponsiveContainer
} from "recharts";
import { motion } from "framer-motion";
import { Responsive, WidthProvider } from "react-grid-layout";
import html2canvas from 'html2canvas';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import { useDashboardStore } from "../store/dashboardStore"; // Ajusta la ruta si es necesario

const ResponsiveGridLayout = WidthProvider(Responsive);

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
    const dashboardRef = React.useRef<HTMLDivElement>(null);
    const { filteredVisualizations, loading, error, selectedCharts, fetchVisualizations, toggleChartSelection, setFilter } = useDashboardStore();

    const handleDownloadImage = () => {
        if (dashboardRef.current) {
            html2canvas(dashboardRef.current).then(canvas => {
                const link = document.createElement('a');
                link.download = 'sadi_dashboard.png';
                link.href = canvas.toDataURL('image/png');
                link.click();
            });
        }
    };

    useEffect(() => {
        fetchVisualizations();
    }, [fetchVisualizations]);

    if (loading) return <p className="p-8 text-white">Cargando visualizaciones...</p>;
    if (error) return <p className="p-8 text-red-400">Error: {error}</p>;
    if (!filteredVisualizations || Object.keys(filteredVisualizations).length === 0) return <p className="p-8 text-white">No hay datos de visualización disponibles.</p>;

    const availableCharts = Object.keys(filteredVisualizations);

    return (
        <div className="p-8 space-y-10 bg-gray-900 text-white min-h-full overflow-y-auto" ref={dashboardRef}>
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

            {/* --- Panel de Filtros --- */}
            <div className="bg-gray-800 p-4 rounded-xl shadow-lg">
                <h2 className="text-lg font-semibold mb-3">Filtros Globales</h2>
                <div>
                    <label htmlFor="model-filter" className="text-sm text-slate-300">Filtrar por Modelo:</label>
                    <select
                        id="model-filter"
                        onChange={(e) => setFilter('classification_model', e.target.value || null)}
                        className="bg-gray-700 ml-2 rounded p-1 text-sm"
                    >
                        <option value="">Todos</option>
                        {/* Esto debería ser dinámico */}
                        <option value="Random Forest">Random Forest</option>
                        <option value="SVM">SVM</option>
                        <option value="Árbol de Decisión">Árbol de Decisión</option>
                        <option value="Red Neuronal (MLP)">Red Neuronal (MLP)</option>
                    </select>
                </div>
            </div>

            {/* --- Renderización de Gráficos Seleccionados --- */}
            <ResponsiveGridLayout
                className="layout"
                layouts={{ lg: selectedCharts.map((key, i) => ({ i: key, x: (i % 2) * 6, y: Math.floor(i / 2) * 4, w: 6, h: 4 })) }}
                breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
                cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
                rowHeight={100}
            >
                {selectedCharts.map(chartKey => (
                    <div key={chartKey} className="bg-gray-800 p-6 rounded-2xl shadow-lg">
                        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
                            <h2 className="text-xl font-semibold mb-4 capitalize">{chartKey.replace(/_/g, ' ')}</h2>
                            <ResponsiveContainer width="100%" height="90%">
                                {renderChart(chartKey, (filteredVisualizations as any)[chartKey])}
                            </ResponsiveContainer>
                        </motion.div>
                    </div>
                ))}
            </ResponsiveGridLayout>

            {selectedCharts.length === 0 && (
                <p className="text-slate-400 col-span-full text-center py-10">Seleccione al menos un gráfico para visualizar.</p>
            )}

            {/* --- Botones de Acción --- */}
            <div className="text-center mt-10 flex justify-center gap-4">
                 <button onClick={handleDownloadImage} className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700">Descargar como Imagen</button>
                 <a href={`${API_BASE_URL}/export/notebook`} className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700">Descargar Notebook (.ipynb)</a>
                 <a href={`${API_BASE_URL}/download-report?format=docx`} className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">Descargar Informe (.docx)</a>
                 <a href={`${API_BASE_URL}/download-report?format=pdf`} className="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700">Descargar Informe (.pdf)</a>
            </div>
        </div>
    );
};
