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
