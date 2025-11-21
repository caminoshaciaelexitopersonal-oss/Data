# Backend

## 1. Propósito de esta carpeta

Esta carpeta contiene todo el código fuente del servidor SADI. Es responsable de la lógica de negocio, el procesamiento de datos, la gestión de modelos de machine learning, la comunicación con la base de datos y la exposición de la API RESTful para el frontend.

## 2. Estructura interna

La arquitectura del backend sigue el patrón **MCP + MPA + WPA**:

-   `/mcp` (Main Control Plane): Orquesta las sesiones y los trabajos de alto nivel.
-   `/mpa` (Modular Process Architecture): Contiene los módulos de proceso de negocio encapsulados (ej. Ingesta, EDA, Calidad de Datos).
-   `/wpa` (Workflow Process Automation): Contiene flujos de trabajo automatizados que orquestan llamadas a los MPA para ejecutar tareas complejas.
-   `/app`: Código heredado y servicios centrales en proceso de migración.
-   `/audit`: Servicio de auditoría centralizado para el logging de eventos críticos.
-   `/llm`: Lógica para la integración y enrutamiento de modelos de lenguaje (LLMs).
-   `/middleware`: Middlewares personalizados para la aplicación FastAPI.
-   `/tests`: Pruebas unitarias y de integración para asegurar la calidad del código.
-   `app_factory.py`: Punto de entrada que construye y configura la aplicación FastAPI.
-   `celery_worker.py`: Define el trabajador Celery para la ejecución de tareas asíncronas.
-   `requirements.in` / `requirements.txt`: Archivos de gestión de dependencias de Python.

## 3. Flujos principales

1.  **Flujo de Ingesta:** El frontend envía un archivo al endpoint de `/mpa/ingestion`. El servicio de ingestión procesa el archivo, lo valida y lo almacena.
2.  **Flujo de Análisis (WPA):** Una solicitud de análisis inicia un flujo en el WPA, que a su vez llama a diferentes MPAs (EDA, Calidad, etc.) para realizar el análisis.
3.  **Tareas Asíncronas:** Tareas pesadas como el entrenamiento de modelos son delegadas a Celery y se ejecutan en segundo plano por el `worker`.

## 4. Reglas y convenciones del módulo

-   Todo el código nuevo debe seguir la arquitectura MCP + MPA + WPA.
-   Las dependencias deben gestionarse a través de `pip-tools` (`requirements.in`).
-   Las pruebas unitarias son obligatorias para la nueva funcionalidad.
-   El versionado de Python debe ser **3.12**.

## 5. Consideraciones de seguridad

-   Las claves de API y otros secretos NUNCA deben estar hardcodeados. Deben ser gestionados a través de variables de entorno.
-   Toda entrada del usuario debe ser validada y sanitizada. El `HardeningMiddleware` provee una capa inicial de protección.

## 6. Cambios relevantes

-   **Q4 2025:** Migración a la arquitectura MCP + MPA + WPA.
-   **Q4 2025:** Centralización del logging en el servicio de Auditoría.
