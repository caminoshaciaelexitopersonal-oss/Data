# backend/logger.py
from typing import List, Dict, Any

# Esta lista actuará como nuestro registro en memoria.
# En una aplicación de producción más avanzada, esto podría ser reemplazado
# por un sistema de registro más robusto (ej. escribir en un archivo, una base de datos, o un servicio como Loki).
executed_steps: List[Dict[str, Any]] = []

from datetime import datetime
import time

def log_step(
    description: str,
    code_snippet: str,
    llm_prompt: str = None,
    llm_response: str = None,
    execution_time_ms: float = None
):
    """
    Registra un paso de ejecución en el log en memoria, incluyendo detalles del LLM y tiempo.

    :param description: Descripción en lenguaje natural del paso.
    :param code_snippet: Fragmento de código Python ejecutado.
    :param llm_prompt: El prompt enviado al LLM para este paso (opcional).
    :param llm_response: La respuesta recibida del LLM (opcional).
    :param execution_time_ms: Tiempo de ejecución del paso en milisegundos (opcional).
    """
    timestamp = datetime.utcnow().isoformat()
    print(f"Logging step: {description}")

    log_entry = {
        "timestamp": timestamp,
        "descripcion": description,
        "codigo": code_snippet,
        "llm_prompt": llm_prompt,
        "llm_response": llm_response,
        "execution_time_ms": execution_time_ms
    }
    executed_steps.append(log_entry)

def get_logged_steps() -> List[Dict[str, Any]]:
    """
    Devuelve todos los pasos que han sido registrados.
    """
    return executed_steps

def clear_log():
    """
    Limpia el log de pasos. Esto debería llamarse al inicio de una nueva ejecución del agente.
    """
    print("Clearing execution log.")
    executed_steps.clear()
