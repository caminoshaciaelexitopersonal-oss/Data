import { ClassificationResult, RegressionResult, ClassificationMetric, ModelComparisonResultItem, ClusterResult } from "../types";

// URL base de la API, asumida como variable de entorno inyectada.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

/**
 * Llama al endpoint proxy seguro del backend para interactuar con Gemini.
 * @param prompt El prompt a enviar a la IA.
 * @returns El texto de respuesta de la IA.
 */
const callGeminiProxy = async (prompt: string): Promise<string> => {
    try {
        const response = await fetch(`${API_BASE_URL}/mpa/ml/proxy/gemini`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Error en la comunicación con el servicio de IA del backend.");
        }

        const data = await response.json();
        return data.text;

    } catch (error) {
        console.error("Error calling Gemini proxy:", error);
        if (error instanceof Error) {
            // Re-lanzar el error para que la UI pueda manejarlo.
            throw new Error(`Análisis de IA fallido: ${error.message}`);
        }
        throw new Error("Análisis de IA fallido: Ocurrió un error desconocido.");
    }
};


export const analyzeClassificationResults = async (
    result: ClassificationResult,
    problemContext: string,
    datasetMetadata: string
): Promise<string> => {
    
    const { accuracy, confusionMatrix, classLabels, report, algorithm } = result;

    const algorithmName = {
        'naive_bayes': 'Naive Bayes',
        'logistic_regression': 'Regresión Logística',
        'decision_tree': 'Árbol de Decisión'
    }[algorithm] || 'Clasificación';

    const prompt = `
        Eres un experto analista de datos. Teniendo en cuenta el siguiente contexto, analiza los resultados de un modelo de clasificación ${algorithmName} y proporciona un resumen conciso en formato Markdown.
        Explica qué significan los resultados en términos sencillos para alguien que no es un experto.

        **Contexto del Problema (Objetivos del usuario):**
        ${problemContext || 'No proporcionado.'}

        **Metadatos del Dataset (Descripción de los datos):**
        ${datasetMetadata || 'No proporcionado.'}
        
        **Resumen de Métricas:**
        - **Exactitud (Accuracy):** ${accuracy.toFixed(3)} (${(accuracy * 100).toFixed(1)}%)
        - **Clases:** ${classLabels.join(', ')}

        **Matriz de Confusión:**
        (Filas son la clase real, columnas son la clase predicha)
        ${classLabels.map((label, i) => `        - ${label}: [${confusionMatrix[i].join(', ')}]`).join('\n')}

        **Reporte por Clase:**
        ${Object.entries(report).map(([className, metrics]) => {
            const typedMetrics = metrics as ClassificationMetric;
            return `        - **${className}**: Precisión=${typedMetrics.precision.toFixed(2)}, Recall=${typedMetrics.recall.toFixed(2)}, F1-Score=${typedMetrics.f1Score.toFixed(2)}`
        }).join('\n')}

        **Análisis Solicitado:**
        1.  **Interpretación de la Exactitud:** ¿Es el modelo bueno en general? ¿Qué significa este porcentaje en el contexto del problema?
        2.  **Análisis de la Matriz de Confusión:** ¿Dónde se confunde más el modelo? ¿Es esto problemático según los objetivos?
        3.  **Análisis del Reporte por Clase:** ¿Hay alguna clase que el modelo prediga particularmente bien o mal? ¿Por qué es relevante?
        4.  **Conclusión y Recomendaciones:** En 1 o 2 frases, ¿cuál es la conclusión principal y qué recomiendas para mejorar el modelo en base al contexto?
    `;

    return callGeminiProxy(prompt);
};


export const analyzeRegressionResults = async (
    result: RegressionResult,
    problemContext: string,
    datasetMetadata: string
): Promise<string> => {
    
    const { rSquared, mse, targetVariable, featureVariables } = result;
    
    const prompt = `
        Eres un experto analista de datos. Teniendo en cuenta el siguiente contexto, analiza los resultados de un modelo de Regresión Lineal y proporciona un resumen conciso en formato Markdown.
        
        **Contexto del Problema (Objetivos del usuario):**
        ${problemContext || 'No proporcionado.'}

        **Metadatos del Dataset (Descripción de los datos):**
        ${datasetMetadata || 'No proporcionado.'}
        
        **Resumen de Métricas:**
        - **Variable Objetivo (Y):** ${targetVariable}
        - **Variables Predictoras (X):** ${featureVariables.join(', ')}
        - **Coeficiente de Determinación (R²):** ${rSquared.toFixed(3)}
        - **Error Cuadrático Medio (MSE):** ${mse.toFixed(3)}

        **Análisis Solicitado:**
        1.  **Interpretación del R-cuadrado (R²):** En el contexto del problema, ¿qué tan bien explican las variables predictoras a la variable objetivo? Explica el valor de R² como un porcentaje.
        2.  **Interpretación del Error Cuadrático Medio (MSE):** ¿Qué nos dice este valor sobre el error promedio de las predicciones?
        3.  **Rendimiento del Modelo:** Basado en el contexto y las métricas, ¿es este un modelo útil para los objetivos planteados?
        4.  **Conclusión y Recomendaciones:** ¿Cuál es la conclusión principal? ¿Qué sugerirías para mejorar el modelo?
    `;

    return callGeminiProxy(prompt);
};


export const analyzeModelComparison = async (
    results: ModelComparisonResultItem[],
    problemContext: string,
    datasetMetadata: string
): Promise<string> => {
    const prompt = `
        Eres un experto analista de datos. Teniendo en cuenta el siguiente contexto, analiza la tabla de comparación de modelos de clasificación y proporciona un resumen ejecutivo en formato Markdown.

        **Contexto del Problema (Objetivos del usuario):**
        ${problemContext || 'No proporcionado.'}

        **Metadatos del Dataset (Descripción de los datos):**
        ${datasetMetadata || 'No proporcionado.'}

        **Resultados de la Comparación:**
        | Algoritmo             | Accuracy | Precisión (Macro) | Recall (Macro) | F1-Score (Macro) | Error     |
        |-----------------------|----------|-------------------|----------------|------------------|-----------|
        ${results.map(r => `| ${r.algorithm.padEnd(21)} | ${r.accuracy !== undefined ? r.accuracy.toFixed(3).padEnd(8) : 'N/A'.padEnd(8)} | ${r.precision !== undefined ? r.precision.toFixed(3).padEnd(17) : 'N/A'.padEnd(17)} | ${r.recall !== undefined ? r.recall.toFixed(3).padEnd(14) : 'N/A'.padEnd(14)} | ${r.f1Score !== undefined ? r.f1Score.toFixed(3).padEnd(16) : 'N/A'.padEnd(16)} | ${r.error || 'Ninguno'.padEnd(9)} |`).join('\n')}

        **Análisis Solicitado:**
        1.  **Mejor Modelo General:** Basado en el contexto y los objetivos, ¿qué modelo recomendarías y por qué? Considera un balance de métricas.
        2.  **Análisis de Fortalezas y Debilidades:** Compara brevemente los modelos. ¿Alguno es mejor para una tarea específica según el contexto (p.ej., minimizar falsos negativos)?
        3.  **Conclusión Final:** Proporciona una recomendación clara y concisa para un público no técnico.
    `;

    return callGeminiProxy(prompt);
};

// Nota: La función analyzeClusterResults requiere un endpoint proxy multimodal que pueda manejar imágenes,
// lo cual no está implementado en esta versión. Se deja la estructura como placeholder.
export const analyzeClusterResults = async (
    chartImageBase64: string,
    clusterResult: ClusterResult,
    problemContext: string,
    datasetMetadata: string
): Promise<string> => {
    
    console.warn("La función 'analyzeClusterResults' requiere un endpoint multimodal que no está implementado en el proxy actual.");

    // Devolvemos un mensaje informativo en lugar de intentar una llamada que fallará.
    return Promise.resolve("## Análisis de Clustering no disponible\n\nEsta funcionalidad requiere una actualización del backend para soportar análisis de imágenes a través del proxy seguro.");
};
