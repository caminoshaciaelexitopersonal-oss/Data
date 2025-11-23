// services/dataService.ts

import Papa from 'papaparse';
import { DataPoint } from '../types';

// All data loading and transformation logic has been moved to the backend.
// This service is now only responsible for client-side utilities like exporting.

// --- DATA EXPORT ---
export const exportDataToCsv = (data: DataPoint[], fileName: string) => {
    if (data.length === 0) {
        alert("No hay datos para exportar.");
        return;
    }
    const csv = Papa.unparse(data);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', fileName.replace(/(\.[\w\d_-]+)$/i, '_processed.csv'));
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}