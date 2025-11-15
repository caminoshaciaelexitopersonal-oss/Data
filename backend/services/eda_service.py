import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from typing import List, Dict, Any

# Asegura que matplotlib use un backend no interactivo para evitar problemas en el servidor
plt.switch_backend('Agg')

def _calculate_advanced_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Calcula estadísticas descriptivas avanzadas para las columnas numéricas."""
    stats = {}
    numerical_cols = df.select_dtypes(include=['number']).columns

    for col in numerical_cols:
        desc = df[col].describe()
        skewness = df[col].skew()
        kurtosis = df[col].kurt()
        iqr = desc['75%'] - desc['25%']

        # Detección simple de outliers usando el rango intercuartílico (IQR)
        lower_bound = desc['25%'] - 1.5 * iqr
        upper_bound = desc['75%'] + 1.5 * iqr
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)].shape[0]

        stats[col] = {
            'mean': desc.get('mean'),
            'std': desc.get('std'),
            'min': desc.get('min'),
            '25%': desc.get('25%'),
            '50%': desc.get('50%'),
            '75%': desc.get('75%'),
            'max': desc.get('max'),
            'skewness': skewness,
            'kurtosis': kurtosis,
            'iqr': iqr,
            'outliers_count': outliers
        }
    return stats

def _generate_plot_base64(fig) -> str:
    """Convierte una figura de matplotlib a un string base64."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def _generate_eda_plots(df: pd.DataFrame) -> Dict[str, str]:
    """Genera histogramas y diagramas de caja para las columnas numéricas."""
    plots = {}
    numerical_cols = df.select_dtypes(include=['number']).columns

    for col in numerical_cols:
        # Generar Histograma
        fig_hist, ax_hist = plt.subplots(figsize=(8, 5))
        df[col].hist(ax=ax_hist, bins=20, grid=False, color='skyblue')
        ax_hist.set_title(f'Histograma de {col}')
        ax_hist.set_xlabel(col)
        ax_hist.set_ylabel('Frecuencia')
        plots[f'histogram_{col}'] = _generate_plot_base64(fig_hist)

        # Generar Diagrama de Caja (Boxplot)
        fig_box, ax_box = plt.subplots(figsize=(8, 5))
        df.boxplot(column=[col], ax=ax_box, grid=False, patch_artist=True)
        ax_box.set_title(f'Diagrama de Caja de {col}')
        ax_box.set_ylabel('Valor')
        plots[f'boxplot_{col}'] = _generate_plot_base64(fig_box)

    return plots

def generate_advanced_eda(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Función principal que genera un informe EDA avanzado con estadísticas y gráficos.

    :param data: Datos de entrada como una lista de diccionarios.
    :return: Un diccionario que contiene estadísticas avanzadas y gráficos en base64.
    """
    if not data:
        return {"error": "No se proporcionaron datos para el análisis EDA."}

    try:
        df = pd.DataFrame(data)

        advanced_stats = _calculate_advanced_stats(df)
        plots = _generate_eda_plots(df)

        return {
            "status": "success",
            "advanced_statistics": advanced_stats,
            "plots_base64": plots
        }
    except Exception as e:
        return {"status": "error", "message": f"Ocurrió un error durante la generación del EDA: {e}"}


# --- Data Quality and Health Score Service ---

def _calculate_missing_values(df: pd.DataFrame) -> Dict[str, Any]:
    """Calcula el porcentaje de valores faltantes por columna."""
    missing_percentage = (df.isnull().sum() / len(df)) * 100
    return {
        "total_percentage": missing_percentage.mean(),
        "by_column": missing_percentage.to_dict()
    }

def _calculate_duplicates(df: pd.DataFrame) -> Dict[str, Any]:
    """Calcula el número y porcentaje de filas duplicadas."""
    duplicate_count = df.duplicated().sum()
    duplicate_percentage = (duplicate_count / len(df)) * 100 if len(df) > 0 else 0
    return {
        "count": duplicate_count,
        "percentage": duplicate_percentage
    }

def _summarize_data_types(df: pd.DataFrame) -> Dict[str, int]:
    """Resume los tipos de datos presentes en el DataFrame."""
    return df.dtypes.astype(str).value_counts().to_dict()

def _calculate_cardinality(df: pd.DataFrame) -> Dict[str, Any]:
    """Calcula la cardinalidad de las columnas categóricas."""
    cardinality_report = {}
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns
    for col in categorical_cols:
        unique_count = df[col].nunique()
        cardinality_report[col] = unique_count
    return cardinality_report

def generate_data_health_report(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Función principal que genera un informe de salud de datos completo y una puntuación.
    """
    if not data:
        return {"error": "No se proporcionaron datos para el informe de salud."}

    try:
        df = pd.DataFrame(data)
        if df.empty:
            return {"error": "El DataFrame está vacío."}

        # Realizar todas las comprobaciones de calidad
        missing_values = _calculate_missing_values(df)
        duplicates = _calculate_duplicates(df)
        data_types = _summarize_data_types(df)
        cardinality = _calculate_cardinality(df)

        # Calcular el Data Health Score
        score = 100
        score -= missing_values['total_percentage'] * 1.5  # Penalización más alta para valores nulos
        score -= duplicates['percentage']  # Penalización directa por duplicados

        # Penalización leve por tener columnas con cardinalidad muy baja (casi constantes)
        for col, num_unique in cardinality.items():
            if num_unique <= 1 and len(df) > 1:
                score -= 5

        health_score = max(0, round(score, 2))  # Asegurar que el score no sea negativo

        return {
            "status": "success",
            "health_score": health_score,
            "report": {
                "missing_values": missing_values,
                "duplicates": duplicates,
                "data_types_summary": data_types,
                "cardinality_summary": cardinality,
            }
        }
    except Exception as e:
        return {"status": "error", "message": f"Ocurrió un error durante la generación del informe de salud: {e}"}
