import pandas as pd
import requests
from typing import Dict, Any, List

def ingest_from_api(url: str, config: Dict[str, Any] = None) -> pd.DataFrame:
    """
    Ingesta datos desde una API a un DataFrame de pandas.

    :param url: URL del endpoint de la API.
    :param config: Configuración opcional para la solicitud (e.g., headers, params).
    :return: DataFrame de pandas con los datos obtenidos.
    :raises: requests.exceptions.RequestException para errores de red o HTTP.
    :raises: ValueError si la respuesta no es un JSON válido o está vacía.
    """
    config = config or {}
    try:
        response = requests.get(url, **config)
        response.raise_for_status()  # Lanza una excepción para códigos de estado 4xx/5xx

        data = response.json()

        if not data:
            raise ValueError("La respuesta JSON de la API está vacía.")

        # Asume que el JSON es una lista de objetos o un objeto que puede ser normalizado
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            # Intenta normalizar un objeto JSON anidado
            df = pd.json_normalize(data)

        return df
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Error durante la solicitud a la API {url}: {e}")
    except ValueError as e:
        raise ValueError(f"Error al procesar el JSON de la API {url}: {e}")
