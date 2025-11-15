# Sistema de Analítica de Datos Inteligente (SADI)

SADI es una plataforma de IA interactiva diseñada para el análisis de datos avanzado. Permite a los usuarios cargar datos desde diversas fuentes, realizar análisis exploratorios, entrenar modelos de machine learning y generar informes profesionales, todo a través de una interfaz conversacional.

## Arquitectura

El sistema está construido con una arquitectura de microservicios contenerizada, orquestada con Docker Compose.

-   **Frontend:** Una aplicación de una sola página (SPA) construida con **React**, **TypeScript** y **Vite**. Utiliza **Tailwind CSS** para el estilo y **Recharts** para las visualizaciones de datos.
-   **Backend:** Una API de **FastAPI** (Python) que sirve como el cerebro del sistema.
-   **Agente de IA:** Un agente inteligente basado en `langchain`, utilizando el patrón **Plan-and-Execute** para interpretar las solicitudes del usuario y orquestar las tareas.
-   **Motor Asíncrono:** Utiliza **Celery** con **Redis** como broker para ejecutar tareas de larga duración (ETL, entrenamiento de modelos) sin bloquear la interfaz de usuario.
-   **MLOps:** Integrado con **MLflow** para el seguimiento de experimentos de machine learning, registro de modelos, parámetros y métricas.
-   **Monitoreo:** Incluye **Prometheus** y **Grafana** para el monitoreo de la salud y el rendimiento de los servicios.

## Características Principales

-   **Ingesta de Datos Multi-fuente:** Carga de datos desde archivos (CSV, Excel, JSON), bases de datos SQL, MongoDB y S3.
-   **Agente Conversacional:** Interactúa con el sistema usando lenguaje natural.
-   **Análisis Exploratorio de Datos (EDA) Avanzado:** Genera automáticamente estadísticas, histogramas, diagramas de caja y mapas de calor de correlación.
-   **Machine Learning Integrado:** Entrena y evalúa modelos como Regresión Lineal, Clasificación (Random Forest) y Clustering (K-Means).
-   **Dashboard Interactivo:** Visualiza los resultados de los análisis en un Panel de Visualización Analítica (PVA) con gráficos interactivos.
-   **Generación de Informes:** Exporta los hallazgos a informes profesionales en formato `.docx` y `.pdf`.
-   **Transparencia de Código (SADI):** Permite a los usuarios ver y exportar el código Python exacto que el agente ejecutó en cada paso.
-   **Soporte MULTI-LLM:** Capacidad para cambiar dinámicamente entre diferentes motores de IA (Gemini, OpenAI, Ollama) directamente desde la interfaz.

## Cómo Ejecutar Localmente

**Prerrequisitos:**
-   Docker y Docker Compose
-   Tener un terminal de línea de comandos (como Bash, Zsh, etc.).

**Pasos:**

1.  **Clonar el Repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd <NOMBRE_DEL_REPOSITORIO>
    ```

2.  **Configurar Variables de Entorno:**
    -   Renombra el archivo `.env.development.example` a `.env.development`.
    -   Abre el archivo `.env.development` y añade tus claves de API para los servicios que desees utilizar (ej. `GOOGLE_API_KEY`).

3.  **Construir y Ejecutar los Contenedores:**
    ```bash
    docker-compose up --build -d
    ```
    Este comando construirá las imágenes de Docker para el frontend y el backend, y luego iniciará todos los servicios en segundo plano.

4.  **Acceder a la Aplicación:**
    -   **Frontend:** Abre tu navegador y ve a `http://localhost:8080`.
    -   **Backend (Documentación de la API):** `http://localhost:8000/docs`.
    -   **MLflow:** `http://localhost:5000`.
    -   **Grafana:** `http://localhost:3001`.

## Ejecución de Pruebas

-   **Backend (Pytest):**
    Para ejecutar la suite de pruebas del backend, asegúrate de que las dependencias estén instaladas y luego ejecuta:
    ```bash
    docker-compose exec backend python3 -m pytest
    ```

-   **Frontend (Playwright):**
    (Instrucciones para configurar y ejecutar pruebas de Playwright irían aquí una vez que el framework esté completamente integrado).
