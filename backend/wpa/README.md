# Workflow Process Automation (WPA)

Este directorio contiene módulos responsables de orquestar flujos de trabajo de análisis complejos y automatizados.

## Módulos

-   **`auto_analysis/`**: Contiene el flujo de trabajo principal para el análisis automatizado de datos, expuesto a través de una API.
-   **(Latente) Sistema de Tareas Asíncronas (Celery)**: El sistema incluye un worker de Celery (`backend/celery_worker.py`) configurado para ejecutar tareas de forma asíncrona, utilizando Redis como broker de mensajes. Las definiciones de tareas se encuentran en `backend/app/etl_tasks.py`.

    **Estado Actual:** Esta capacidad está completamente configurada y desplegada, pero actualmente no es invocada por ninguna de las APIs expuestas en el `unified_router`. Está diseñada para ser utilizada en futuros flujos de trabajo que requieran un procesamiento de datos pesado y de larga duración (ej. pipelines de ETL complejos, entrenamiento de modelos a gran escala) sin bloquear las respuestas de la API.
