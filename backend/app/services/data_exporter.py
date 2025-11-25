import pandas as pd
import os
from typing import List, Dict, Any

# --- Constantes de Exportación ---
OUTPUT_DIRECTORY = "data/processed"

def unify_dataframes(dataframes: List[pd.DataFrame]) -> pd.DataFrame:
    """
    Unifica una lista de DataFrames en uno solo mediante concatenación.
    """
    if not dataframes or not all(isinstance(df, pd.DataFrame) for df in dataframes):
        raise ValueError("La entrada debe ser una lista no vacía de DataFrames de pandas.")

    unified_df = pd.concat(dataframes, ignore_index=True)
    return unified_df

def export_data(df: pd.DataFrame, output_filename: str, config: Dict[str, Any] = None) -> str:
    """
    Exporta un DataFrame a un archivo CSV en el directorio predefinido.

    :param df: El DataFrame a exportar.
    :param output_filename: El nombre del archivo de salida (sin extensión).
    :param config: Configuración adicional para la función to_csv de pandas.
    :return: La ruta completa al archivo exportado.
    :raises: Exception para errores durante el proceso de escritura del archivo.
    """
    config = config or {}

    try:
        # Asegurar que el directorio de salida existe
        os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

        # Construir la ruta completa
        full_path = os.path.join(OUTPUT_DIRECTORY, f"{output_filename}.csv")

        # Exportar a CSV
        df.to_csv(full_path, index=False, **config)

        print(f"Datos exportados exitosamente a {full_path}")
        return full_path

    except Exception as e:
        raise Exception(f"Error al exportar datos a {full_path}: {e}")
