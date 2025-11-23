import React, { useReducer, useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { initialState, reducer } from './reducer';
import { ToastMessage } from './components/Toast';
import { ChatView } from './components/ChatView';
import { DataSourceModal } from './components/DataSourceModal';
import { CodeViewerModal } from './components/CodeViewerModal';
import { VisualAnalyticsBoard } from './components/VisualAnalyticsBoard';
import { PromptTraceModal } from './features/prompt-trace/PromptTraceModal';
import { CodeIcon, ChartIcon } from './components/icons';
import { QualityReportPayloadSchema, ChatAgentPayloadSchema } from '@/frontend/src/validation/apiSchemas';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000") + "/compat/v1";

const SheetSelectionModal: React.FC<{
    sheetNames: string[];
    onSelectSheet: (sheetName: string) => void;
    onClose: () => void;
}> = ({ sheetNames, onSelectSheet, onClose }) => (
    <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center">
        <div className="bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-md border border-gray-700">
            <h2 className="text-xl font-bold text-white mb-4">Seleccionar Hoja de Cálculo</h2>
            <p className="text-slate-400 mb-4">El archivo Excel contiene múltiples hojas. Por favor, selecciona una para cargar.</p>
            <div className="space-y-2">
                {sheetNames.map(name => (
                    <button
                        key={name}
                        onClick={() => onSelectSheet(name)}
                        className="w-full text-left p-3 bg-gray-700 hover:bg-cyan-600 rounded-md transition-colors"
                    >
                        {name}
                    </button>
                ))}
            </div>
            <button onClick={onClose} className="mt-4 text-sm text-slate-400 hover:underline">Cancelar</button>
        </div>
    </div>
);

import { ToastContainer } from './components/Toast';

const App: React.FC = () => {
    const [state, dispatch] = useReducer(reducer, initialState);
    const [isDataSourceModalOpen, setIsDataSourceModalOpen] = useState(false);
    const [isCodeViewerModalOpen, setIsCodeViewerModalOpen] = useState(false);
    const [isPromptTraceModalOpen, setIsPromptTraceModalOpen] = useState(false);
    const [currentView, setCurrentView] = useState<'chat' | 'dashboard'>('chat');
    const [toasts, setToasts] = useState<ToastMessage[]>([]);
    const [llmPreference, setLlmPreference] = useState<'gemini' | 'openai' | 'ollama'>('gemini');
    const [sessionId, setSessionId] = useState('');

    useEffect(() => {
        setSessionId(uuidv4());
    }, []);

    const [sheetModalState, setSheetModalState] = useState<{ isOpen: boolean; file: File | null; sheetNames: string[] }>({
        isOpen: false,
        file: null,
        sheetNames: [],
    });

    const addToast = (message: string, type: 'success' | 'error' | 'info') => {
        const newToast: ToastMessage = {
            id: Date.now(),
            message,
            type,
        };
        setToasts(prevToasts => [...prevToasts, newToast]);
    };

    const dismissToast = (id: number) => {
        setToasts(prevToasts => prevToasts.filter(toast => toast.id !== id));
    };

    const pollTaskStatus = (taskId: string) => {
        const interval = setInterval(async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/mcp/tasks/${taskId}/status`);
                if (!response.ok) {
                    clearInterval(interval);
                    return;
                }
                const result = await response.json();

                if (result.status === 'SUCCESS') {
                    clearInterval(interval);
                    addToast('El procesamiento de archivos ha finalizado con éxito.', 'success');
                } else if (result.status === 'FAILURE') {
                    clearInterval(interval);
                    addToast(`El procesamiento de archivos ha fallado: ${result.result}`, 'error');
                }
            } catch (error) {
                clearInterval(interval);
                addToast('No se pudo verificar el estado de la tarea.', 'error');
            }
        }, 5000);
    };

    const fetchAndSetDataHealthReport = async (data: any[], fileName: string) => {
        try {
            QualityReportPayloadSchema.parse(data);
            const response = await fetch(`${API_BASE_URL}/mpa/quality/report`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            if (!response.ok) throw new Error('No se pudo generar el informe de salud de los datos.');

            const healthReport = await response.json();
            dispatch({ type: 'SET_DATA_HEALTH_REPORT', payload: { healthReport } });
            addToast(`Informe de salud generado para '${fileName}'. Puntuación: ${healthReport.health_score}`, 'info');
        } catch (error) {
            addToast(`Error al generar el informe de salud: ${(error as Error).message}`, 'error');
        }
    };

    const handleExcelFileLoad = async (file: File) => {
        await handleFileLoad(file);
    };

    const handleMongoDbConnect = async (uri: string, db: string, collection: string) => {
        dispatch({ type: 'SET_LOADING', payload: { isLoading: true, message: 'Conectando a MongoDB...' } });
        try {
            const response = await fetch(`${API_BASE_URL}/wpa/ingestion/from-mongodb`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mongo_uri: uri, db_name: db, collection_name: collection }),
            });
            if (!response.ok) throw new Error((await response.json()).detail);

            const { data } = await response.json();
            const fileName = `MongoDB: ${db}/${collection}`;
            dispatch({ type: 'SET_DATA_LOADED', payload: { data, originalData: data, fileName, qualityReport: {}, outlierReport: {} } });
            addToast(`Datos cargados desde MongoDB correctamente.`, 'success');
            fetchAndSetDataHealthReport(data, fileName);
        } catch (error) {
            addToast(`Error de conexión con MongoDB: ${(error as Error).message}`, 'error');
        } finally {
            dispatch({ type: 'SET_LOADING', payload: { isLoading: false } });
        }
    };

    const handleS3Connect = async (bucket: string, key: string) => {
        dispatch({ type: 'SET_LOADING', payload: { isLoading: true, message: 'Cargando datos desde S3...' } });
        try {
            const response = await fetch(`${API_BASE_URL}/wpa/ingestion/from-s3`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ bucket_name: bucket, object_key: key }),
            });
            if (!response.ok) throw new Error((await response.json()).detail);

            const { data } = await response.json();
            const fileName = `S3: ${bucket}/${key}`;
            dispatch({ type: 'SET_DATA_LOADED', payload: { data, originalData: data, fileName, qualityReport: {}, outlierReport: {} } });
            addToast(`Datos cargados desde S3 correctamente.`, 'success');
            fetchAndSetDataHealthReport(data, fileName);
        } catch (error) {
            addToast(`Error de conexión con S3: ${(error as Error).message}`, 'error');
        } finally {
            dispatch({ type: 'SET_LOADING', payload: { isLoading: false } });
        }
    };

    const handleSheetSelection = async (sheetName: string, file: File | null) => {
        if (!file) return;
        setSheetModalState({ isOpen: false, file: null, sheetNames: [] });
        await handleFileLoad(file);
    };

    const handleFileLoad = async (file: File) => {
        dispatch({ type: 'SET_LOADING', payload: { isLoading: true, message: 'Cargando archivo...' } });
        const formData = new FormData();
        formData.append('file', file);
        try {
            const response = await fetch(`${API_BASE_URL}/mpa/ingestion/upload-file/`, {
                method: 'POST',
                body: formData
            });
            if (!response.ok) throw new Error((await response.json()).detail);
            
            const { filename, data } = await response.json();
            dispatch({ type: 'SET_DATA_LOADED', payload: { data, originalData: data, fileName: filename, qualityReport: {}, outlierReport: {} } });
            addToast(`Archivo '${filename}' cargado.`, 'success');
            fetchAndSetDataHealthReport(data, filename);
            return `Archivo ${filename} cargado con ${data.length} filas.`;
        } catch (error) {
            addToast(`Error al cargar el archivo: ${(error as Error).message}`, 'error');
            throw error;
        } finally {
            dispatch({ type: 'SET_LOADING', payload: { isLoading: false } });
        }
    };

    const handleDbConnect = async (uri: string, query: string) => {
        dispatch({ type: 'SET_LOADING', payload: { isLoading: true, message: 'Conectando a la base de datos...' } });
        try {
            const response = await fetch(`${API_BASE_URL}/wpa/ingestion/from-db`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ db_uri: uri, query }),
            });
            if (!response.ok) throw new Error((await response.json()).detail);

            const { data } = await response.json();
            const fileName = `Consulta: ${query.substring(0, 30)}...`;
            dispatch({ type: 'SET_DATA_LOADED', payload: { data, originalData: data, fileName, qualityReport: {}, outlierReport: {} } });
            addToast(`Datos cargados desde la base de datos.`, 'success');
            fetchAndSetDataHealthReport(data, fileName);
            return `Datos cargados desde la base de datos con ${data.length} filas.`;
        } catch (error) {
            addToast(`Error de conexión con la base de datos: ${(error as Error).message}`, 'error');
            throw error;
        } finally {
            dispatch({ type: 'SET_LOADING', payload: { isLoading: false } });
        }
    };

    const handleUserMessage = async (message: string, sessionId: string): Promise<any> => {
        const lowerCaseMessage = message.toLowerCase();
        if (lowerCaseMessage.includes("carga") || lowerCaseMessage.includes("sube")) {
            setIsDataSourceModalOpen(true);
            return { output: "Claro, por favor selecciona una fuente de datos." };
        }
        if (lowerCaseMessage.includes("panel") || lowerCaseMessage.includes("dashboard") || lowerCaseMessage.includes("visualización")) {
            setCurrentView('dashboard');
            return { output: "Claro, abriendo el Panel de Visualización Analítica." };
        }
        if (!state.processedData || state.processedData.length === 0) {
            throw new Error("No hay datos cargados. Por favor, carga un archivo o conéctate a una base de datos primero.");
        }
        try {
            const payload = {
                message: message,
                data: state.processedData,
                llm_preference: llmPreference,
                session_id: sessionId
            };
            ChatAgentPayloadSchema.parse(payload);
            const response = await fetch(`${API_BASE_URL}/api/v1/chat/agent/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            if (!response.ok) throw new Error((await response.json()).detail);
            const agentResponse = await response.json();

            if (agentResponse.output) {
                setCurrentView('dashboard');
            }

            return agentResponse;
        } catch (error) {
            console.error("Error del Agente:", error);
            throw error;
        }
    };

    const handleMultiFileLoad = async (files: FileList) => {
        dispatch({ type: 'SET_LOADING', payload: { isLoading: true, message: 'Subiendo archivos...' } });
        const formData = new FormData();
        Array.from(files).forEach(file => {
            formData.append('files', file);
        });

        try {
            const response = await fetch(`${API_BASE_URL}/mpa/ingestion/multi-upload/`, {
                method: 'POST',
                body: formData,
            });
            if (!response.ok) throw new Error((await response.json()).detail);

            const { task_id, message } = await response.json();
            addToast(message, 'info');
            pollTaskStatus(task_id);
        } catch (error) {
            addToast(`Error al subir los archivos: ${(error as Error).message}`, 'error');
        } finally {
            dispatch({ type: 'SET_LOADING', payload: { isLoading: false } });
        }
    };

    return (
        <div className="bg-gray-900 text-slate-200 h-screen font-sans flex flex-col">
            {sheetModalState.isOpen && ( <SheetSelectionModal sheetNames={sheetModalState.sheetNames} onSelectSheet={(sheetName) => handleSheetSelection(sheetName, sheetModalState.file)} onClose={() => setSheetModalState({ isOpen: false, file: null, sheetNames: [] })} /> )}
            {isDataSourceModalOpen && ( <DataSourceModal onFileLoad={(file) => { handleFileLoad(file); setIsDataSourceModalOpen(false); }} onMultiFileLoad={(files) => { handleMultiFileLoad(files); setIsDataSourceModalOpen(false); }} onExcelFileLoad={(file) => { handleExcelFileLoad(file); setIsDataSourceModalOpen(false); }} onDbConnect={(uri, query) => { handleDbConnect(uri, query); setIsDataSourceModalOpen(false); }} onMongoDbConnect={(uri, db, collection) => { handleMongoDbConnect(uri, db, collection); setIsDataSourceModalOpen(false); }} onS3Connect={(bucket, key) => { handleS3Connect(bucket, key); setIsDataSourceModalOpen(false); }} onClose={() => setIsDataSourceModalOpen(false)} /> )}
            {isCodeViewerModalOpen && ( <CodeViewerModal onClose={() => setIsCodeViewerModalOpen(false)} session_id={sessionId} /> )}
            {isPromptTraceModalOpen && ( <PromptTraceModal onClose={() => setIsPromptTraceModalOpen(false)} /> )}

            <header className="p-4 border-b border-gray-700 flex justify-between items-center">
                <h1 className="text-xl font-bold">Sistema de Analítica de Datos Inteligente (SADI)</h1>
                <div className="flex items-center gap-4">
                    <div>
                        <label htmlFor="llm-select" className="text-xs text-slate-400 mr-2">Motor IA:</label>
                        <select
                            id="llm-select"
                            value={llmPreference}
                            onChange={(e) => setLlmPreference(e.target.value as any)}
                            className="bg-gray-700 border border-gray-600 rounded-md text-sm py-1 px-2"
                        >
                            <option value="gemini">Gemini</option>
                            <option value="openai">OpenAI</option>
                            <option value="ollama">Ollama</option>
                        </select>
                    </div>
                    <button
                        onClick={() => setCurrentView(currentView === 'chat' ? 'dashboard' : 'chat')}
                        className="bg-purple-600 text-white flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
                    >
                        <ChartIcon className="w-4 h-4" />
                        {currentView === 'chat' ? 'Ver Panel' : 'Ver Chat'}
                    </button>
                    <button
                        onClick={() => setIsCodeViewerModalOpen(true)}
                        className="bg-blue-600 text-white flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        <CodeIcon className="w-4 h-4" /> Ver Pasos y Código
                    </button>
                    <button
                        onClick={() => setIsPromptTraceModalOpen(true)}
                        className="bg-teal-600 text-white flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-teal-700 transition-colors"
                    >
                        <CodeIcon className="w-4 h-4" /> Ver Trazas de Prompts
                    </button>
                </div>
            </header>

            <main className="flex-1 overflow-y-auto">
                {currentView === 'chat' ? (
                    <ChatView onSendMessage={handleUserMessage} session_id={sessionId} />
                ) : (
                    <VisualAnalyticsBoard />
                )}
            </main>
            <ToastContainer toasts={toasts} onDismiss={dismissToast} />
        </div>
    );
};

export default App;
