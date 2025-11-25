import React, { useState, useEffect } from 'react';
import { XIcon } from './icons';

interface Step {
    descripcion: string;
    codigo: string;
}

interface CodeViewerModalProps {
    onClose: () => void;
    session_id: string;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const CodeViewerModal: React.FC<CodeViewerModalProps> = ({ onClose, session_id }) => {
    const [steps, setSteps] = useState<Step[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchSteps = async () => {
            if (!session_id) {
                setError("No se ha proporcionado un ID de sesión.");
                setLoading(false);
                return;
            }
            try {
                const response = await fetch(`${API_BASE_URL}/api/v1/get-steps?session_id=${session_id}`);
                if (!response.ok) {
                    throw new Error('No se pudo obtener los pasos del servidor.');
                }
                const data = await response.json();
                setSteps(data.steps);
            } catch (err) {
                setError((err as Error).message);
            } finally {
                setLoading(false);
            }
        };

        fetchSteps();
    }, [session_id]);

    const handleCopy = (code: string) => {
        navigator.clipboard.writeText(code);
        // Opcional: mostrar una notificación de "Copiado!"
    };

    return (
        <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center">
            <div className="bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-2xl border border-gray-700 max-h-[90vh] flex flex-col">
                <div className="flex justify-between items-center mb-4">
                    <div>
                        <h2 className="text-xl font-bold text-white">Pasos Técnicos y Código Fuente</h2>
                        {steps.length > 0 && (
                            <a
                                href={`${API_BASE_URL}/api/v1/export/code?session_id=${session_id}`}
                                download="sadi_codigo_exportado.zip"
                                className="text-sm text-cyan-400 hover:underline mt-1 inline-block"
                            >
                                Descargar Código Completo (.zip)
                            </a>
                        )}
                    </div>
                    <button onClick={onClose} className="text-gray-400 hover:text-white">
                        <XIcon className="w-6 h-6" />
                    </button>
                </div>
                <div className="overflow-y-auto space-y-4">
                    {loading && <p className="text-slate-300">Cargando pasos...</p>}
                    {error && <p className="text-red-400">Error: {error}</p>}
                    {!loading && !error && steps.length === 0 && (
                        <p className="text-slate-400">Aún no se ha ejecutado ningún paso.</p>
                    )}
                    {steps.map((step, index) => (
                        <div key={index} className="bg-gray-900 rounded-lg p-4">
                            <p className="text-slate-300 mb-2">{step.descripcion}</p>
                            <div className="bg-black text-green-400 text-sm p-4 rounded-md relative">
                                <pre><code>{step.codigo}</code></pre>
                                <button
                                    onClick={() => handleCopy(step.codigo)}
                                    className="absolute top-2 right-2 bg-gray-700 hover:bg-gray-600 text-white text-xs py-1 px-2 rounded"
                                >
                                    Copiar
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};
