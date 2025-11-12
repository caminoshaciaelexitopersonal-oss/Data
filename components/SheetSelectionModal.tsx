
import React from 'react';

interface SheetSelectionModalProps {
  sheetNames: string[];
  onSelect: (sheetName: string) => void;
  onCancel: () => void;
  fileName: string;
}

export const SheetSelectionModal: React.FC<SheetSelectionModalProps> = ({ sheetNames, onSelect, onCancel, fileName }) => {
  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center animate-fade-in">
      <div className="bg-gray-800 rounded-lg shadow-xl p-6 border border-gray-700 w-full max-w-md">
        <h2 className="text-xl font-bold text-white mb-2">Seleccionar Hoja de Cálculo</h2>
        <p className="text-slate-400 mb-4">El archivo <strong className="text-cyan-300">{fileName}</strong> contiene múltiples hojas. Por favor, selecciona cuál quieres analizar.</p>
        
        <div className="max-h-60 overflow-y-auto pr-2">
            <ul className="space-y-2">
            {sheetNames.map(name => (
                <li key={name}>
                <button
                    onClick={() => onSelect(name)}
                    className="w-full text-left p-3 rounded-md bg-gray-700 hover:bg-cyan-500/20 hover:text-cyan-300 transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500"
                >
                    {name}
                </button>
                </li>
            ))}
            </ul>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={onCancel}
            className="px-4 py-2 rounded-md text-slate-300 bg-gray-600 hover:bg-gray-500 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400"
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
};
