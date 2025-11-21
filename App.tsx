import React, { useReducer, useState } from 'react';
import { initialState, reducer } from './reducer';
import { ToastMessage } from './components/Toast';
import { ChatView } from './components/ChatView';
import { DataSourceModal } from './components/DataSourceModal';
import { CodeViewerModal } from './components/CodeViewerModal';
import { VisualAnalyticsBoard } from './components/VisualAnalyticsBoard'; // Importar PVA
import { PromptTraceModal } from './features/prompt-trace/PromptTraceModal';
import { CodeIcon, ChartIcon } from './components/icons'; // Importar ChartIcon

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

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
        // @TODO: Backend endpoint for task polling (/api/v1/etl/status/{taskId}) does not exist.
        // Temporarily disabled to prevent runtime errors.
        console.warn("pollTaskStatus is disabled due to a missing backend endpoint.");
    };

    const fetchAndSetDataHealthReport = async (data: any[], fileName: string) => {
        try {
            const response = await fetch(`${API_BASE_URL}/mpa/quality/report`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ data }),
            });
            if (!response.ok) throw new Error('No se pudo generar el informe de salud de los datos.');

            const healthReport = await response.json();

            // Aquí asumimos que el reducer puede manejar esta nueva acción
            dispatch({ type: 'SET_DATA_HEALTH_REPORT', payload: { healthReport } });
            addToast(`Informe de salud generado para '${fileName}'. Puntuación: ${healthReport.health_score}`, 'info');

        } catch (error) {
            addToast(`Error al generar el informe de salud: ${(error as Error).message}`, 'error');
        }
    };

    const handleExcelFileLoad = async (file: File) => {
        // Refactorizado para usar el manejador de carga de archivos unificado y correcto.
        await handleFileLoad(file);
    };

    const handleMongoDbConnect = async (uri: string, db: string, collection: string) => {
        // @TODO: Backend endpoint for MongoDB connection (/load-from-mongodb/) does not exist.
        // Temporarily disabled to prevent runtime errors.
        addToast("La conexión a MongoDB no está disponible actualmente.", "info");
    };

    const handleS3Connect = async (bucket: string, key: string) => {
        // @TODO: Backend endpoint for S3 connection (/load-from-s3/) does not exist.
        // Temporarily disabled to prevent runtime errors.
        addToast("La conexión a S3 no está disponible actualmente.", "info");
    };

    const handleSheetSelection = async (sheetName: string, file: File | null) => {
        // La nueva lógica de backend maneja la selección de hojas automáticamente.
        // Simplemente pasamos el archivo al manejador de carga principal.
        if (!file) return;
        setSheetModalState({ isOpen: false, file: null, sheetNames: [] });
        await handleFileLoad(file);
    };

    const handleFileLoad = async (file: File) => {
        dispatch({ type: 'SET_LOADING', payload: { isLoading: true, message: 'Cargando archivo...' } });
        const formData = new FormData();
        formData.append('file', file); // Ensure the key is 'file'
        try {
            // Corrected endpoint
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

    const handleUserMessage = async (message: string): Promise<any> => {
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
            const response = await fetch(`${API_BASE_URL}/api/v1/chat/agent/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    data: state.processedData,
                    llm_preference: llmPreference
                }),
            });
            if (!response.ok) throw new Error((await response.json()).detail);
            const agentResponse = await response.json();

            if (agentResponse.output) {
                // Forzar actualización del panel después de una ejecución
                setCurrentView('dashboard');
            }

            return agentResponse;
        } catch (error) {
            console.error("Error del Agente:", error);
            throw error;
        }
    };

    const handleMultiFileLoad = async (files: FileList) => {
        // @TODO: Backend endpoint for multi-file upload (/upload/multi) does not exist.
        // Temporarily disabled to prevent runtime errors.
        addToast("La carga de múltiples archivos no está disponible actualmente.", "info");
    };

    return (
        <div className="bg-gray-900 text-slate-200 h-screen font-sans flex flex-col">
            {sheetModalState.isOpen && ( <SheetSelectionModal sheetNames={sheetModalState.sheetNames} onSelectSheet={(sheetName) => handleSheetSelection(sheetName, sheetModalState.file)} onClose={() => setSheetModalState({ isOpen: false, file: null, sheetNames: [] })} /> )}
            {isDataSourceModalOpen && ( <DataSourceModal onFileLoad={(file) => { handleFileLoad(file); setIsDataSourceModalOpen(false); }} onMultiFileLoad={(files) => { handleMultiFileLoad(files); setIsDataSourceModalOpen(false); }} onExcelFileLoad={(file) => { handleExcelFileLoad(file); setIsDataSourceModalOpen(false); }} onDbConnect={(uri, query) => { handleDbConnect(uri, query); setIsDataSourceModalOpen(false); }} onMongoDbConnect={(uri, db, collection) => { handleMongoDbConnect(uri, db, collection); setIsDataSourceModalOpen(false); }} onS3Connect={(bucket, key) => { handleS3Connect(bucket, key); setIsDataSourceModalOpen(false); }} onClose={() => setIsDataSourceModalOpen(false)} /> )}
            {isCodeViewerModalOpen && ( <CodeViewerModal onClose={() => setIsCodeViewerModalOpen(false)} /> )}
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
                    <ChatView onSendMessage={handleUserMessage} />
                ) : (
                    <VisualAnalyticsBoard />
                )}
            </main>
            <ToastContainer toasts={toasts} onDismiss={dismissToast} />
        </div>
    );
};

export default App;
