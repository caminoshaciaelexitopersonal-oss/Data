import pandas as pd
import io
from typing import Dict, Any

def load_parquet(file_content: bytes, config: Dict[str, Any] = None) -> pd.DataFrame:
    """
    Carga datos desde el contenido en bytes de un archivo Parquet a un DataFrame de pandas.

    :param file_content: Contenido del archivo Parquet en bytes.
    :param config: Configuración opcional para la lectura del Parquet (e.g., columns).
    :return: DataFrame de pandas con los datos cargados.
    :raises: Exception para errores de lectura.
    """
    config = config or {}
    try:
        # Usar BytesIO para leer el contenido binario directamente
        df = pd.read_parquet(io.BytesIO(file_content), **config)
        return df
    except Exception as e:
        raise Exception(f"Error al leer el contenido del archivo Parquet: {e}")
