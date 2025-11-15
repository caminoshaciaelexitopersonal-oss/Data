import create from 'zustand';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

interface DashboardState {
  visualizations: Record<string, any> | null;
  loading: boolean;
  error: string | null;
  selectedCharts: string[];
  fetchVisualizations: () => Promise<void>;
  toggleChartSelection: (chartKey: string) => void;
}

export const useDashboardStore = create<DashboardState>((set, get) => ({
  visualizations: null,
  loading: true,
  error: null,
  selectedCharts: [],

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

      set({ visualizations: data, loading: false, selectedCharts: defaultSelected });
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
}));
