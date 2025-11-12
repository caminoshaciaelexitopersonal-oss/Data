import React, { useState, useEffect } from 'react';
import { Action } from '../types';
import { BookOpenIcon, SaveIcon } from './icons';
import { marked } from 'marked';

interface ProblemContextProps {
  problemContext: string;
  dispatch: React.Dispatch<Action>;
}

export const ProblemContext: React.FC<ProblemContextProps> = ({ problemContext, dispatch }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(problemContext);
  const [renderedHtml, setRenderedHtml] = useState('');

  useEffect(() => {
    setEditText(problemContext);
    if (!problemContext) {
        setIsEditing(true);
    } else {
        setIsEditing(false);
        const parse = async () => {
            const html = await marked.parse(problemContext);
            setRenderedHtml(html);
        }
        parse();
    }
  }, [problemContext]);

  const handleSave = () => {
    dispatch({ type: 'SET_PROBLEM_CONTEXT', payload: editText });
    setIsEditing(false);
  };

  return (
    <div className="bg-gray-800/50 backdrop-blur-sm p-4 rounded-lg border border-gray-700 mb-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-white flex items-center">
          <BookOpenIcon className="w-5 h-5 mr-3 text-cyan-400" />
          Contexto del Problema y Objetivos
        </h3>
        {!isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="text-sm text-cyan-400 hover:text-cyan-300"
          >
            Editar
          </button>
        )}
      </div>
      
      {isEditing ? (
        <div>
          <textarea
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            placeholder="¿Qué preguntas buscas responder con estos datos? Describe el problema, tus hipótesis o los objetivos del análisis..."
            className="w-full h-32 p-2 bg-gray-900 border border-gray-600 rounded-md text-slate-300 text-sm focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
          />
          <div className="flex justify-end mt-2 space-x-2">
             {problemContext && (
                 <button
                    onClick={() => setIsEditing(false)}
                    className="px-4 py-2 rounded-md text-sm text-slate-300 bg-gray-600 hover:bg-gray-500 transition-colors"
                >
                    Cancelar
                </button>
             )}
            <button
              onClick={handleSave}
              className="px-4 py-2 rounded-md text-sm text-white font-semibold bg-cyan-600 hover:bg-cyan-700 transition-colors flex items-center"
            >
              <SaveIcon className="w-4 h-4 mr-2" />
              Guardar Contexto
            </button>
          </div>
        </div>
      ) : (
        <div 
          className="prose prose-sm prose-invert max-w-none prose-p:text-slate-300 prose-headings:text-slate-200 prose-strong:text-slate-100"
          dangerouslySetInnerHTML={{ __html: renderedHtml }} 
        />
      )}
    </div>
  );
};