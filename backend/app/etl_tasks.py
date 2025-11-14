from backend.celery_worker import celery_app
from backend.app.services.etl_multisource_service import run_etl_pipeline
from typing import Dict, Any

@celery_app.task(name='app.run_etl_pipeline_task')
def run_etl_pipeline_task(config: Dict[str, Any]) -> str:
    """
    Tarea de Celery para ejecutar el pipeline ETL multi-fuente de forma asíncrona.

    :param config: El diccionario de configuración para el trabajo ETL.
    :return: El resultado de la ejecución del pipeline (mensaje de éxito o error).
    """
    try:
        result_message = run_etl_pipeline(config)
        return result_message
    except Exception as e:
        # Celery manejará el rastreo de la excepción.
        # Opcionalmente, se puede registrar de nuevo aquí o realizar acciones de limpieza.
        return f"La tarea ETL falló: {e}"
