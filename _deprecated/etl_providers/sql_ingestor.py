import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, Any

def ingest_from_sql(db_uri: str, query: str, config: Dict[str, Any] = None) -> pd.DataFrame:
    """
    Ingesta datos desde una base de datos SQL a un DataFrame de pandas.

    :param db_uri: URI de conexión a la base de datos (e.g., 'postgresql://user:password@host/dbname').
    :param query: Consulta SQL a ejecutar.
    :param config: Configuración opcional para pd.read_sql (e.g., index_col).
    :return: DataFrame de pandas con los resultados de la consulta.
    :raises: SQLAlchemyError para errores de conexión o ejecución de la consulta.
    :raises: Exception para otros errores inesperados.
    """
    config = config or {}
    try:
        engine = create_engine(db_uri)
        with engine.connect() as connection:
            df = pd.read_sql(query, connection, **config)
        return df
    except SQLAlchemyError as e:
        raise SQLAlchemyError(f"Error de base de datos al ejecutar la consulta. URI: {db_uri}. Error: {e}")
    except Exception as e:
        raise Exception(f"Un error inesperado ocurrió durante la ingesta de SQL: {e}")
