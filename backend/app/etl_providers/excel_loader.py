import pandas as pd
import io
from typing import Dict, Any

def load_excel(file_content: bytes) -> Dict[str, pd.DataFrame]:
    """
    Carga datos desde el contenido en bytes de un archivo Excel.
    Si el archivo tiene múltiples hojas, las devuelve todas como un diccionario de DataFrames.

    :param file_content: Contenido del archivo Excel en bytes.
    :return: Un diccionario donde las claves son los nombres de las hojas y los valores son los DataFrames.
    :raises: Exception para errores de lectura.
    """
    try:
        # Usar BytesIO para leer el contenido binario directamente.
        # sheet_name=None le dice a pandas que cargue todas las hojas.
        excel_sheets = pd.read_excel(io.BytesIO(file_content), sheet_name=None)
        return excel_sheets
    except Exception as e:
        raise Exception(f"Error al leer el contenido del archivo Excel: {e}")
