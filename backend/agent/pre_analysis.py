import pandas as pd
from typing import Dict, Any, List

def detect_intent(user_query: str, data_sample: pd.DataFrame = None) -> Dict[str, Any]:
    """
    Analiza la consulta del usuario y una muestra de datos para detectar la intención
    y extraer contexto relevante.

    Args:
        user_query (str): La pregunta o comando del usuario.
        data_sample (pd.DataFrame, optional): Una muestra del DataFrame para análisis de contexto.

    Returns:
        Dict[str, Any]: Un diccionario con la intención detectada y el contexto.
    """
    query_lower = user_query.lower()
    intent = "unknown"
    context = {}

    # Detección de intención basada en palabras clave
    if any(keyword in query_lower for keyword in ["eda", "analiza", "explora", "describe", "resumen"]):
        intent = "EDA"
    elif any(keyword in query_lower for keyword in ["entrena", "modelo", "machine learning", "ml", "predecir", "clasificar"]):
        intent = "ML"
    elif any(keyword in query_lower for keyword in ["carga", "sube", "lee", "importa"]):
        intent = "LOAD_DATA"
    elif any(keyword in query_lower for keyword in ["calidad", "limpia", "health", "calidad de datos"]):
        intent = "QUALITY_REPORT"
    elif any(keyword in query_lower for keyword in ["anomalías", "outliers", "valores atípicos"]):
        intent = "ANOMALY_DETECTION"

    # Extracción de contexto si hay datos disponibles
    if data_sample is not None and not data_sample.empty:
        context['dataset_shape'] = data_sample.shape
        context['columns'] = data_sample.columns.tolist()
        context['numerical_columns'] = data_sample.select_dtypes(include=['number']).columns.tolist()
        context['categorical_columns'] = data_sample.select_dtypes(include=['object', 'category']).columns.tolist()

    return {
        "intent": intent,
        "context": context
    }
