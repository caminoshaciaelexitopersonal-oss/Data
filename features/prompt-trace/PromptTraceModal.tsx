import React, { useEffect, useState } from 'react';
import { useDashboardStore } from '../../store/dashboardStore';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

interface PromptTraceModalProps {
  onClose: () => void;
}

export const PromptTraceModal: React.FC<PromptTraceModalProps> = ({ onClose }) => {
  const [traces, setTraces] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const sessionId = useDashboardStore.getState().sessionId; // Asumiendo que el sessionId está en el store

  useEffect(() => {
    if (!sessionId) {
      setError("No hay una sesión activa para mostrar la trazabilidad.");
      setLoading(false);
      return;
    }

    const fetchTraces = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/prompts/trace/${sessionId}`);
        if (!response.ok) {
          throw new Error('No se pudieron cargar las trazas de prompts.');
        }
        const data = await response.json();
        setTraces(data);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    fetchTraces();
  }, [sessionId]);

  return (
    <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center">
      <div className="bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-2xl border border-gray-700">
        <h2 className="text-xl font-bold text-white mb-4">Trazabilidad de Prompts</h2>
        <div className="max-h-96 overflow-y-auto">
          {loading && <p>Cargando trazas...</p>}
          {error && <p className="text-red-400">{error}</p>}
          {!loading && !error && (
            <div className="space-y-4">
              {traces.map((trace, index) => (
                <div key={index} className="p-4 bg-gray-700 rounded-lg">
                  <p className="text-sm text-gray-400">{new Date(trace.timestamp).toLocaleString()}</p>
                  <p className="font-semibold mt-2">Usuario:</p>
                  <p className="text-cyan-300">{trace.user_prompt}</p>
                  <p className="font-semibold mt-2">Respuesta del Agente:</p>
                  <pre className="text-sm bg-gray-900 p-2 rounded mt-1 overflow-x-auto">
                    {JSON.stringify(trace.agent_response, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          )}
        </div>
        <button onClick={onClose} className="mt-4 text-sm text-cyan-400 hover:underline">
          Cerrar
        </button>
      </div>
    </div>
  );
};
