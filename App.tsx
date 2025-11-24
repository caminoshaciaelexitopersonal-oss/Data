import React, { useReducer, useState, useEffect } from 'react';
import { initialState, reducer } from './reducer';
import { ToastMessage } from './components/Toast';
import { ChatView } from './components/ChatView';
import { DataSourceModal } from './components/DataSourceModal';
import { CodeViewerModal } from './components/CodeViewerModal';
import { CodeIcon } from './components/icons';
// Import the generated API client
import { DefaultService, QualityReport } from './services/api-client';

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
    const [toasts, setToasts] = useState<ToastMessage[]>([]);
    const [llmPreference, setLlmPreference] = useState<'gemini' | 'openai' | 'ollama'>('gemini');
    const [sessionId, setSessionId] = useState<string | null>(null);

    useEffect(() => {
        const createSession = async () => {
            try {
                // Use the generated client to create a session
                const session = await DefaultService.createSession();
                setSessionId(session.session_id);
                addToast(`Sesión iniciada: ${session.session_id}`, 'info');
            } catch (error) {
                addToast(`Error al iniciar sesión: ${(error as Error).message}`, 'error');
            }
        };
        createSession();
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

    const generateAndSetDataHealthReport = async (sessionId: string, fileName: string) => {
        if (!sessionId) return;
        try {
            // Use the generated client to get the quality report, sending the correct payload
            const healthReport = await DefaultService.getQualityReport({ session_id: sessionId });
            if (healthReport) {
                 dispatch({ type: 'SET_DATA_HEALTH_REPORT', payload: { healthReport: healthReport as QualityReport } });
                 addToast(`Informe de salud generado para '${fileName}'. Puntuación: ${healthReport.health_score}`, 'info');
            } else {
                throw new Error("El informe de salud no pudo ser generado.");
            }
        } catch (error) {
            addToast(`Error al generar el informe de salud: ${(error as Error).message}`, 'error');
        }
    };

    const handleExcelFileLoad = async (file: File) => {
        await handleFileLoad(file);
    };

    const handleSheetSelection = async (sheetName: string, file: File | null) => {
        if (!file) return;
        setSheetModalState({ isOpen: false, file: null, sheetNames: [] });
        await handleFileLoad(file);
    };

    const handleFileLoad = async (file: File) => {
        if (!sessionId) {
            addToast('La sesión no está activa. Por favor, recargue la página.', 'error');
            return;
        }
        dispatch({ type: 'SET_LOADING', payload: { isLoading: true, message: 'Cargando archivo...' } });

        try {
            // Use the generated client. This fixes the incorrect URL path.
            const response = await DefaultService.uploadFile({ session_id: sessionId, file: file });
            dispatch({ type: 'SET_DATA_LOADED', payload: { data: [], originalData: [], fileName: response.filename, qualityReport: {}, outlierReport: {} } });
            addToast(`Archivo '${response.filename}' cargado y asociado a la sesión.`, 'success');

            // Now, get the health report using the session_id
            await generateAndSetDataHealthReport(sessionId, response.filename);

            return `Archivo ${response.filename} cargado.`;
        } catch (error) {
            addToast(`Error al cargar el archivo: ${(error as Error).message}`, 'error');
            throw error;
        } finally {
            dispatch({ type: 'SET_LOADING', payload: { isLoading: false } });
        }
    };

    // NOTE: DB Connect functionality is temporarily disabled as it's not defined in the final OpenAPI contract.
    const handleDbConnect = async (uri: string, query: string) => {
        const message = "La conexión a bases de datos está en desarrollo.";
        addToast(message, 'info');
        return message;
    };

    const handleUserMessage = async (message: string, sessionId: string | null): Promise<any> => {
        if (!sessionId) {
            addToast('La sesión no está activa. Por favor, recargue la página.', 'error');
            return;
        }
        const lowerCaseMessage = message.toLowerCase();
        if (lowerCaseMessage.includes("carga") || lowerCaseMessage.includes("sube")) {
            setIsDataSourceModalOpen(true);
            return { output: "Claro, por favor selecciona una fuente de datos." };
        }
        // DEPRECATED: Dashboard functionality is removed until fixed.
        // if (lowerCaseMessage.includes("panel") || lowerCaseMessage.includes("dashboard") || lowerCaseMessage.includes("visualización")) {
        //     setCurrentView('dashboard');
        //     return { output: "Claro, abriendo el Panel de Visualización Analítica." };
        // }

        if (!state.fileName) {
            throw new Error("No hay datos cargados. Por favor, carga un archivo o conéctate a una base de datos primero.");
        }
        try {
            // Use the generated client, which sends the correct session-based payload.
            const agentResponse = await DefaultService.chatAgent({
                session_id: sessionId,
                message: message
            });

            return agentResponse;
        } catch (error) {
            console.error("Error del Agente:", error);
            throw error;
        }
    };

    return (
        <div className="bg-gray-900 text-slate-200 h-screen font-sans flex flex-col">
            {sheetModalState.isOpen && ( <SheetSelectionModal sheetNames={sheetModalState.sheetNames} onSelectSheet={(sheetName) => handleSheetSelection(sheetName, sheetModalState.file)} onClose={() => setSheetModalState({ isOpen: false, file: null, sheetNames: [] })} /> )}
            {isDataSourceModalOpen && ( <DataSourceModal onFileLoad={(file) => { handleFileLoad(file); setIsDataSourceModalOpen(false); }} onExcelFileLoad={(file) => { handleExcelFileLoad(file); setIsDataSourceModalOpen(false); }} onDbConnect={(uri, query) => { handleDbConnect(uri, query); setIsDataSourceModalOpen(false); }} onClose={() => setIsDataSourceModalOpen(false)} /> )}
            {isCodeViewerModalOpen && ( <CodeViewerModal onClose={() => setIsCodeViewerModalOpen(false)} session_id={sessionId ?? ""} /> )}

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
                        onClick={() => setIsCodeViewerModalOpen(true)}
                        className="bg-blue-600 text-white flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        <CodeIcon className="w-4 h-4" /> Ver Pasos y Código
                    </button>
                </div>
            </header>

            <main className="flex-1 overflow-y-auto">
                <ChatView onSendMessage={handleUserMessage} session_id={sessionId} />
            </main>
            <ToastContainer toasts={toasts} onDismiss={dismissToast} />
        </div>
    );
};

export default App;
