import React from 'react';
import { useCrossFilterStore } from './CrossFilterEngine';
import { FilterBadge } from './FilterBadge';
import { useDashboardStore } from '../../store/dashboardStore';

export const MultiFilterPanel: React.FC = () => {
  const { filters, addFilter, clearFilters } = useCrossFilterStore();
  const { visualizations } = useDashboardStore();

  const getCategoricalColumns = () => {
    if (!visualizations?.raw_data) return [];
    const firstRow = visualizations.raw_data[0] || {};
    return Object.keys(firstRow).filter(key => typeof firstRow[key] === 'string');
  };

  const handleAddFilter = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const [dimension, value] = e.target.value.split(':');
    if (dimension && value) {
      addFilter(dimension, value);
    }
  };

  return (
    <div className="bg-gray-800 p-4 rounded-lg">
      <h3 className="text-lg font-semibold mb-4">Filtros Cruzados</h3>
      <div className="mb-4">
        <select onChange={handleAddFilter} className="w-full p-2 bg-gray-700 rounded">
          <option value="">Añadir filtro...</option>
          {getCategoricalColumns().map(col =>
            [...new Set(visualizations.raw_data.map(row => row[col]))].map(val => (
              <option key={`${col}-${val}`} value={`${col}:${val}`}>{col}: {val}</option>
            ))
          )}
        </select>
      </div>
      <div className="flex flex-wrap">
        {Object.entries(filters).flatMap(([dim, vals]) =>
          vals.map(val => <FilterBadge key={`${dim}-${val}`} dimension={dim} value={val} />)
        )}
      </div>
      {Object.keys(filters).length > 0 && (
        <button onClick={clearFilters} className="mt-4 text-sm text-cyan-400 hover:underline">
          Limpiar todos los filtros
        </button>
      )}
    </div>
  );
};
