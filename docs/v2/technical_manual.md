# Manual Técnico v2

Este manual proporciona detalles técnicos para desarrolladores y administradores de sistemas.

## Configuración del Entorno

...

## Despliegue

...

## Nuevos Endpoints

### `/export/environment` (POST)
- **Descripción:** Inicia la exportación de un ambiente de trabajo.
- **Request Body:** `{ "job_id": "string", "mlflow_run_id": "string" (opcional) }`
- **Response:** Un archivo `application/zip`.

### `/validation/run` (POST)
- **Descripción:** Ejecuta reglas de validación sobre un conjunto de datos.
- **Request Body:** `{ "data": [...], "rules": [...] }`
- **Response:** Un JSON con el estado de la validación y los errores.

## Ejecución de Pruebas Avanzadas

- **Backend:** `pytest backend/tests_advanced/`
- **Frontend:** `npx playwright test frontend/tests/playwright/`
