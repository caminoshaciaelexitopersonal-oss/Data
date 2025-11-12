import React, { useReducer, useState } from 'react';
import { initialState, reducer } from './reducer';
import { Notification } from './types';
import { ChatView } from './components/ChatView';
import { DataSourceModal } from './components/DataSourceModal';
import { analyzeDataQuality, detectOutliers } from './services/dataService';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const App: React.FC = () => {
    const [state, dispatch] = useReducer(reducer, initialState);
    const [isDataSourceModalOpen, setIsDataSourceModalOpen] = useState(false);
    const [notifications, setNotifications] = useState<Notification[]>([]);

    const addNotification = (message: string, type: 'success' | 'error' | 'info') => {
        // (lógica de notificación)
    };

    const handleFileLoad = async (file: File) => {
        dispatch({ type: 'SET_LOADING', payload: { isLoading: true, message: 'Cargando archivo...' } });
        const formData = new FormData();
        formData.append('file', file);
        try {
            const response = await fetch(`${API_BASE_URL}/upload-data/`, { method: 'POST', body: formData });
            if (!response.ok) throw new Error((await response.json()).detail);
            
            const { filename, data } = await response.json();
            const qualityReport = analyzeDataQuality(data);
            const outlierReport = detectOutliers(data, qualityReport);

            dispatch({ type: 'SET_DATA_LOADED', payload: { data, originalData: data, fileName: filename, qualityReport, outlierReport } });
            addNotification(`Archivo '${filename}' cargado.`, 'success');
            return `Archivo ${filename} cargado con ${data.length} filas.`;
        } catch (error) {
            addNotification(`Error al cargar archivo: ${(error as Error).message}`, 'error');
            throw error;
        } finally {
            dispatch({ type: 'SET_LOADING', payload: { isLoading: false } });
        }
    };

    const handleDbConnect = async (uri: string, query: string) => {
        dispatch({ type: 'SET_LOADING', payload: { isLoading: true, message: 'Conectando a la base de datos...' } });
        try {
            const response = await fetch(`${API_BASE_URL}/load-from-db/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ db_uri: uri, query }),
            });
            if (!response.ok) throw new Error((await response.json()).detail);

            const { data } = await response.json();
            const qualityReport = analyzeDataQuality(data);
            const outlierReport = detectOutliers(data, qualityReport);

            dispatch({ type: 'SET_DATA_LOADED', payload: { data, originalData: data, fileName: `Query: ${query.substring(0, 30)}...`, qualityReport, outlierReport } });
            addNotification(`Datos cargados desde la base de datos.`, 'success');
            return `Datos cargados desde la base de datos con ${data.length} filas.`;
        } catch (error) {
            addNotification(`Error de base de datos: ${(error as Error).message}`, 'error');
            throw error;
        } finally {
            dispatch({ type: 'SET_LOADING', payload: { isLoading: false } });
        }
    };

    const handleUserMessage = async (message: string): Promise<any> => {
        if (message.toLowerCase().includes("carga") || message.toLowerCase().includes("sube")) {
            setIsDataSourceModalOpen(true);
            return { output: "Claro, por favor selecciona una fuente de datos." };
        }
        if (!state.processedData || state.processedData.length === 0) {
            throw new Error("No hay datos cargados. Por favor, carga un archivo o conéctate a una base de datos primero.");
        }
        try {
            const response = await fetch(`${API_BASE_URL}/chat/agent/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message, data: state.processedData }),
            });
            if (!response.ok) throw new Error((await response.json()).detail);

            const agentResponse = await response.json();

            if (agentResponse.output && typeof agentResponse.output === 'object' && agentResponse.output.assignments) {
                dispatch({ type: 'SET_CLUSTER_RESULTS', payload: agentResponse.output });
            }
             if (agentResponse.output && typeof agentResponse.output === 'object' && agentResponse.output.rSquared) {
                dispatch({ type: 'SET_REGRESSION_RESULTS', payload: agentResponse.output });
            }

            return agentResponse;
        } catch (error) {
            console.error("Agent Handler Error:", error);
            throw error;
        }
    };

    return (
        <div className="bg-gray-900 text-slate-200 h-screen font-sans">
             {isDataSourceModalOpen && (
                <DataSourceModal
                    onFileLoad={(file) => {
                        handleFileLoad(file);
                        setIsDataSourceModalOpen(false);
                    }}
                    onDbConnect={(uri, query) => {
                        handleDbConnect(uri, query);
                        setIsDataSourceModalOpen(false);
                    }}
                    onClose={() => setIsDataSourceModalOpen(false)}
                />
            )}
            <ChatView onSendMessage={handleUserMessage} />
        </div>
    );
};

export default App;
