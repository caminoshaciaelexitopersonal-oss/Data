# Informe Ampliado de Endpoints Faltantes y Rutas Desconectadas

## Objetivo
Este documento proporciona un análisis detallado de los endpoints del backend que son invocados por el frontend pero que no existen o no están registrados en la arquitectura actual, junto con su impacto y recomendaciones.

---

### 1. Endpoint del Agente de Chat (`/chat/agent/`)

- **Severidad:** **Crítica**
- **Endpoint Invocado:** `POST /chat/agent/`
- **Impacto Funcional:** Esta es la funcionalidad **principal** de la aplicación. Sin este endpoint, toda la capacidad de análisis conversacional y la interacción con la IA están completamente rotas. El usuario no puede hacer preguntas sobre sus datos.
- **Estado:** El router que contiene esta lógica no está siendo importado ni registrado en `app_factory.py`. El código probablemente existe pero está desconectado.
- **Recomendación Técnica:**
  1.  Localizar el archivo `api.py` que contiene el router del chat (probablemente en `backend/routers/` o una nueva carpeta `mpa/chat/`).
  2.  Importar el router en `backend/app_factory.py`.
  3.  Añadir `app.include_router(chat_router)` en la sección de routers de la fábrica de la aplicación.

---

### 2. Endpoint de Visualizaciones (`/api/visualizations`)

- **Severidad:** **Alta**
- **Endpoint Invocado:** `GET /api/visualizations`
- **Impacto Funcional:** El Panel de Analítica Avanzada (`VisualAnalyticsBoard`) está completamente vacío y no es funcional. No se puede mostrar ningún gráfico ni resultado de análisis.
- **Estado:** Este endpoint no existe en la nueva arquitectura. La lógica para generar y servir visualizaciones necesita ser refactorizada a un MPA.
- **Recomendación Técnica:**
  1.  Crear un nuevo módulo `backend/mpa/visualization/` con su `api.py` y `service.py`.
  2.  Migrar la lógica de generación de gráficos al nuevo `VisualizationService`.
  3.  Exponer un nuevo endpoint `GET /mpa/visualization/` y registrarlo en `app_factory.py`.
  4.  Actualizar la llamada en `VisualAnalyticsBoard.tsx` al nuevo endpoint.

---

### 3. Endpoints de Ingesta de Datos Adicionales

Los siguientes endpoints representan funcionalidades de ingesta de datos que existían en el frontend pero no tienen un backend correspondiente.

#### 3.1 Carga de Múltiples Archivos
- **Severidad:** **Media**
- **Endpoint Invocado:** `POST /upload/multi`
- **Impacto Funcional:** El usuario no puede subir y procesar múltiples archivos a la vez, limitando la eficiencia para análisis de lotes.
- **Recomendación Técnica:** Ampliar el `IngestionService` para que acepte una lista de `UploadFile`. Esto probablemente requerirá mover el procesamiento a una tarea de Celery en segundo plano para evitar timeouts.

#### 3.2 Conexión a MongoDB
- **Severidad:** **Media**
- **Endpoint Invocado:** `POST /load-from-mongodb/`
- **Impacto Funcional:** El usuario no puede conectar la aplicación a una base de datos MongoDB para analizar datos.
- **Recomendación Técnica:** Crear un nuevo módulo `backend/mpa/ingestion_mongodb/` y un servicio que utilice `pymongo` para conectar y ejecutar consultas de agregación.

#### 3.3 Conexión a S3
- **Severidad:** **Media**
- **Endpoint Invocado:** `POST /load-from-s3/`
- **Impacto Funcional:** El usuario no puede cargar datos directamente desde buckets de Amazon S3.
- **Recomendación Técnica:** Crear un nuevo módulo `backend/mpa/ingestion_s3/` y un servicio que utilice `boto3` para descargar y procesar archivos desde S3.

#### 3.4 Manejo de Múltiples Hojas de Excel
- **Severidad:** **Baja**
- **Endpoint Invocado:** `POST /upload-data/`
- **Impacto Funcional:** Si un usuario sube un archivo Excel con múltiples hojas, la aplicación no puede manejarlo, limitando la capacidad de análisis de este tipo de archivos.
- **Recomendación Técnica:** Modificar el `IngestionService` para que, si detecta un archivo Excel, devuelva la lista de hojas al frontend. El frontend debería entonces permitir al usuario seleccionar una hoja y reenviar la petición con un parámetro `sheet_name`, que el servicio usaría al leer el archivo con `pandas`.
