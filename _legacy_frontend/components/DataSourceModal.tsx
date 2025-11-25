import React, { useState } from 'react';
import { UploadIcon, DatabaseIcon, XIcon, MongoDbIcon, AwsS3Icon } from './icons';

interface DataSourceModalProps {
    onFileLoad: (file: File) => void;
    onMultiFileLoad: (files: FileList) => void;
    onExcelFileLoad: (file: File) => void;
    onDbConnect: (uri: string, query: string) => void;
    onMongoDbConnect: (uri: string, db: string, collection: string) => void;
    onS3Connect: (bucket: string, key: string) => void;
    onClose: () => void;
}

export const DataSourceModal: React.FC<DataSourceModalProps> = ({ onFileLoad, onExcelFileLoad, onDbConnect, onMongoDbConnect, onS3Connect, onClose }) => {
    const [sourceType, setSourceType] = useState<'file' | 'db' | 'mongodb' | 's3' | null>(null);
    const multiFileInputRef = React.useRef<HTMLInputElement>(null);

    // SQL DB State
    const [dbUri, setDbUri] = useState('');
    const [dbQuery, setDbQuery] = useState('SELECT * FROM tu_tabla LIMIT 100;');

    // MongoDB State
    const [mongoUri, setMongoUri] = useState('');
    const [mongoDbName, setMongoDbName] = useState('');
    const [mongoCollection, setMongoCollection] = useState('');

    // S3 State
    const [s3Bucket, setS3Bucket] = useState('');
    const [s3Key, setS3Key] = useState('');

    // State for validation errors
    const [errors, setErrors] = useState<Record<string, string>>({});

    const fileInputRef = React.useRef<HTMLInputElement>(null);

    const validateAndSubmit = (validator: () => boolean, submitAction: () => void) => {
        if (validator()) {
            submitAction();
            onClose();
        }
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            const extension = file.name.split('.').pop()?.toLowerCase();
            if (extension === 'xlsx' || extension === 'xls') {
                onExcelFileLoad(file);
            } else {
                onFileLoad(file);
            }
        }
    };

    const handleMultiFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (files && files.length > 0) {
            onMultiFileLoad(files);
            onClose();
        }
    };

    const handleDbSubmit = () => {
        validateAndSubmit(
            () => {
                const newErrors: Record<string, string> = {};
                if (!dbUri.trim()) newErrors.dbUri = "La URI de conexión es obligatoria.";
                if (!dbQuery.trim()) newErrors.dbQuery = "La consulta SQL es obligatoria.";
                setErrors(newErrors);
                return Object.keys(newErrors).length === 0;
            },
            () => onDbConnect(dbUri, dbQuery)
        );
    };

    const handleMongoDbSubmit = () => {
        validateAndSubmit(
            () => {
                const newErrors: Record<string, string> = {};
                if (!mongoUri.trim()) newErrors.mongoUri = "La URI de conexión es obligatoria.";
                if (!mongoDbName.trim()) newErrors.mongoDbName = "El nombre de la BD es obligatorio.";
                if (!mongoCollection.trim()) newErrors.mongoCollection = "El nombre de la colección es obligatorio.";
                setErrors(newErrors);
                return Object.keys(newErrors).length === 0;
            },
            () => onMongoDbConnect(mongoUri, mongoDbName, mongoCollection)
        );
    };

    const handleS3Submit = () => {
        validateAndSubmit(
            () => {
                const newErrors: Record<string, string> = {};
                if (!s3Bucket.trim()) newErrors.s3Bucket = "El nombre del bucket es obligatorio.";
                if (!s3Key.trim()) newErrors.s3Key = "La clave del objeto es obligatoria.";
                setErrors(newErrors);
                return Object.keys(newErrors).length === 0;
            },
            () => onS3Connect(s3Bucket, s3Key)
        );
    };

    const renderForm = () => {
        if (sourceType === 'db') {
            const isDbFormInvalid = !dbUri.trim() || !dbQuery.trim();
            return (
                <div className="space-y-4">
                    <div>
                        <label className="text-sm text-slate-300 block mb-1">URI de Conexión (SQLAlchemy)</label>
                        <input type="text" value={dbUri} onChange={(e) => setDbUri(e.target.value)} placeholder="postgresql://usuario:pass@host/db" className={`w-full bg-gray-900 border ${errors.dbUri ? 'border-red-500' : 'border-gray-600'} rounded p-2 text-sm`} />
                        {errors.dbUri && <p className="text-red-500 text-xs mt-1">{errors.dbUri}</p>}
                    </div>
                    <div>
                        <label className="text-sm text-slate-300 block mb-1">Consulta SQL</label>
                        <textarea value={dbQuery} onChange={(e) => setDbQuery(e.target.value)} rows={4} className={`w-full bg-gray-900 border ${errors.dbQuery ? 'border-red-500' : 'border-gray-600'} rounded p-2 text-sm font-mono`} />
                        {errors.dbQuery && <p className="text-red-500 text-xs mt-1">{errors.dbQuery}</p>}
                    </div>
                    <button onClick={handleDbSubmit} disabled={isDbFormInvalid} className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 rounded disabled:opacity-50 disabled:cursor-not-allowed">Conectar y Cargar Datos</button>
                </div>
            );
        }
        if (sourceType === 'mongodb') {
            const isMongoFormInvalid = !mongoUri.trim() || !mongoDbName.trim() || !mongoCollection.trim();
            return (
                <div className="space-y-4">
                    <div>
                        <label className="text-sm text-slate-300 block mb-1">URI de Conexión de MongoDB</label>
                        <input type="text" value={mongoUri} onChange={(e) => setMongoUri(e.target.value)} placeholder="mongodb://usuario:pass@host:port/" className={`w-full bg-gray-900 border ${errors.mongoUri ? 'border-red-500' : 'border-gray-600'} rounded p-2 text-sm`} />
                        {errors.mongoUri && <p className="text-red-500 text-xs mt-1">{errors.mongoUri}</p>}
                    </div>
                    <div>
                        <label className="text-sm text-slate-300 block mb-1">Nombre de la Base de Datos</label>
                        <input type="text" value={mongoDbName} onChange={(e) => setMongoDbName(e.target.value)} placeholder="mi_base_de_datos" className={`w-full bg-gray-900 border ${errors.mongoDbName ? 'border-red-500' : 'border-gray-600'} rounded p-2 text-sm`} />
                        {errors.mongoDbName && <p className="text-red-500 text-xs mt-1">{errors.mongoDbName}</p>}
                    </div>
                    <div>
                        <label className="text-sm text-slate-300 block mb-1">Nombre de la Colección</label>
                        <input type="text" value={mongoCollection} onChange={(e) => setMongoCollection(e.target.value)} placeholder="mi_coleccion" className={`w-full bg-gray-900 border ${errors.mongoCollection ? 'border-red-500' : 'border-gray-600'} rounded p-2 text-sm`} />
                        {errors.mongoCollection && <p className="text-red-500 text-xs mt-1">{errors.mongoCollection}</p>}
                    </div>
                    <button onClick={handleMongoDbSubmit} disabled={isMongoFormInvalid} className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2 rounded disabled:opacity-50 disabled:cursor-not-allowed">Conectar y Cargar Datos</button>
                </div>
            );
        }
        if (sourceType === 's3') {
            const isS3FormInvalid = !s3Bucket.trim() || !s3Key.trim();
            return (
                <div className="space-y-4">
                    <p className="text-xs text-slate-400">Asegúrate de que las credenciales de AWS (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY) están configuradas en el entorno del backend.</p>
                    <div>
                        <label className="text-sm text-slate-300 block mb-1">Nombre del Bucket de S3</label>
                        <input type="text" value={s3Bucket} onChange={(e) => setS3Bucket(e.target.value)} placeholder="mi-bucket-s3" className={`w-full bg-gray-900 border ${errors.s3Bucket ? 'border-red-500' : 'border-gray-600'} rounded p-2 text-sm`} />
                        {errors.s3Bucket && <p className="text-red-500 text-xs mt-1">{errors.s3Bucket}</p>}
                    </div>
                    <div>
                        <label className="text-sm text-slate-300 block mb-1">Clave del Objeto (Ruta del archivo)</label>
                        <input type="text" value={s3Key} onChange={(e) => setS3Key(e.target.value)} placeholder="ruta/a/mi/archivo.csv" className={`w-full bg-gray-900 border ${errors.s3Key ? 'border-red-500' : 'border-gray-600'} rounded p-2 text-sm`} />
                        {errors.s3Key && <p className="text-red-500 text-xs mt-1">{errors.s3Key}</p>}
                    </div>
                    <button onClick={handleS3Submit} disabled={isS3FormInvalid} className="w-full bg-orange-600 hover:bg-orange-700 text-white font-bold py-2 rounded disabled:opacity-50 disabled:cursor-not-allowed">Conectar y Cargar Datos</button>
                </div>
            );
        }
        return null;
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
                    <div className="grid grid-cols-2 md:grid-cols-2 gap-4">
                        <button onClick={() => fileInputRef.current?.click()} className="flex flex-col items-center justify-center p-6 bg-gray-700/50 hover:bg-cyan-500/20 rounded-lg transition-colors border border-gray-600 hover:border-cyan-500">
                            <UploadIcon className="w-10 h-10 mb-2 text-cyan-400" />
                            <span className="text-md font-semibold text-white">Cargar Archivo</span>
                            <span className="text-xs text-slate-400">CSV, Excel, JSON</span>
                        </button>
                        <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" accept=".csv,.xls,.xlsx,.json" />

                        {/* @TODO: Re-enable when backend endpoint /upload/multi is available. */}
                        {/* <button onClick={() => multiFileInputRef.current?.click()} className="flex flex-col items-center justify-center p-6 bg-gray-700/50 hover:bg-teal-500/20 rounded-lg transition-colors border border-gray-600 hover:border-teal-500">
                            <UploadIcon className="w-10 h-10 mb-2 text-teal-400" />
                            <span className="text-md font-semibold text-white">Cargar Múltiples Archivos</span>
                            <span className="text-xs text-slate-400">.zip, .tar.gz</span>
                        </button>
                        <input type="file" multiple ref={multiFileInputRef} onChange={handleMultiFileChange} className="hidden" /> */}

                        <button onClick={() => setSourceType('db')} className="flex flex-col items-center justify-center p-6 bg-gray-700/50 hover:bg-purple-500/20 rounded-lg transition-colors border border-gray-600 hover:border-purple-500">
                            <DatabaseIcon className="w-10 h-10 mb-2 text-purple-400" />
                            <span className="text-md font-semibold text-white">Base de Datos SQL</span>
                            <span className="text-xs text-slate-400">PostgreSQL, etc.</span>
                        </button>

                        {/* @TODO: Re-enable when backend endpoint /load-from-mongodb/ is available. */}
                        {/* <button onClick={() => setSourceType('mongodb')} className="flex flex-col items-center justify-center p-6 bg-gray-700/50 hover:bg-green-500/20 rounded-lg transition-colors border border-gray-600 hover:border-green-500">
                            <MongoDbIcon className="w-10 h-10 mb-2 text-green-400" />
                            <span className="text-md font-semibold text-white">MongoDB</span>
                            <span className="text-xs text-slate-400">Conectar a una colección</span>
                        </button> */}

                        {/* @TODO: Re-enable when backend endpoint /load-from-s3/ is available. */}
                        {/* <button onClick={() => setSourceType('s3')} className="flex flex-col items-center justify-center p-6 bg-gray-700/50 hover:bg-orange-500/20 rounded-lg transition-colors border border-gray-600 hover:border-orange-500">
                            <AwsS3Icon className="w-10 h-10 mb-2 text-orange-400" />
                            <span className="text-md font-semibold text-white">Amazon S3</span>
                            <span className="text-xs text-slate-400">Cargar desde un bucket</span>
                        </button> */}
                    </div>
                ) : (
                    <div>
                        <button onClick={() => setSourceType(null)} className="text-sm text-cyan-400 mb-4 hover:underline">← Volver</button>
                        {renderForm()}
                    </div>
                )}
            </div>
        </div>
    );
};
