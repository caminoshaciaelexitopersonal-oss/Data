import { GoogleGenAI, GenerateContentResponse } from "@google/genai";
import { ClassificationResult, RegressionResult, ClassificationMetric, ModelComparisonResultItem, ClusterResult } from "../types";

const getAiClient = (): GoogleGenAI => {
    // Always create a new instance to ensure it uses the latest API key from the environment.
    return new GoogleGenAI({ apiKey: process.env.API_KEY as string });
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

    try {
        const client = getAiClient();
        const response = await client.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: prompt,
        });
        return response.text;
    } catch (error) {
        console.error("Error calling Gemini API:", error);
        if (error instanceof Error) {
            if (error.message.includes('API key')) {
                 throw new Error("Análisis de IA fallido: La clave API no es válida o no está configurada.");
            }
            if (error.message.includes('Requested entity was not found')) {
                throw new Error("INVALID_KEY"); // Special message to be caught by UI
            }
        }
        throw new Error("Análisis de IA fallido: No se pudo conectar con el servicio.");
    }
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

    try {
        const client = getAiClient();
        const response = await client.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: prompt,
        });
        return response.text;
    } catch (error) {
        console.error("Error calling Gemini API:", error);
        if (error instanceof Error) {
            if (error.message.includes('API key')) {
                 throw new Error("Análisis de IA fallido: La clave API no es válida o no está configurada.");
            }
            if (error.message.includes('Requested entity was not found')) {
                throw new Error("INVALID_KEY");
            }
        }
        throw new Error("Análisis de IA fallido: No se pudo conectar con el servicio.");
    }
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

    try {
        const client = getAiClient();
        const response = await client.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: prompt,
        });
        return response.text;
    } catch (error) {
        console.error("Error calling Gemini API:", error);
        if (error instanceof Error) {
            if (error.message.includes('API key')) {
                 throw new Error("Análisis de IA fallido: La clave API no es válida o no está configurada.");
            }
            if (error.message.includes('Requested entity was not found')) {
                throw new Error("INVALID_KEY");
            }
        }
        throw new Error("Análisis de IA fallido: No se pudo conectar con el servicio.");
    }
};


export const analyzeClusterResults = async (
    chartImageBase64: string,
    clusterResult: ClusterResult,
    problemContext: string,
    datasetMetadata: string
): Promise<string> => {
    
    const uniqueClusters = [...new Set(clusterResult.assignments)];
    const noisePoints = clusterResult.assignments.filter(a => a === -1).length;
    const hasNoise = noisePoints > 0;

    const prompt = `
        Eres un experto analista de datos. Tu tarea es analizar los resultados de un algoritmo de clustering.

        **Contexto del Problema y Objetivos del Usuario:**
        ${problemContext || 'No proporcionado.'}

        **Metadatos del Dataset:**
        ${datasetMetadata || 'No proporcionado.'}

        **Resultados del Clustering (${clusterResult.algorithm}):**
        - **Número de Clústeres Identificados:** ${uniqueClusters.filter(c => c !== -1).length}
        - **Características Utilizadas:** ${clusterResult.featureNames.join(', ')}
        ${hasNoise ? `- Se identificaron ${noisePoints} puntos como ruido (no pertenecen a ningún clúster).` : ''}

        **Análisis Solicitado:**
        1.  **Interpretación del Gráfico:** Observa la imagen adjunta. Describe los clústeres que ves. ¿Están bien separados? ¿Son densos o dispersos? ¿Hay algún patrón visual obvio?
        2.  **Perfil de los Clústeres:** Basado en el gráfico y los datos, intenta describir cada clúster. Por ejemplo, "El Clúster 1 (color X) parece agrupar puntos con valores altos en [Característica A] y bajos en [Característica B]".
        3.  **Conexión con el Contexto:** Relaciona los clústeres encontrados con el contexto del problema proporcionado. ¿Qué podrían significar estos grupos? (ej. "Estos clústeres podrían representar diferentes segmentos de clientes...").
        4.  **Conclusión y Siguientes Pasos:** Ofrece una conclusión general. ¿Fue útil el clustering? ¿Qué sugerirías hacer a continuación?

        Proporciona el análisis en formato Markdown.
    `;

    try {
        const client = getAiClient();
        const imagePart = {
            inlineData: {
                mimeType: 'image/jpeg',
                data: chartImageBase64,
            },
        };
        const textPart = { text: prompt };

        const response: GenerateContentResponse = await client.models.generateContent({
            model: 'gemini-2.5-flash-image', // Using a multimodal model
            contents: { parts: [textPart, imagePart] },
        });

        return response.text;
    } catch (error) {
        console.error("Error calling Gemini API:", error);
        if (error instanceof Error) {
            if (error.message.includes('API key')) {
                throw new Error("Análisis de IA fallido: La clave API no es válida o no está configurada.");
            }
            if (error.message.includes('Requested entity was not found')) {
                throw new Error("INVALID_KEY");
            }
        }
        throw new Error("Análisis de IA fallido: No se pudo conectar con el servicio.");
    }
};