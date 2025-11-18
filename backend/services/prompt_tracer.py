import json
import os
from datetime import datetime
from uuid import uuid4
from typing import Dict, Any

LOG_DIR = "data/logs/prompts"
os.makedirs(LOG_DIR, exist_ok=True)

class PromptTracerService:
    """
    Servicio para registrar la traza de interacciones con el agente (prompts y respuestas).
    """
    def log_trace(self, session_id: str, user_prompt: str, agent_response: Any, metadata: Dict[str, Any] = None) -> str:
        """
        Registra una nueva traza de prompt en un archivo JSON.

        Args:
            session_id (str): El ID de la sesión del usuario.
            user_prompt (str): El prompt enviado por el usuario.
            agent_response (Any): La respuesta generada por el agente.
            metadata (Dict[str, Any], optional): Metadatos adicionales (ej. modelo usado, latencia).

        Returns:
            str: El ID de la traza registrada.
        """
        trace_id = str(uuid4())
        trace_data = {
            "trace_id": trace_id,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user_prompt": user_prompt,
            "agent_response": agent_response,
            "metadata": metadata or {}
        }

        file_path = os.path.join(LOG_DIR, f"{session_id}_{trace_id}.json")
        try:
            with open(file_path, "w") as f:
                json.dump(trace_data, f, indent=4)
        except Exception as e:
            # En una aplicación real, usar un sistema de logging más robusto
            print(f"Error al registrar la traza del prompt: {e}")

        return trace_id
