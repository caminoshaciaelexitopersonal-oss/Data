# Diagramas de Flujos de Trabajo (WPA)

Este documento visualiza los flujos de trabajo automatizados implementados en la arquitectura WPA.

## Flujo 1: Análisis Automático de Salud de Datos

Este flujo recibe una fuente de datos y una serie de pasos de ETL, y devuelve automáticamente un informe de análisis exploratorio de datos (EDA).

```mermaid
graph TD
    A[Frontend: Inicia Flujo] --> B{POST /wpa/auto-analysis};
    B --> C[WPA Service: Inicia Orquestación];
    C --> D[MPA Ingesta: Crea DataFrame];
    D --> E[MPA ETL: Procesa DataFrame];
    E --> F[MPA EDA: Genera Informe];
    F --> G[WPA Service: Compila Respuesta];
    G --> H[Frontend: Recibe Informe EDA];
```

## Flujo 2: Entrenamiento de Modelos

Este flujo recibe una configuración de entrenamiento, entrena un modelo y lo registra en MLflow.

```mermaid
graph TD
    A[Frontend: Inicia Entrenamiento] --> B{POST /wpa/modeling/train};
    B --> C[WPA Service: Inicia Orquestación];
    C --> D[Service: Carga Datos de Sesión];
    D --> E[Service: Entrena Modelo];
    E --> F[MLflow: Registra Experimento y Modelo];
    F --> G[WPA Service: Compila Respuesta];
    G --> H[Frontend: Recibe Run ID y Métrica];
```

## Flujo 3: Generación de Reportes

Este flujo genera un reporte DOCX/PDF basado en los artefactos de una sesión.

```mermaid
graph TD
    A[Frontend: Solicita Reporte] --> B{POST /wpa/reports/generate};
    B --> C[WPA Service: Inicia Orquestación];
    C --> D[Service: Reutiliza Report Generator];
    D --> E[WPA Service: Compila Respuesta con URL];
    E --> F[Frontend: Recibe URL de Descarga];
```

## Flujo 4: Ingesta desde Base de Datos

Este flujo carga datos desde una base de datos y los almacena en una nueva sesión.

```mermaid
graph TD
    A[Frontend: Solicita Carga] --> B{POST /wpa/ingestion/db};
    B --> C[WPA Service: Inicia Orquestación];
    C --> D[MPA Ingesta: Ejecuta Consulta SQL];
    D --> E[WPA Service: Crea Sesión y Almacena Datos];
    E --> F[Frontend: Recibe ID de Sesión y Vista Previa];
```
