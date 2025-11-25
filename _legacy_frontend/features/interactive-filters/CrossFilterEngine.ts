import { create } from 'zustand';

interface CrossFilterState {
  filters: Record<string, any[]>;
  addFilter: (dimension: string, value: any) => void;
  removeFilter: (dimension: string, value: any) => void;
  clearFilters: () => void;
}

export const useCrossFilterStore = create<CrossFilterState>((set) => ({
  filters: {},
  addFilter: (dimension, value) =>
    set((state) => ({
      filters: {
        ...state.filters,
        [dimension]: [...(state.filters[dimension] || []), value],
      },
    })),
  removeFilter: (dimension, value) =>
    set((state) => ({
      filters: {
        ...state.filters,
        [dimension]: (state.filters[dimension] || []).filter((v) => v !== value),
      },
    })),
  clearFilters: () => set({ filters: {} }),
}));
