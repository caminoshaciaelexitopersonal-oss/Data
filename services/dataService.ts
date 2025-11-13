// services/dataService.ts

import Papa from 'papaparse';
import { DataPoint, OutlierReport, Transformation } from '../types';

// --- DATA LOADING ---

export const loadDataFromFile = async (file: File): Promise<{ data: DataPoint[], fileName: string }> => {
    const fileName = file.name;
    const extension = fileName.split('.').pop()?.toLowerCase();

    if (extension === 'csv' || extension === 'txt') {
        return { data: await parseCsv(file), fileName };
    }
    if (extension === 'json') {
        return { data: await parseJson(file), fileName };
    }
    throw new Error(`Unsupported file type for client-side parsing: .${extension}. Excel files should be handled by the backend.`);
};

const parseCsv = (file: File): Promise<DataPoint[]> => {
    return new Promise((resolve, reject) => {
        Papa.parse(file, {
            header: true,
            dynamicTyping: true,
            skipEmptyLines: true,
            complete: (results) => {
                if (results.errors.length) {
                    reject(new Error(`CSV parsing error: ${results.errors[0].message}`));
                } else {
                    const cleanData = results.data.filter(row => 
                        Object.values(row as object).some(val => val !== null && val !== '')
                    ) as DataPoint[];
                    resolve(cleanData);
                }
            },
            error: (error: Error) => reject(error),
        });
    });
};

const parseJson = (file: File): Promise<DataPoint[]> => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const text = event.target?.result;
                if (typeof text === 'string') {
                    const jsonData = JSON.parse(text);
                    if (Array.isArray(jsonData) && jsonData.every(item => typeof item === 'object' && item !== null)) {
                        resolve(jsonData);
                    } else {
                        reject(new Error('JSON file must be an array of objects.'));
                    }
                } else {
                     reject(new Error('Failed to read JSON file.'));
                }
            } catch (e) {
                const err = e as Error;
                reject(new Error(`Invalid JSON format: ${err.message}`));
            }
        };
        reader.onerror = (error) => reject(error);
        reader.readAsText(file);
    });
};


const parseExcel = async (file: File): Promise<{ sheetNames: string[], firstSheetData: DataPoint[] }> => {
    const arrayBuffer = await file.arrayBuffer();
    const workbook = XLSX.read(arrayBuffer, { type: 'buffer' });
    const sheetNames = workbook.SheetNames;
    if (sheetNames.length === 0) {
        throw new Error("The Excel file contains no sheets.");
    }
    const firstSheetName = sheetNames[0];
    const worksheet = workbook.Sheets[firstSheetName];
    const firstSheetData = XLSX.utils.sheet_to_json<DataPoint>(worksheet);
    return { sheetNames, firstSheetData };
};


// --- DATA ANALYSIS ---

export const analyzeDataQuality = (data: DataPoint[]): { [key: string]: { nulls: number; type: string } } => {
    if (data.length === 0) return {};

    const headers = Object.keys(data[0]);
    const qualityReport: { [key: string]: { nulls: number; type: string } } = {};

    headers.forEach(header => {
        let nullCount = 0;
        let numericCount = 0;
        let nonNumericCount = 0;

        data.forEach(row => {
            const value = row[header];
            if (value === null || value === undefined || value === '') {
                nullCount++;
            } else if (typeof value === 'number' && isFinite(value)) {
                numericCount++;
            } else {
                nonNumericCount++;
            }
        });

        // Determine type based on majority of non-null values
        const type = numericCount > nonNumericCount ? 'numeric' : 'categorical';

        qualityReport[header] = {
            nulls: nullCount,
            type: type,
        };
    });

    return qualityReport;
};


export const detectOutliers = (data: DataPoint[], qualityReport: { [key: string]: { type: string } }): OutlierReport => {
    const outlierReport: OutlierReport = {};
    const numericHeaders = Object.keys(qualityReport).filter(h => qualityReport[h].type === 'numeric');

    numericHeaders.forEach(header => {
        const values = data.map(row => row[header] as number).filter(v => v !== null && typeof v === 'number' && isFinite(v));
        if (values.length < 5) return; // Not enough data for robust outlier detection

        const sortedValues = [...values].sort((a, b) => a - b);
        const q1 = sortedValues[Math.floor(sortedValues.length * 0.25)];
        const q3 = sortedValues[Math.floor(sortedValues.length * 0.75)];
        const iqr = q3 - q1;

        const lowerBound = q1 - 1.5 * iqr;
        const upperBound = q3 + 1.5 * iqr;

        const outliers = values.filter(v => v < lowerBound || v > upperBound);

        if (outliers.length > 0) {
            outlierReport[header] = {
                count: outliers.length,
                lowerBound,
                upperBound,
            };
        }
    });

    return outlierReport;
};

// --- DATA TRANSFORMATION ---

export const applyTransformations = (data: DataPoint[], transformations: Transformation[], outlierReport: OutlierReport): DataPoint[] => {
    let transformedData = data.map(row => ({ ...row }));

    for (const action of transformations) {
        if (action.type === 'DROP_COLUMN') {
            transformedData.forEach(row => delete row[action.column]);
        }
        else if (action.type === 'FILL_NULLS') {
            const { column, strategy } = action;
            const values = transformedData.map(r => r[column]).filter(v => v !== null && v !== undefined && v !== '') as (number | string)[];
            
            let fillValue: string | number | null = null;
            if (strategy === 'mean') {
                const numericValues = values.filter(v => typeof v === 'number') as number[];
                if (numericValues.length > 0) fillValue = numericValues.reduce((a, b) => a + b, 0) / numericValues.length;
            } else if (strategy === 'median') {
                const numericValues = values.filter(v => typeof v === 'number') as number[];
                if (numericValues.length > 0) {
                    const sorted = [...numericValues].sort((a, b) => a - b);
                    const mid = Math.floor(sorted.length / 2);
                    fillValue = sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
                }
            } else if (strategy === 'mode') {
                if(values.length > 0) {
                    const counts = values.reduce((acc, val) => {
                        acc[String(val)] = (acc[String(val)] || 0) + 1;
                        return acc;
                    }, {} as Record<string, number>);
                    fillValue = Object.keys(counts).reduce((a, b) => counts[a] > counts[b] ? a : b);
                }
            }
            
            if(fillValue !== null) {
                transformedData.forEach(row => {
                    if (row[column] === null || row[column] === undefined || row[column] === '') {
                        row[column] = fillValue;
                    }
                });
            }
        }
        else if (action.type === 'NORMALIZE') {
            const { column, method } = action;
            const values = transformedData.map(r => r[column] as number).filter(v => typeof v === 'number');
            if(values.length === 0) continue;

            if (method === 'z-score') {
                const mean = values.reduce((a, b) => a + b, 0) / values.length;
                const stdDev = Math.sqrt(values.map(x => (x - mean) ** 2).reduce((a, b) => a + b, 0) / values.length);
                transformedData.forEach(row => {
                    if (typeof row[column] === 'number') {
                        row[column] = (row[column] as number - mean) / (stdDev || 1);
                    }
                });
            } else if (method === 'min-max') {
                const min = Math.min(...values);
                const max = Math.max(...values);
                const range = max - min;
                transformedData.forEach(row => {
                     if (typeof row[column] === 'number') {
                        row[column] = range > 0 ? ((row[column] as number - min) / range) : 0;
                    }
                });
            }
        }
        else if (action.type === 'REMOVE_OUTLIERS') {
            const report = outlierReport[action.column];
            if (!report) continue;
            transformedData = transformedData.filter(row => {
                const value = row[action.column];
                if (typeof value !== 'number') return true; // keep non-numeric/null rows
                return value >= report.lowerBound && value <= report.upperBound;
            });
        }
        else if (action.type === 'CAP_OUTLIERS') {
            const report = outlierReport[action.column];
            if (!report) continue;
            transformedData.forEach(row => {
                const value = row[action.column];
                if (typeof value === 'number') {
                    if (value < report.lowerBound) row[action.column] = report.lowerBound;
                    if (value > report.upperBound) row[action.column] = report.upperBound;
                }
            });
        }
        else if (action.type === 'ONE_HOT_ENCODE') {
            const { column } = action;
            const uniqueValues = [...new Set(transformedData.map(row => row[column]).filter(v => v !== null && v !== undefined))];
            
            uniqueValues.forEach(value => {
                const newColName = `${column}_${String(value).replace(/\s+/g, '_')}`;
                transformedData.forEach(row => {
                    row[newColName] = (row[column] === value) ? 1 : 0;
                });
            });

            transformedData.forEach(row => {
                delete row[column];
            });
        }
    }

    return transformedData;
};

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