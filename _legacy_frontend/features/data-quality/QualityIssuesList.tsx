import React from 'react';

interface QualityIssuesListProps {
  issues: {
    missing_values?: Record<string, number>;
    duplicates?: { count: number; percentage: number };
    data_types_summary?: Record<string, number>;
  } | null;
}

export const QualityIssuesList: React.FC<QualityIssuesListProps> = ({ issues }) => {
  if (!issues) {
    return <div className="bg-gray-800 p-6 rounded-lg"><p>No se han detectado problemas de calidad.</p></div>;
  }

  return (
    <div className="bg-gray-800 p-6 rounded-lg">
      <h3 className="text-lg font-semibold mb-4">Problemas de Calidad Detectados</h3>
      <ul className="space-y-3">
        {issues.missing_values && Object.entries(issues.missing_values.by_column).map(([col, percent]) => (
          percent > 0 && <li key={col} className="text-sm">Columna <strong>{col}</strong> tiene un <strong>{percent.toFixed(2)}%</strong> de valores faltantes.</li>
        ))}
        {issues.duplicates && issues.duplicates.count > 0 && (
          <li className="text-sm">Se encontraron <strong>{issues.duplicates.count}</strong> filas duplicadas ({issues.duplicates.percentage.toFixed(2)}%).</li>
        )}
        {/* Aquí se podrían añadir más tipos de problemas */}
      </ul>
    </div>
  );
};
