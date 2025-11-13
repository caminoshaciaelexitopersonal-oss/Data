# backend/logger.py
from typing import List, Dict, Any

# Esta lista actuará como nuestro registro en memoria.
# En una aplicación de producción más avanzada, esto podría ser reemplazado
# por un sistema de registro más robusto (ej. escribir en un archivo, una base de datos, o un servicio como Loki).
executed_steps: List[Dict[str, Any]] = []

def log_step(description: str, code_snippet: str):
    """
    Registra un paso de ejecución en el log en memoria.

    :param description: Una descripción en lenguaje natural de lo que hace el paso.
    :param code_snippet: El fragmento de código Python real que se ejecutó.
    """
    print(f"Logging step: {description}") # Log para debugging en el servidor
    executed_steps.append({
        "descripcion": description,
        "codigo": code_snippet
    })

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
