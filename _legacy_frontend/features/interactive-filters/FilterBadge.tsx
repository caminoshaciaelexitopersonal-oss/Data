import React from 'react';
import { useCrossFilterStore } from './CrossFilterEngine';

export const FilterBadge: React.FC<{ dimension: string; value: any }> = ({ dimension, value }) => {
  const removeFilter = useCrossFilterStore((state) => state.removeFilter);

  return (
    <span className="inline-flex items-center px-2 py-1 mr-2 text-sm font-medium text-cyan-100 bg-cyan-700 rounded-full">
      {dimension}: {String(value)}
      <button
        onClick={() => removeFilter(dimension, value)}
        className="ml-1.5 text-cyan-200 hover:text-white"
      >
        &times;
      </button>
    </span>
  );
};
