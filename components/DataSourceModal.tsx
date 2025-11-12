import React, { useState } from 'react';
import { UploadIcon, DatabaseIcon, XIcon } from './icons';

interface DataSourceModalProps {
    onFileLoad: (file: File) => void;
    onDbConnect: (uri: string, query: string) => void;
    onClose: () => void;
}

export const DataSourceModal: React.FC<DataSourceModalProps> = ({ onFileLoad, onDbConnect, onClose }) => {
    const [sourceType, setSourceType] = useState<'file' | 'db' | null>(null);
    const [dbUri, setDbUri] = useState('');
    const [dbQuery, setDbQuery] = useState('SELECT * FROM your_table LIMIT 100;');
    const fileInputRef = React.useRef<HTMLInputElement>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            onFileLoad(file);
            onClose();
        }
    };

    const handleDbSubmit = () => {
        if (dbUri && dbQuery) {
            onDbConnect(dbUri, dbQuery);
            onClose();
        }
    };

    return (
        <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center">
            <div className="bg-gray-800 rounded-lg shadow-xl p-6 w-full max-w-lg border border-gray-700">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold text-white">Seleccionar Origen de Datos</h2>
                    <button onClick={onClose} className="text-gray-400 hover:text-white">
                        <XIcon className="w-6 h-6" />
                    </button>
                </div>

                {!sourceType ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <button onClick={() => fileInputRef.current?.click()} className="flex flex-col items-center justify-center p-8 bg-gray-700/50 hover:bg-cyan-500/20 rounded-lg transition-colors border border-gray-600 hover:border-cyan-500">
                            <UploadIcon className="w-12 h-12 mb-3 text-cyan-400" />
                            <span className="text-lg font-semibold text-white">Cargar Archivo</span>
                            <span className="text-xs text-slate-400">CSV, Excel, JSON</span>
                        </button>
                        <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" />

                        <button onClick={() => setSourceType('db')} className="flex flex-col items-center justify-center p-8 bg-gray-700/50 hover:bg-purple-500/20 rounded-lg transition-colors border border-gray-600 hover:border-purple-500">
                            <DatabaseIcon className="w-12 h-12 mb-3 text-purple-400" />
                            <span className="text-lg font-semibold text-white">Base de Datos</span>
                            <span className="text-xs text-slate-400">PostgreSQL, MySQL, etc.</span>
                        </button>
                    </div>
                ) : (
                    <div>
                        <button onClick={() => setSourceType(null)} className="text-sm text-cyan-400 mb-4 hover:underline">← Volver</button>
                        <div className="space-y-4">
                            <div>
                                <label className="text-sm text-slate-300 block mb-1">URI de Conexión (SQLAlchemy)</label>
                                <input
                                    type="text"
                                    value={dbUri}
                                    onChange={(e) => setDbUri(e.target.value)}
                                    placeholder="postgresql://user:pass@host/db"
                                    className="w-full bg-gray-900 border border-gray-600 rounded p-2 text-sm"
                                />
                            </div>
                            <div>
                                <label className="text-sm text-slate-300 block mb-1">Consulta SQL</label>
                                <textarea
                                    value={dbQuery}
                                    onChange={(e) => setDbQuery(e.target.value)}
                                    rows={4}
                                    className="w-full bg-gray-900 border border-gray-600 rounded p-2 text-sm font-mono"
                                />
                            </div>
                            <button onClick={handleDbSubmit} className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 rounded">
                                Conectar y Cargar Datos
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
