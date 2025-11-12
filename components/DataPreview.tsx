import React from 'react';
import { DataPoint } from '../types';

interface DataPreviewProps {
  data: DataPoint[];
}

export const DataPreview: React.FC<DataPreviewProps> = ({ data }) => {
  if (data.length === 0) {
    return null;
  }

  const headers = Object.keys(data[0]);
  const previewData = data.slice(0, 10);

  return (
    <div className="bg-gray-900/50 p-4 rounded-lg border border-gray-700 mb-6">
      <div className="overflow-x-auto max-h-64">
        <table className="w-full text-sm text-left text-slate-300">
          <thead className="text-xs text-slate-400 uppercase bg-gray-700/50 sticky top-0">
            <tr>
              {headers.map(header => (
                <th key={header} scope="col" className="px-4 py-2 whitespace-nowrap">
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {previewData.map((row, rowIndex) => (
              <tr key={rowIndex} className="hover:bg-gray-800/60">
                {headers.map(header => (
                  <td key={`${rowIndex}-${header}`} className="px-4 py-2 whitespace-nowrap">
                    {row[header] === null ? <span className="text-slate-500 italic">null</span> : String(row[header])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {data.length > 10 && (
          <p className="text-xs text-slate-500 mt-2 text-center">
              Mostrando las primeras 10 de {data.length} filas.
          </p>
      )}
    </div>
  );
};