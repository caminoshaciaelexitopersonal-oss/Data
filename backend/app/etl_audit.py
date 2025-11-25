import json
import os
from datetime import datetime
from typing import Dict, Any

# --- Constantes ---
LOG_DIRECTORY = "data/logs"
LOG_FILE_PATH = os.path.join(LOG_DIRECTORY, "etl_log.json")

# --- Lógica del Logger de Auditoría ETL ---

def log_etl_event(message: str, level: str = 'info', extra_data: Dict[str, Any] = None) -> None:
    """
    Registra un evento del pipeline ETL en un archivo de log estructurado.

    El formato de log es JSON Lines, donde cada línea es un objeto JSON válido.

    :param message: El mensaje de log a registrar.
    :param level: El nivel del log (e.g., 'info', 'warning', 'error').
    :param extra_data: Un diccionario opcional para añadir campos estructurados al log.
    """
    try:
        # 1. Asegurar que el directorio de logs existe
        os.makedirs(LOG_DIRECTORY, exist_ok=True)

        # 2. Construir el registro de log
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "data": extra_data or {}
        }

        # 3. Escribir el registro en el archivo
        # Se usa 'a' para añadir al final del archivo (append)
        with open(LOG_FILE_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n') # Corregido: '\n' en lugar de '\\n'

    except Exception as e:
        # Si el logging falla, imprimir el error a la salida estándar/stderr
        # para no interrumpir el flujo principal de la aplicación.
        print(f"ALERTA: No se pudo escribir en el log de auditoría ETL en {LOG_FILE_PATH}: {e}")
