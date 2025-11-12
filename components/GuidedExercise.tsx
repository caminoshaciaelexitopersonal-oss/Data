import React, { useState, useEffect } from 'react';
import { marked } from 'marked';

interface Cell {
  tipo_celda: 'markdown' | 'código';
  fuente: string[];
}

export interface Notebook {
  células: Cell[];
}

interface GuidedExerciseProps {
  notebook: Notebook;
}

const MarkdownCell: React.FC<{ source: string[] }> = ({ source }) => {
    const [html, setHtml] = useState('');
    useEffect(() => {
        const parse = async () => {
            const fullText = source.join('');
            const parsedHtml = await marked.parse(fullText);
            setHtml(parsedHtml);
        }
        parse();
    }, [source]);

    return <div className="prose prose-sm prose-invert max-w-none prose-p:text-slate-300 prose-headings:text-slate-200 prose-strong:text-slate-100 prose-code:text-yellow-300 prose-pre:bg-gray-900 prose-table:w-full prose-th:border prose-th:border-gray-600 prose-th:p-2 prose-td:border prose-td:border-gray-600 prose-td:p-2" dangerouslySetInnerHTML={{ __html: html }} />;
}

export const GuidedExercise: React.FC<GuidedExerciseProps> = ({ notebook }) => {
  return (
    <div className="space-y-4 max-w-4xl mx-auto">
      {notebook.células.map((cell, index) => (
        <div key={index} className="bg-gray-800 border border-gray-700 rounded-lg overflow-hidden">
          {cell.tipo_celda === 'markdown' ? (
            <div className="p-4">
                <MarkdownCell source={cell.fuente} />
            </div>
          ) : (
            <div className="bg-gray-900 p-4">
              <pre className="text-sm text-cyan-300 overflow-x-auto">
                <code>
                    {cell.fuente.join('')}
                </code>
              </pre>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};