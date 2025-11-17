# Diseño del Main Control Plane (MCP)

Este documento describe el diseño y las responsabilidades del Main Control Plane (MCP) para el sistema SADI, como parte de la Fase 2 de la transformación arquitectónica a MCP + MPA + WPA.

## 1. Propósito del MCP

El MCP es el cerebro centralizado del sistema. Su propósito es:

-   **Orquestar la Comunicación:** Servir como el único punto de entrada para todas las solicitudes del frontend, eliminando las llamadas directas a servicios dispersos.
-   **Centralizar el Control:** Gestionar la lógica de negocio de alto nivel, el estado de las tareas y la seguridad.
-   **Desacoplar Componentes:** Actuar como una capa de abstracción entre el frontend y los Módulos de Proceso (MPA), permitiendo que los módulos evolucionen de forma independiente.

## 2. Responsabilidades Centralizadas en el MCP

El MCP asumirá la orquestación de las siguientes responsabilidades, que actualmente están distribuidas en varios endpoints y servicios:

1.  **Orquestación del Ciclo de Vida del Análisis:**
    *   Gestionar el flujo completo de una sesión de análisis, desde la carga de datos hasta la generación de informes.
    *   Mantener el estado de la sesión (p. ej., datos cargados, transformaciones aplicadas).

2.  **Ingesta de Datos Unificada:**
    *   Proporcionar un único endpoint para la ingesta de datos, ya sea desde archivos o bases de datos.
    *   Invocar al futuro **MPA-Ingestión** para manejar los detalles de la carga y el parsing.

3.  **Ejecución de Pipelines ETL:**
    *   Recibir solicitudes para ejecutar transformaciones de datos.
    *   Llamar al futuro **MPA-ETL** para aplicar los pasos del pipeline.

4.  **Procesamiento del Agente de IA:**
    *   Recibir las consultas del usuario (`/chat/agent`).
    *   Invocar al `agent_executor` y gestionar la interacción con el LLM y sus herramientas. Esta será la responsabilidad principal del **MPA-Análisis**.

5.  **Generación y Recuperación de Artefactos:**
    *   Orquestar la creación de informes, visualizaciones y exportaciones de código.
    *   Gestionar las llamadas a los futuros **MPA-Informes** y **MPA-Visualización**.
    *   Proporcionar endpoints unificados para que el frontend recupere estos artefactos.

6.  **Análisis Especializados:**
    *   Exponer endpoints para análisis específicos como el EDA y el PCA, que a su vez invocarán a los **MPA-EDA** y **MPA-PCA**.

## 3. Flujos de Comunicación a Orquestar

El MCP gestionará los siguientes flujos de comunicación:

**Flujo 1: Sesión de Análisis Típica**

1.  **Frontend -> MCP:** `POST /mcp/session/start` (con datos de archivo o DB).
2.  **MCP -> MPA-Ingestión:** `process_data(...)`.
3.  **MPA-Ingestión -> MCP:** Devuelve el DataFrame inicial.
4.  **MCP:** Almacena el DataFrame en el estado de la sesión.
5.  **Frontend -> MCP:** `POST /mcp/session/{session_id}/chat` (con una pregunta del usuario).
6.  **MCP -> MPA-Análisis:** `execute_agent(question, data)`.
7.  **MPA-Análisis -> (MPA-EDA, MPA-PCA, etc.):** El agente utiliza sus herramientas.
8.  **MPA-Análisis -> MCP:** Devuelve la respuesta del agente y los artefactos generados (visualizaciones, etc.).
9.  **MCP:** Actualiza el estado de la sesión.
10. **Frontend -> MCP:** `GET /mcp/session/{session_id}/artifacts`.
11. **MCP:** Devuelve los artefactos de la sesión.

**Flujo 2: Generación de Informe Final**

1.  **Frontend -> MCP:** `POST /mcp/session/{session_id}/generate_report`.
2.  **MCP -> MPA-Informes:** `create_report(summary, artifacts)`.
3.  **MPA-Informes -> MCP:** Devuelve la ruta al archivo del informe.
4.  **MCP -> Frontend:** Proporciona un enlace de descarga.

## 4. Entidades de Datos Principales

El MCP operará sobre las siguientes entidades de datos, definidas en `schemas.py`:

-   `DbConnectionRequest`: Para la ingesta desde bases de datos.
-   `PipelineRequest`: Para la ejecución de pipelines de ETL.
-   `ChatRequest`: Para las interacciones con el agente de IA.

El MCP introducirá una nueva entidad `Session` para gestionar el estado a lo largo del tiempo.
