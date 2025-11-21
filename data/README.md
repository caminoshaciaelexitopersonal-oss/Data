# Data

## 1. Propósito de esta carpeta

Esta carpeta sirve como el repositorio central para todos los datos persistentes utilizados y generados por la aplicación SADI, excluyendo los artefactos de MLflow que tienen su propio volumen.

## 2. Estructura interna

-   `/logs`: Almacena logs estructurados generados por la aplicación.
    -   `audit_log.json`: Un log de eventos de auditoría importantes.
-   `/processed`: Contiene datos que han sido procesados por los flujos de trabajo de la aplicación.
    -   `/code_blocks`: Almacena los bloques de código ejecutados por el agente de IA para la funcionalidad "View Source Code". Cada ejecución se guarda en una subcarpeta con el `job_id`.
-   `/sessions`: (Directorio implícito, no versionado) Usado por el `SessionManager` para persistir DataFrames de Pandas entre diferentes flujos de WPA.

## 3. Flujos principales

-   **Flujo de Auditoría:** El `AuditService` en el backend escribe eventos significativos en `logs/audit_log.json`.
-   **Flujo de "View Source Code":** Cuando el agente de IA ejecuta una herramienta, el código correspondiente se guarda en `/processed/code_blocks/<job_id>/`.
-   **Flujo de Sesión WPA:** El `SessionManager` guarda y carga archivos pickle de DataFrames en el directorio `/data/sessions/` para compartir estado entre tareas.

## 4. Reglas y convenciones del módulo

-   No se deben subir datos sensibles o de clientes a este directorio en el repositorio de Git. Los archivos dentro de esta carpeta son para estructura, ejemplos o logs no sensibles.
-   Los datos de producción reales deben ser manejados a través de volúmenes de Docker y no ser versionados.

## 5. Consideraciones de seguridad

-   El contenido de `/logs` y `/processed` puede contener información sobre las operaciones realizadas. El acceso a estos directorios en un entorno de producción debe estar restringido.
-   Asegurarse de que los datos temporales o de sesión se limpien adecuadamente.

## 6. Cambios relevantes

-   **Q4 2025:** Se introdujo el directorio `processed/code_blocks` para dar soporte a la funcionalidad de trazabilidad de código.
