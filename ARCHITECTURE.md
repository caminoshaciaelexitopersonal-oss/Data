# Documento de Arquitectura de SADI

Este documento define la arquitectura y las convenciones de nomenclatura para el Sistema de Analítica de Datos Inteligente (SADI).

## 1. Estructura de Carpetas (Directorio Raíz)

- **/backend**: Contiene toda la lógica del lado del servidor (API de FastAPI).
- **/frontend**: Contiene toda la lógica del lado del cliente (Aplicación React).
- **/data**: Almacena datos utilizados por la aplicación, incluyendo logs de auditoría. Es ignorado por Git.
- **/infra**: Contiene la configuración de infraestructura como código (Docker, Kubernetes, etc.).
- **/docs**: Almacena toda la documentación del proyecto (manuales, diagramas).

## 2. Arquitectura del Backend

El backend sigue una arquitectura de servicios modular.

- **/backend/api**: Contendrá los endpoints de FastAPI, organizados por recurso. (Ej: `endpoints/data_sources.py`, `endpoints/analysis.py`).
- **/backend/core**: Lógica de negocio central, incluyendo el agente de IA.
- **/backend/llm**: Módulo para la integración con múltiples Modelos de Lenguaje Grandes (LLMs).
- **/backend/services**: Servicios específicos como `etl_service.py`, `reporting_service.py`.
- **/backend/models**: Definiciones de modelos de datos (Pydantic).
- **/backend/utils**: Funciones de utilidad compartidas.
- **/backend/tests**: Pruebas unitarias y de integración.

### Convenciones de Nombres (Backend)

- **Módulos**: `nombre_en_minusculas_con_guiones_bajos.py` (ej: `audit_logger.py`).
- **Clases**: `PascalCase` (ej: `AnalysisTool`).
- **Funciones**: `snake_case` (ej: `run_linear_regression`).
- **Variables**: `snake_case`.

## 3. Arquitectura del Frontend

El frontend seguirá una estructura basada en características (feature-based).

- **/frontend/src/features**: Cada característica principal (ej: `chat`, `dashboard`, `data_loader`) tendrá su propio directorio.
  - **/feature_name/components**: Componentes de React específicos de la característica.
  - **/feature_name/hooks**: Hooks de React específicos.
  - **/feature_name/services**: Lógica para interactuar con la API.
  - **/feature_name/state**: Lógica de estado (reducers, slices).
- **/frontend/src/components**: Componentes de UI compartidos y genéricos.
- **/frontend/src/services**: Servicios globales (ej: `api_client.ts`).
- **/frontend/src/hooks**: Hooks globales.
- **/frontend/src/tests**: Pruebas de extremo a extremo con Playwright.

### Convenciones de Nombres (Frontend)

- **Archivos/Componentes**: `PascalCase.tsx` (ej: `ChatView.tsx`).
- **Funciones/Hooks**: `camelCase` (ej: `useSpeechRecognition`).
- **Variables**: `camelCase`.
- **Estilos**: Se utilizará Tailwind CSS.

## 4. Flujo de Datos del Agente

1.  **Recepción**: El endpoint de la API recibe la solicitud del usuario.
2.  **Enrutamiento LLM**: Se selecciona el LLM a través del `llm_router`.
3.  **Planificación**: El `planner` del agente de LangChain crea un plan de ejecución.
4.  **Ejecución**: El `executor` ejecuta las herramientas (`tools.py`) secuencialmente.
5.  **Auditoría y Logging**: Cada paso significativo se registra.
6.  **Respuesta**: Se ensambla la respuesta y se devuelve al cliente.
