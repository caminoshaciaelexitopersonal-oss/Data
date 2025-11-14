import pandas as pd
import yaml
import json
from typing import Dict, Any

def load_yaml(file_content: bytes) -> pd.DataFrame:
    """
    Carga datos desde el contenido en bytes de un archivo YAML a un DataFrame.
    NOTA: Requiere la librería 'PyYAML'.

    :param file_content: Contenido del archivo YAML en bytes.
    :return: DataFrame de pandas con los datos cargados.
    :raises: Exception para errores de parseo o conversión.
    """
    try:
        # Usar PyYAML para parsear el contenido YAML
        yaml_data = yaml.safe_load(file_content)

        # Pandas puede normalizar datos JSON/dict directamente
        df = pd.json_normalize(yaml_data)

        return df
    except yaml.YAMLError as e:
        raise Exception(f"Error al parsear el contenido del archivo YAML: {e}")
    except Exception as e:
        raise Exception(f"Error al convertir los datos YAML a DataFrame: {e}")
