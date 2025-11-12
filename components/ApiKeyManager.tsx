// components/ApiKeyManager.tsx
import React from 'react';
import { CheckCircleIcon, XCircleIcon } from './icons';

// Note: The global declaration for window.aistudio was removed from this file
// to prevent conflicts with the declaration in App.tsx.

interface ApiKeyManagerProps {
  isKeyReady: boolean;
  setIsKeyReady: (isReady: boolean) => void;
}

export const ApiKeyManager: React.FC<ApiKeyManagerProps> = ({ isKeyReady, setIsKeyReady }) => {

  const handleSelectKey = async () => {
    if (window.aistudio) {
      try {
        await window.aistudio.openSelectKey();
        // Optimistically set the key as ready. The next API call will validate it.
        setIsKeyReady(true); 
      } catch (error) {
        console.error("Error opening API key selection:", error);
      }
    } else {
        console.warn("window.aistudio is not available.");
    }
  };

  return (
    <div className={`p-3 rounded-lg border ${isKeyReady ? 'bg-emerald-900/50 border-emerald-500/30' : 'bg-rose-900/50 border-rose-500/30'}`}>
        <div className="flex items-center">
            {isKeyReady ? (
                <CheckCircleIcon className="w-5 h-5 text-emerald-400 mr-2 flex-shrink-0" />
            ) : (
                <XCircleIcon className="w-5 h-5 text-rose-400 mr-2 flex-shrink-0" />
            )}
            <h4 className="text-sm font-semibold text-white">Clave API de Gemini</h4>
        </div>
        <p className="text-xs text-slate-400 mt-2">
            Las funciones de análisis con IA requieren una Clave API de Gemini. 
            <a href="https://ai.google.dev/gemini-api/docs/billing" target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:underline ml-1">
                Verifica la facturación.
            </a>
        </p>
        {!isKeyReady && (
            <button
                onClick={handleSelectKey}
                className="w-full mt-3 bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-1.5 px-3 rounded text-sm transition-colors"
            >
                Seleccionar Clave API
            </button>
        )}
    </div>
  );
};
