import React, { useEffect, useState } from "react";
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell
} from "recharts";
import { motion } from "framer-motion";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Tooltip personalizado en español
const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-white p-3 border rounded-xl shadow-lg">
                <p className="font-semibold text-gray-800">{label}</p>
                {payload.map((p: any, i: number) => (
                    <p key={i} className="text-sm text-gray-700">
                        {p.name}: <span className="font-bold">{p.value}</span>
                    </p>
                ))}
            </div>
        );
    }
    return null;
};

export const VisualAnalyticsBoard: React.FC = () => {
    const [data, setData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/api/visualizations`);
                if (!response.ok) {
                    throw new Error("No se pudieron cargar las visualizaciones.");
                }
                const data = await response.json();
                setData(data);
            } catch (err) {
                setError((err as Error).message);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) return <p className="p-8 text-white">Cargando visualizaciones...</p>;
    if (error) return <p className="p-8 text-red-400">Error: {error}</p>;
    if (!data) return <p className="p-8 text-white">No hay datos de visualización disponibles. Ejecuta un análisis para ver los gráficos.</p>;

    return (
        <div className="p-8 space-y-10 bg-gray-900 text-white min-h-full overflow-y-auto">
            <h1 className="text-3xl font-bold">
                Panel de Visualización Analítica
            </h1>
            <p className="text-slate-300">
                Interfaz interactiva con visualizaciones dinámicas. Pasa el cursor sobre los gráficos para ver los valores exactos.
            </p>

            {data.etl_summary && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                    <div className="bg-gray-800 p-6 rounded-2xl shadow-lg">
                        <h2 className="text-xl font-semibold mb-4">📊 Limpieza y Distribución de Datos (ETL)</h2>
                        <BarChart width={650} height={300} data={data.etl_summary}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="feature" />
                            <YAxis />
                            <Tooltip content={<CustomTooltip />} />
                            <Legend />
                            <Bar dataKey="mean" fill="#2563eb" name="Promedio" />
                            <Bar dataKey="std" fill="#f59e0b" name="Desviación" />
                        </BarChart>
                    </div>
                </motion.div>
            )}

            {data.kmeans_clusters && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                    <div className="bg-gray-800 p-6 rounded-2xl shadow-lg">
                        <h2 className="text-xl font-semibold mb-4">🤖 Agrupamiento K-Means</h2>
                        <PieChart width={400} height={300}>
                            <Pie
                                data={data.kmeans_clusters}
                                dataKey="count"
                                nameKey="cluster"
                                cx="50%"
                                cy="50%"
                                outerRadius={100}
                                label={({ cluster, count }: any) => `${cluster}: ${count}`}
                            >
                                {data.kmeans_clusters.map((entry: any, index: number) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                            <Tooltip content={<CustomTooltip />} />
                        </PieChart>
                    </div>
                </motion.div>
            )}

            {data.classification_accuracy && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                    <div className="bg-gray-800 p-6 rounded-2xl shadow-lg">
                        <h2 className="text-xl font-semibold mb-4">🧬 Clasificación (Naive Bayes)</h2>
                        <BarChart width={650} height={300} data={data.classification_accuracy}>
                             <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="modelo" />
                            <YAxis domain={[0, 1]} />
                            <Tooltip content={<CustomTooltip />} />
                            <Legend />
                            <Bar dataKey="accuracy" fill="#22c55e" name="Precisión" />
                        </BarChart>
                    </div>
                </motion.div>
            )}

            {data.regression_plot && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                    <div className="bg-gray-800 p-6 rounded-2xl shadow-lg">
                        <h2 className="text-xl font-semibold mb-4">📉 Modelo de Regresión</h2>
                        <LineChart width={650} height={300} data={data.regression_plot}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="x" name="Observación" />
                            <YAxis />
                            <Tooltip content={<CustomTooltip />} />
                            <Legend />
                            <Line type="monotone" dataKey="y_real" stroke="#f43f5e" name="Valor Real" dot={false} />
                            <Line type="monotone" dataKey="y_pred" stroke="#3b82f6" name="Predicción" dot={false} />
                        </LineChart>
                    </div>
                </motion.div>
            )}

            <div className="text-center mt-10 flex justify-center gap-4">
                <a
                    href={`${API_BASE_URL}/download-report`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                    📥 Descargar Informe (.docx)
                </a>
                <button onClick={() => window.print()} className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700">
                    🖨️ Exportar Dashboard (PDF/Imprimir)
                </button>
            </div>
        </div>
    );
};
