# Documentación de Arquitectura v2

Este documento describe la arquitectura actualizada del sistema SADI, incluyendo la integración de las Fases 4 y 5.

## Diagrama de Flujo

*(Aquí se incrustará un diagrama Mermaid o una imagen del flujo de datos actualizado)*

## Descripción de Componentes

### Módulo de Exportación (`environment_exporter.py`)
- **Propósito:** Empaquetar y exportar todos los artefactos de una sesión de análisis.
- **Endpoint:** `/export/environment`

### Módulo de Validación (`validation_rules.py`)
- **Propósito:** Aplicar reglas de validación dinámicas a los conjuntos de datos.
- **Endpoint:** `/validation/run`

### Middleware de Hardening (`hardening_middleware.py`)
- **Propósito:** Proteger el sistema limitando los tamaños y tipos de archivo en los endpoints de carga.
