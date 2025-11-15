# Documentación de la API de SADI

Esta documentación describe los endpoints principales de la API del backend de SADI.

**URL Base:** `http://localhost:8000`

---

## 1. Agente de IA

### `POST /chat/agent/`

Ejecuta el agente de IA `Plan-and-Execute` para procesar una solicitud en lenguaje natural.

-   **Cuerpo de la Solicitud (`application/json`):**
    ```json
    {
      "message": "string",
      "data": "array[object]",
      "llm_preference": "string | null"
    }
    ```
    -   `message`: La instrucción del usuario en lenguaje natural.
    -   `data`: El conjunto de datos actual sobre el que operar, como un array de objetos JSON.
    -   `llm_preference` (opcional): La preferencia del motor de IA ('gemini', 'openai', 'ollama'). Si no se proporciona, se usa el predeterminado.

-   **Respuesta Exitosa (`200 OK`):**
    ```json
    {
      "output": "string"
    }
    ```
    -   `output`: La respuesta final del agente en texto plano o un objeto JSON si devuelve un artefacto (ej. un gráfico).

---

## 2. Artefactos y Logs

### `GET /get-steps`

Obtiene la lista de todos los pasos ejecutados por el agente durante la última operación, incluyendo descripciones y fragmentos de código.

-   **Respuesta Exitosa (`200 OK`):**
    ```json
    {
      "steps": [
        {
          "timestamp": "string (ISO 8601)",
          "descripcion": "string",
          "codigo": "string",
          "llm_prompt": "string | null",
          "llm_response": "string | null",
          "execution_time_ms": "number | null"
        }
      ]
    }
    ```

### `GET /export/code`

Descarga un archivo `.zip` que contiene todos los fragmentos de código de la última ejecución del agente.

-   **Respuesta Exitosa (`200 OK`):**
    -   **Tipo de Contenido:** `application/zip`
    -   **Cuerpo:** El archivo binario `.zip`.

### `GET /audit-log`

Obtiene el registro de auditoría completo, con los eventos más recientes primero.

-   **Respuesta Exitosa (`200 OK`):**
    Un array de objetos JSON, donde cada objeto representa un evento de auditoría (ej. ingesta de datos).

---

## 3. Informes y Visualizaciones

### `GET /download-report`

Descarga el informe analítico profesional generado.

-   **Parámetros de Consulta:**
    -   `format` (opcional): Especifica el formato del informe. Puede ser `docx` (predeterminado) o `pdf`.

-   **Respuesta Exitosa (`200 OK`):**
    -   **Tipo de Contenido:** `application/vnd.openxmlformats-officedocument.wordprocessingml.document` (para DOCX) o `application/pdf` (para PDF).
    -   **Cuerpo:** El archivo binario del informe.

### `GET /api/visualizations`

Obtiene los datos necesarios para renderizar todos los gráficos en el Panel de Visualización Analítica (PVA).

-   **Respuesta Exitosa (`200 OK`):**
    Un objeto JSON donde cada clave es el nombre de una visualización y su valor son los datos para el gráfico.

---

## 4. Ingesta de Datos

La API incluye varios endpoints para la carga de datos, tales como:
-   `POST /upload-data/`
-   `POST /load-from-db/`
-   `POST /load-from-mongodb/`
-   `POST /load-from-s3/`

Todos ellos reciben la configuración de conexión o el archivo correspondiente y devuelven el conjunto de datos cargado como un array de objetos JSON.
