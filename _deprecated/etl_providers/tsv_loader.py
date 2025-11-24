import pandas as pd
import io
from typing import Dict, Any

def load_tsv(file_content: bytes, config: Dict[str, Any] = None) -> pd.DataFrame:
    """
    Carga datos desde el contenido en bytes de un archivo TSV a un DataFrame de pandas.

    :param file_content: Contenido del archivo TSV en bytes.
    :param config: Configuración opcional para la lectura del CSV.
    :return: DataFrame de pandas con los datos cargados.
    :raises: Exception para errores de decodificación o lectura.
    """
    config = config or {}
    try:
        content_str = file_content.decode('utf-8')
        # Corregido: usar '\t' como separador y especificar el motor de python
        df = pd.read_csv(io.StringIO(content_str), sep='\t', engine='python', **config)
        return df
    except UnicodeDecodeError as e:
        raise Exception(f"Error de codificación al procesar el archivo TSV. Se esperaba UTF-8. Error: {e}")
    except Exception as e:
        raise Exception(f"Error al leer el contenido del archivo TSV: {e}")
