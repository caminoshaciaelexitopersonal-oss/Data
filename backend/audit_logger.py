import json
import os
from datetime import datetime
from hashlib import sha256
import difflib
from typing import List, Dict, Any
import pandas as pd

# --- Configuration ---
LOG_FILE_PATH = os.path.join('data', 'logs', 'audit_log.json')
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

def _calculate_dataframe_hash(df: pd.DataFrame) -> str:
    """Calculates a SHA256 hash of the dataframe's content."""
    # The hash is based on the JSON representation of the dataframe
    # to ensure consistency.
    df_json = df.to_json(orient='records', date_format='iso')
    return sha256(df_json.encode()).hexdigest()

def log_data_ingestion(
    source_type: str,
    source_identifier: str,
    user_or_agent: str,
    data: pd.DataFrame
):
    """
    Logs a data ingestion event to the audit trail.

    :param source_type: The type of the data source (e.g., 'file_upload', 'mongodb').
    :param source_identifier: The name of the source (e.g., filename, collection name).
    :param user_or_agent: The entity responsible for the ingestion.
    :param data: The pandas DataFrame that was ingested.
    """
    if data.empty:
        return # Do not log empty dataframes

    log_entry = {
        "event_id": sha256(f"{datetime.utcnow().isoformat()}{source_identifier}".encode()).hexdigest(),
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": "data_ingestion",
        "user_or_agent": user_or_agent,
        "source": {
            "type": source_type,
            "identifier": source_identifier,
        },
        "data_details": {
            "row_count": len(data),
            "column_count": len(data.columns),
            "columns": list(data.columns),
            "data_hash": _calculate_dataframe_hash(data),
        }
    }

    try:
        logs = []
        if os.path.exists(LOG_FILE_PATH) and os.path.getsize(LOG_FILE_PATH) > 0:
            try:
                with open(LOG_FILE_PATH, 'r') as f:
                    content = f.read()
                    if content.strip():
                        logs = json.loads(content)
                    else:
                        logs = []

                if not isinstance(logs, list):
                    raise json.JSONDecodeError("Log file does not contain a JSON list.", content, 0)

            except json.JSONDecodeError as e:
                print(f"Audit log file at '{LOG_FILE_PATH}' is corrupted. Backing it up. Error: {e}")
                backup_path = LOG_FILE_PATH + '.bak'
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                os.rename(LOG_FILE_PATH, backup_path)
                logs = []

        logs.append(log_entry)

        with open(LOG_FILE_PATH, 'w') as f:
            json.dump(logs, f, indent=4)

    except IOError as e:
        print(f"Error writing to audit log: {e}")


# --- Sistema de LOCK Lógico ---

PROTECTED_FILES = {
    "backend/main.py",
    "backend/celery_worker.py",
    "docker-compose.yml",
    "App.tsx",
    "package.json",
    "backend/requirements.txt",
    "backend/audit_logger.py"  # Proteger este mismo archivo
}

class ProtectedFileError(Exception):
    """Excepción personalizada para intentos de modificar archivos protegidos."""
    pass

def verify_path_is_not_protected(filepath: str):
    """
    Verifica si una ruta de archivo está en la lista de protegidos.
    Lanza una excepción ProtectedFileError si la ruta está protegida.
    """
    if filepath in PROTECTED_FILES:
        raise ProtectedFileError(
            f"Operación denegada. El archivo '{filepath}' está protegido por el sistema de LOCK lógico."
        )

# --- Fin del Sistema de LOCK Lógico ---


# --- Verificador de Diferencias (Diff Checker) ---

class DestructiveChangeError(Exception):
    """Excepción para cambios que eliminan código de forma no autorizada."""
    pass

def verify_change_is_not_destructive(
    filepath: str,
    original_content: str,
    new_content: str,
    deletion_threshold: int = 10
):
    """
    Analiza un 'diff' entre el contenido original y el nuevo.
    Lanza una excepción si el cambio se considera destructivo (elimina más líneas de las que añade).
    """
    diff = list(difflib.unified_diff(
        original_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=f"a/{filepath}",
        tofile=f"b/{filepath}",
    ))

    # Contar líneas eliminadas y añadidas
    deletions = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
    additions = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))

    net_change = additions - deletions

    # Lógica de seguridad:
    # Si hay más eliminaciones que adiciones, y el número de eliminaciones supera un umbral,
    # se considera un cambio destructivo.
    if net_change < 0 and deletions > deletion_threshold:
        raise DestructiveChangeError(
            f"Operación denegada en '{filepath}'. El cambio propuesto elimina {deletions} "
            f"líneas y solo añade {additions}, lo cual se considera una modificación destructiva. "
            "Se requiere autorización explícita para eliminar código."
        )

# --- Fin del Verificador de Diferencias ---
