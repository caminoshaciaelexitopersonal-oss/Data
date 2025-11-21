# Frontend

## 1. Propósito de esta carpeta

Esta carpeta contiene todo el código fuente de la aplicación de frontend SADI. Es una aplicación de una sola página (SPA) construida con React y TypeScript, utilizando Vite como herramienta de construcción. Su responsabilidad es proporcionar la interfaz de usuario, gestionar la interacción con el usuario y comunicarse con el backend a través de su API RESTful.

## 2. Estructura interna

La estructura de archivos es no estándar, con componentes y lógica de negocio ubicados en el directorio raíz:

-   `/components`: Contiene los componentes reutilizables de React que conforman la interfaz de usuario.
-   `/features`: Contiene componentes de mayor nivel que encapsulan funcionalidades específicas (ej. Calidad de Datos, Trazabilidad de Prompts).
-   `/services`: Lógica para la comunicación con APIs externas y servicios del lado del cliente. **Nota: Contiene archivos heredados vacíos.**
-   `/store`: Contiene la lógica de gestión de estado global, implementada con Zustand.
-   `App.tsx`: El componente raíz de la aplicación que orquesta las vistas principales.
-   `index.tsx`: El punto de entrada de la aplicación que renderiza el componente `App`.
-   `vite.config.ts`: Archivo de configuración para el servidor de desarrollo y la herramienta de construcción Vite.
-   `package.json`: Define las dependencias de Node.js y los scripts del proyecto.

## 3. Flujos principales

1.  **Flujo de Carga de Datos:** El usuario selecciona un archivo a través de `DataSourceModal`, que es enviado al endpoint `/mpa/ingestion/upload-file/` del backend.
2.  **Flujo de Interacción con el Chat:** El usuario interactúa con `ChatView`, que envía prompts al backend. El estado de la conversación se actualiza en tiempo real.
3.  **Visualización de Datos:** Componentes como `VisualAnalyticsBoard` obtienen datos procesados del backend para renderizar gráficos y tablas.

## 4. Reglas y convenciones del módulo

-   La gestión de estado global debe realizarse a través del store de Zustand para mantener la lógica de negocio desacoplada de los componentes.
-   Las llamadas a la API deben centralizarse y gestionar la URL base a través de variables de entorno (`VITE_API_BASE_URL`).
-   Se utiliza TypeScript para asegurar la tipificación estática y reducir errores.

## 5. Consideraciones de seguridad

-   **CRÍTICO:** Ninguna clave de API debe ser almacenada o expuesta en este código. La `GEMINI_API_KEY` debe ser eliminada de `vite.config.ts` y gestionada a través de un endpoint proxy en el backend.
-   Todas las variables de entorno inyectadas en el cliente (con prefijo `VITE_`) son públicamente visibles. No deben contener información sensible.

## 6. Cambios relevantes

-   **Q4 2025:** Se identificó una vulnerabilidad de seguridad crítica por exposición de API Key en `vite.config.ts`.
-   **Q4 2025:** Se detectó una desincronización masiva de endpoints con la nueva arquitectura del backend.
