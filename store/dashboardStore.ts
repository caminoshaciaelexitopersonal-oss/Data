import { create } from 'zustand';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

interface DashboardState {
  visualizations: Record<string, any> | null;
  filteredVisualizations: Record<string, any> | null;
  loading: boolean;
  error: string | null;
  selectedCharts: string[];
  filters: Record<string, any>;
  fetchVisualizations: () => Promise<void>;
  toggleChartSelection: (chartKey: string) => void;
  setFilter: (key: string, value: any) => void;
}

const applyFilters = (data: Record<string, any>, filters: Record<string, any>): Record<string, any> => {
    if (Object.keys(filters).length === 0) return data;
    // Lógica de filtrado simple (ejemplo)
    // Esto necesitaría ser mucho más robusto en una implementación real
    let filteredData = { ...data };
    // Esta es una simplificación. Un filtrado real requeriría lógica por tipo de gráfico.
    return filteredData;
};

export const useDashboardStore = create<DashboardState>((set, get) => ({
  visualizations: null,
  filteredVisualizations: null,
  loading: true,
  error: null,
  selectedCharts: [],
  filters: {},

  fetchVisualizations: async () => {
    set({ loading: true, error: null });
    try {
      const response = await fetch(`${API_BASE_URL}/api/visualizations`);
      if (!response.ok) {
        throw new Error("No se pudieron cargar las visualizaciones.");
      }
      const data = await response.json();

      // Al cargar nuevos datos, seleccionamos todos los gráficos disponibles por defecto.
      const defaultSelected = Object.keys(data);
      const filteredData = applyFilters(data, get().filters);

      set({
          visualizations: data,
          filteredVisualizations: filteredData,
          loading: false,
          selectedCharts: defaultSelected
      });
    } catch (err) {
      set({ error: (err as Error).message, loading: false });
    }
  },

  toggleChartSelection: (chartKey: string) => {
    set((state) => {
      const selectedCharts = state.selectedCharts.includes(chartKey)
        ? state.selectedCharts.filter((key) => key !== chartKey)
        : [...state.selectedCharts, chartKey];
      return { selectedCharts };
    });
  },

  setFilter: (key: string, value: any) => {
    set((state) => {
      const newFilters = { ...state.filters, [key]: value };
      if (value === null || value === undefined) {
        delete newFilters[key];
      }
      const filteredData = applyFilters(state.visualizations || {}, newFilters);
      return { filters: newFilters, filteredVisualizations: filteredData };
    });
  },
}));
