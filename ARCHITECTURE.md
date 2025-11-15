# Documento de Arquitectura de SADI

Este documento define la arquitectura y las convenciones de nomenclatura para el Sistema de Analítica de Datos Inteligente (SADI).

## 1. Estructura de Carpetas (Directorio Raíz)

-   `/` (Raíz): Contiene los archivos de configuración de Docker (`docker-compose.yml`), el `Dockerfile` del frontend, y los archivos fuente del frontend (`App.tsx`, `index.tsx`, `components/`).
-   `/backend`: Contiene toda la lógica del lado del servidor (API de FastAPI, tareas de Celery, servicios, etc.).
-   `/data`: Almacena datos utilizados por la aplicación, como los logs de auditoría. Es ignorado por Git.
-   `/store`: Contiene la lógica de estado del frontend (Zustand).
-   `/tests`: Contiene las pruebas de extremo a extremo (E2E) del frontend con Playwright.

## 2. Arquitectura del Backend

El backend sigue una arquitectura de servicios modular.

-   `/backend/main.py`: Punto de entrada principal de la aplicación FastAPI. Define los endpoints y la configuración del agente.
-   `/backend/llm`: Módulo para la integración con múltiples Modelos de Lenguaje Grandes (LLMs) a través de un router.
-   `/backend/services`: Contiene la lógica de negocio para funcionalidades específicas como EDA y PCA.
-   `/backend/app/services`: Contiene servicios relacionados con el ETL y la auditoría.
-   `/backend/app/export`: Módulo para la exportación de artefactos, como el código del agente.
-   `/backend/tests`: Pruebas unitarias y de integración del backend con Pytest.

### Convenciones de Nombres (Backend)

-   **Módulos**: `nombre_en_minusculas_con_guiones_bajos.py` (ej: `audit_logger.py`).
-   **Clases**: `PascalCase` (ej: `AnalysisTool`).
-   **Funciones**: `snake_case` (ej: `run_linear_regression`).
-   **Variables**: `snake_case`.

## 3. Arquitectura del Frontend

El frontend sigue una estructura basada en componentes y características.

-   `/components`: Contiene los componentes de React reutilizables (`ChatView`, `VisualAnalyticsBoard`, etc.).
-   `/store`: Maneja el estado global de la aplicación con Zustand.
-   `/services`: Contiene lógica para interactuar con APIs externas o realizar cálculos en el lado del cliente.
-   `/App.tsx`: Componente principal que ensambla la aplicación.

### Convenciones de Nombres (Frontend)

-   **Archivos/Componentes**: `PascalCase.tsx` (ej: `ChatView.tsx`).
-   **Funciones/Hooks**: `camelCase` (ej: `useSpeechRecognition`).
-   **Variables**: `camelCase`.
-   **Estilos**: Se utiliza Tailwind CSS.

## 4. Flujo de Datos del Agente

1.  **Recepción**: El endpoint `/chat/agent` en `main.py` recibe la solicitud del usuario, que incluye la preferencia de LLM.
2.  **Configuración Dinámica**: Se instancia el agente (`PlanAndExecute`) en tiempo real, configurándolo con el LLM seleccionado a través del `llm_router`.
3.  **Planificación**: El `planner` del agente crea un plan de ejecución.
4.  **Ejecución**: El `executor` ejecuta las herramientas (`@tool`) secuencialmente.
5.  **Logging y Auditoría**: Cada paso significativo se registra en el `logger` en memoria y en el `audit_log.json`.
6.  **Respuesta**: Se ensambla la respuesta final y se devuelve al cliente.

## 5. Flujo de Ingesta y ETL

1.  **Recepción**: Endpoints como `/upload-data` o `/load-from-db` reciben los datos.
2.  **Procesamiento**: Se utiliza `pandas` para convertir los datos a un DataFrame.
3.  **Auditoría**: Se llama a `log_data_ingestion` para registrar el evento.
4.  **Tareas Asíncronas**: Tareas pesadas como el procesamiento de múltiples archivos se delegan a `celery_worker.py`.
