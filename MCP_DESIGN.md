# Diseño del Main Control Plane (MCP) - v2

Este documento describe el diseño y las responsabilidades del Main Control Plane (MCP) para el sistema SADI, revisado y ampliado según la directriz de verificación de la Fase 2.

## 1. Propósito del MCP

(Sin cambios)

## 2. Responsabilidades Centralizadas en el MCP

(Sin cambios)

## 3. Flujos de Comunicación Detallados

**Flujo 1: Análisis Completo (ETL, EDA, Modelo, Reporte)**

1.  **Frontend -> MCP:** `POST /mcp/sessions/` (con datos).
2.  **MCP -> MPA-Ingestión:** Procesa los datos.
3.  **MCP:** Crea una `Session` y un `JobID`, almacena los datos iniciales.
4.  **Frontend -> MCP:** `POST /mcp/sessions/{id}/etl` (con pasos de ETL).
5.  **MCP -> MPA-ETL:** Ejecuta el pipeline.
6.  **MCP:** Actualiza los datos de la sesión.
7.  **Frontend -> MCP:** `POST /mcp/sessions/{id}/analysis/eda`.
8.  **MCP -> MPA-EDA:** Genera el informe EDA.
9.  **MCP:** Almacena el informe EDA como un artefacto de la sesión.
10. **Frontend -> MCP:** `POST /mcp/sessions/{id}/chat` (p. ej., "Entrena un modelo de clasificación").
11. **MCP -> MPA-Análisis (Agente):**
12. **MPA-Análisis -> LLM Router:** Selecciona el modelo de IA apropiado.
13. **MPA-Análisis -> MPA-Modelo:** El agente invoca la herramienta de entrenamiento de modelos.
14. **MPA-Modelo -> MLflow:** Registra el experimento y el modelo.
15. **MCP:** Almacena el `run_id` de MLflow y otros resultados como artefactos.
16. **Frontend -> MCP:** `GET /mcp/sessions/{id}/report/download`.
17. **MCP -> MPA-Reportes:** Genera el informe final.
18. **MCP -> Audit Logger:** Cada paso del flujo registra una entrada de auditoría con el `JobID` y `SessionID` para trazabilidad.

## 4. Entidades de Datos Críticas

El MCP gestionará las siguientes entidades de datos:

-   **Session:** El estado de una sesión de análisis de un usuario. Contiene los datos actuales y metadatos.
-   **Job:** Una operación completa y atómica (p. ej., un flujo WPA). Tiene un `job_id` para trazabilidad.
-   **Step:** Una operación individual dentro de un Job (p. ej., un paso de ETL, una llamada al LLM).
-   **Dataset:** Representa los datos cargados, incluyendo metadatos (nombre, fuente, esquema).
-   **Artifact:** Un producto generado durante un Job (p. ej., un gráfico, un modelo entrenado, un informe).
-   **AuditLog:** Un registro inmutable de cada acción realizada en el sistema, vinculado a un `Job` y `Session`.
-   **Model:** Representa un modelo de ML entrenado, con referencias a su `run_id` en MLflow.
-   **Report:** El informe final generado.

## 5. Esquemas de Datos (schemas.py)

Las entidades anteriores se reflejarán en los esquemas de Pydantic, que incluirán campos para la trazabilidad como `session_id` y `job_id`.
