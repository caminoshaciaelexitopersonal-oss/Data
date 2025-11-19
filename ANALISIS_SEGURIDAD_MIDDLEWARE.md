# Análisis de Seguridad del Middleware de Ingestión

## Objetivo
Este informe evalúa las medidas de seguridad implementadas en el `HardeningMiddleware` y el `IngestionService` en relación con la carga de archivos.

## 1. Validación de Tamaño Máximo de Archivo
- **Estado:** ✅ **Implementado**
- **Detalles:** Tanto el `HardeningMiddleware` como el `IngestionService` implementan una verificación de tamaño máximo. El límite está configurado en **100 MB** (`MAX_FILE_SIZE = 100 * 1024 * 1024`).
  - El middleware verifica el `content-length` del encabezado HTTP.
  - El servicio verifica el atributo `file.size` del objeto `UploadFile` de FastAPI.
- **Evaluación:** La medida es correcta y redundante, lo cual es una buena práctica.

## 2. Sanitización de Contenido
- **Estado:** ❌ **Ausente**
- **Detalles:** No se realiza ninguna sanitización del contenido de los archivos. Los archivos se leen directamente en memoria y se procesan con librerías como `pandas`.
- **Riesgo:** Un archivo malformado o malicioso (e.g., un CSV con scripts incrustados, aunque el riesgo es bajo en el contexto de `pandas`) podría potencialmente causar un comportamiento inesperado o DoS en el parser. No hay un riesgo directo de ejecución de código, pero sí de consumo de recursos.
- **Recomendación:** Considerar el uso de librerías que validen la estructura de los archivos antes de intentar el parseo completo.

## 3. Verificación de MIME Real vs. Declarado
- **Estado:** ❌ **Ausente**
- **Detalles:** La validación se basa únicamente en el `content-type` declarado en la cabecera HTTP (en el middleware) o en el atributo `file.content_type` (en el servicio). No se inspecciona el contenido del archivo (e.g., "magic bytes") para verificar si su tipo real coincide con el declarado.
- **Riesgo:** Un atacante podría subir un archivo con un tipo de contenido malicioso (e.g., un ejecutable) pero declararlo como `text/csv`. Si en el futuro se añade lógica para, por ejemplo, almacenar y servir estos archivos, esto podría llevar a que se sirvan archivos peligrosos. Para el parseo actual con `pandas`, el riesgo principal es un `Unprocessable Entity Error`, que es manejado.
- **Recomendación:** Implementar una verificación de "magic bytes" para confirmar el tipo de archivo real.

## 4. Control de "Zip Bombs"
- **Estado:** ❌ **Ausente**
- **Detalles:** El middleware permite la subida de archivos comprimidos (`.zip`, `.gz`, `.tar`), pero no hay ninguna lógica para protegerse contra "zip bombs" (archivos pequeños que se descomprimen en archivos de tamaño gigantesco, agotando la memoria o el disco).
- **Riesgo:** **Alto**. Un atacante podría subir un archivo `zip` de pocos KB que, al ser procesado en memoria, podría agotar los recursos del servidor y causar una denegación de servicio (DoS).
- **Recomendación:** **Crítico**. Implementar una descompresión segura que verifique el tamaño de los datos descomprimidos antes de cargarlos completamente en memoria.

## 5. Límites de Rate Limiting
- **Estado:** ❌ **Ausente**
- **Detalles:** No existe ningún mecanismo de `rate limiting` en el endpoint de carga de archivos.
- **Riesgo:** Un atacante podría realizar un gran número de peticiones de carga de archivos en un corto período de tiempo, sobrecargando el servidor y causando una denegación de servicio (DoS) por agotamiento de recursos de CPU y red.
- **Recomendación:** Implementar un `rate limiter` (e.g., basado en IP) para el endpoint de subida de archivos, utilizando una dependencia como `slowapi`.
