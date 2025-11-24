import { create } from 'zustand';
import { useCrossFilterStore } from '../features/interactive-filters/CrossFilterEngine';
import { v4 as uuidv4 } from 'uuid';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000") + "/compat/v1";

interface DashboardState {
  sessionId: string | null;
  visualizations: Record<string, any> | null;
  filteredVisualizations: Record<string, any> | null;
  dataHealthReport: Record<string, any> | null;
  loading: boolean;
  error: string | null;
  selectedCharts: string[];
  filters: Record<string, any>;
  fetchVisualizations: () => Promise<void>;
  fetchDataHealthReport: () => Promise<void>;
  recalculateVisualizations: (filteredData: any[]) => Promise<void>;
  toggleChartSelection: (chartKey: string) => void;
  setFilter: (key: string, value: any) => void;
}

const applyFilters = (data: Record<string, any>, crossFilters: Record<string, any[]>): any[] => {
    if (!data || !data.raw_data) {
        return [];
    }
    if (Object.keys(crossFilters).length === 0) {
        return data.raw_data;
    }

    return data.raw_data.filter(row => {
        return Object.entries(crossFilters).every(([dimension, values]) => {
            if (!values || values.length === 0) return true;
            return values.includes(row[dimension]);
        });
    });
};

export const useDashboardStore = create<DashboardState>((set, get) => {
    const store = {
        sessionId: uuidv4(),
        visualizations: null,
        filteredVisualizations: null,
        dataHealthReport: null,
        loading: true,
        error: null,
        selectedCharts: [],
        filters: {},

        fetchVisualizations: async () => {
            set({ loading: true, error: null });
            try {
            const response = await fetch(`${API_BASE_URL}/api/v1/visualizations`);
                if (!response.ok) {
                    throw new Error("No se pudieron cargar las visualizaciones.");
                }
                const data = await response.json();
                const defaultSelected = Object.keys(data);
                set({
                    visualizations: data,
                    filteredVisualizations: data,
                    loading: false,
                    selectedCharts: defaultSelected
                });
            } catch (err) {
                set({ error: (err as Error).message, loading: false });
            }
        },

        fetchDataHealthReport: async () => {
            const rawData = get().visualizations?.raw_data;
            if (!rawData) {
                set({ error: "No hay datos crudos para generar el informe de salud." });
                return;
            }
            try {
                const response = await fetch(`${API_BASE_URL}/mpa/quality/report`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify( rawData ),
                });
                if (!response.ok) {
                    throw new Error('No se pudo generar el informe de salud.');
                }
                const report = await response.json();
                set({ dataHealthReport: report });
            } catch (err) {
                set({ error: (err as Error).message });
            }
        },

        recalculateVisualizations: async (filteredData: any[]) => {
            try {
                const response = await fetch(`${API_BASE_URL}/mpa/eda/recalculate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ data: filteredData }),
                });
                if (!response.ok) {
                    throw new Error('No se pudieron recalcular las visualizaciones.');
                }
                const newVisualizations = await response.json();
                const currentVisualizations = get().visualizations;
                set({
                    filteredVisualizations: { ...currentVisualizations, ...newVisualizations },
                });
            } catch (err) {
                set({ error: (err as Error).message });
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
                // This filter is now handled by the cross-filter subscription
                return { filters: newFilters };
            });
        },
    };

    useCrossFilterStore.subscribe(
        (filters) => {
            const { visualizations, recalculateVisualizations } = get();
            if (visualizations) {
                const filteredData = applyFilters(visualizations, filters);
                recalculateVisualizations(filteredData);
            }
        },
        (state) => state.filters
    );

    return store;
});
