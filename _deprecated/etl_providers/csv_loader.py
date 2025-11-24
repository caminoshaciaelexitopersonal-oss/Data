import pandas as pd
import io
from typing import Dict, Any

def load_csv(file_content: bytes, config: Dict[str, Any] = None) -> pd.DataFrame:
    """
    Carga datos desde el contenido en bytes de un archivo CSV a un DataFrame de pandas.

    :param file_content: Contenido del archivo CSV en bytes.
    :param config: Configuración opcional para la lectura del CSV (e.g., separador, codificación).
    :return: DataFrame de pandas con los datos cargados.
    :raises: Exception para errores de decodificación o lectura.
    """
    config = config or {}
    try:
        # Decodificar los bytes a una cadena y usar StringIO para que pandas lo lea como un archivo
        content_str = file_content.decode('utf-8')
        df = pd.read_csv(io.StringIO(content_str), **config)
        return df
    except UnicodeDecodeError as e:
        raise Exception(f"Error de codificación al procesar el archivo CSV. Se esperaba UTF-8. Error: {e}")
    except Exception as e:
        raise Exception(f"Error al leer el contenido del archivo CSV: {e}")
