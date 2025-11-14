import json
import hashlib
import os
from datetime import datetime
import pandas as pd

# La ruta debe ser relativa al directorio raíz del proyecto.
LOG_FILE_PATH = "data/logs/audit_log.json"

def ensure_log_directory_exists():
    """Crea el directorio de logs si no existe."""
    log_dir = os.path.dirname(LOG_FILE_PATH)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

def get_data_hash(data: pd.DataFrame) -> str:
    """Calcula el hash SHA256 del contenido de un DataFrame."""
    data_string = data.to_json(orient='records', date_format='iso', default_handler=str)
    return hashlib.sha256(data_string.encode('utf-8')).hexdigest()

def log_audit_record(
    file_name: str,
    data_df: pd.DataFrame,
    processed_by: str = "Agente SADI"
):
    """
    Registra un evento de carga de datos en el log de auditoría.

    :param file_name: Nombre del archivo o fuente de datos.
    :param data_df: El DataFrame de pandas con los datos cargados.
    :param processed_by: El agente o usuario que procesó el archivo.
    """
    if data_df.empty:
        print("Auditoría omitida: el DataFrame de datos está vacío.")
        return

    ensure_log_directory_exists()

    record = {
        "nombre_del_archivo": file_name,
        "fecha_hora": datetime.utcnow().isoformat() + "Z",
        "hash_del_dataset": get_data_hash(data_df),
        "tamaño_bytes": int(data_df.memory_usage(deep=True).sum()),
        "columnas_detectadas": list(data_df.columns),
        "procesado_por": processed_by
    }

    try:
        logs = []
        if os.path.exists(LOG_FILE_PATH):
            with open(LOG_FILE_PATH, 'r') as f:
                try:
                    logs = json.load(f)
                    if not isinstance(logs, list):
                        logs = []
                except json.JSONDecodeError:
                    # El archivo está vacío o corrupto, se sobreescribirá.
                    pass

        logs.append(record)
        with open(LOG_FILE_PATH, 'w') as f:
            json.dump(logs, f, indent=4)

        print(f"Registro de auditoría guardado para '{file_name}'")

    except Exception as e:
        print(f"Error al escribir en el log de auditoría: {e}")
