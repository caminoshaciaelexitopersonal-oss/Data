import React, { useState, useEffect } from 'react';
import { Action } from '../types';
import { InfoIcon, SaveIcon } from './icons';
import { marked } from 'marked';

interface DatasetMetadataProps {
  datasetMetadata: string;
  dispatch: React.Dispatch<Action>;
}

export const DatasetMetadata: React.FC<DatasetMetadataProps> = ({ datasetMetadata, dispatch }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(datasetMetadata);
  const [renderedHtml, setRenderedHtml] = useState('');

  useEffect(() => {
    setEditText(datasetMetadata);
    if (datasetMetadata) {
        const parse = async () => {
            const html = await marked.parse(datasetMetadata);
            setRenderedHtml(html);
        }
        parse();
    }
  }, [datasetMetadata]);

  const handleSave = () => {
    dispatch({ type: 'SET_DATASET_METADATA', payload: editText });
    setIsEditing(false);
  };
  
  const handleCancel = () => {
    setEditText(datasetMetadata);
    setIsEditing(false);
  }

  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg border border-gray-700 mb-6">
        <details className="group">
            <summary className="flex justify-between items-center p-4 cursor-pointer list-none">
                 <h3 className="text-lg font-semibold text-white flex items-center">
                    <InfoIcon className="w-5 h-5 mr-3 text-cyan-400" />
                    Metadatos del Dataset
                </h3>
                <span className="text-sm text-cyan-400 group-open:hidden">Mostrar</span>
                <span className="text-sm text-cyan-400 hidden group-open:inline">Ocultar</span>
            </summary>
            <div className="p-4 border-t border-gray-700">
                {!datasetMetadata && !isEditing && (
                    <div className="text-center text-slate-400 text-sm">
                        <p>No se han añadido metadatos para este dataset.</p>
                        <button onClick={() => setIsEditing(true)} className="mt-2 text-cyan-400 hover:underline">
                            + Añadir información
                        </button>
                    </div>
                )}

                {isEditing ? (
                    <div>
                        <textarea
                            value={editText}
                            onChange={(e) => setEditText(e.target.value)}
                            placeholder="Describe el dataset, el significado de las columnas, su origen, etc. Soporta Markdown."
                            className="w-full h-32 p-2 bg-gray-900 border border-gray-600 rounded-md text-slate-300 text-sm focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
                        />
                        <div className="flex justify-end mt-2 space-x-2">
                            <button
                                onClick={handleCancel}
                                className="px-4 py-2 rounded-md text-sm text-slate-300 bg-gray-600 hover:bg-gray-500 transition-colors"
                            >
                                Cancelar
                            </button>
                            <button
                            onClick={handleSave}
                            className="px-4 py-2 rounded-md text-sm text-white font-semibold bg-cyan-600 hover:bg-cyan-700 transition-colors flex items-center"
                            >
                            <SaveIcon className="w-4 h-4 mr-2" />
                            Guardar Metadatos
                            </button>
                        </div>
                    </div>
                ) : (
                    datasetMetadata && (
                        <div>
                             <div 
                                className="prose prose-sm prose-invert max-w-none prose-p:text-slate-300 prose-headings:text-slate-200 prose-strong:text-slate-100"
                                dangerouslySetInnerHTML={{ __html: renderedHtml }} 
                            />
                            <div className="text-right mt-2">
                                <button
                                    onClick={() => setIsEditing(true)}
                                    className="text-sm text-cyan-400 hover:text-cyan-300"
                                >
                                    Editar
                                </button>
                            </div>
                        </div>
                    )
                )}
            </div>
        </details>
    </div>
  );
};