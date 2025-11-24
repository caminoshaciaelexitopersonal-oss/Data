import pandas as pd
import io
from typing import Dict, Any

def load_jsonl(file_content: bytes, config: Dict[str, Any] = None) -> pd.DataFrame:
    """
    Carga datos desde el contenido en bytes de un archivo JSON Lines (JSONL) a un DataFrame.

    :param file_content: Contenido del archivo JSONL en bytes.
    :param config: Configuración opcional para la lectura del JSON.
    :return: DataFrame de pandas con los datos cargados.
    :raises: Exception para errores de decodificación o lectura.
    """
    config = config or {}
    try:
        content_str = file_content.decode('utf-8')
        # El parámetro 'lines=True' es clave para procesar el formato JSONL
        df = pd.read_json(io.StringIO(content_str), lines=True, **config)
        return df
    except UnicodeDecodeError as e:
        raise Exception(f"Error de codificación al procesar el archivo JSONL. Se esperaba UTF-8. Error: {e}")
    except Exception as e:
        raise Exception(f"Error al leer el contenido del archivo JSONL: {e}")
