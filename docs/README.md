# Docs

## 1. Propósito de esta carpeta

Esta carpeta contiene la documentación oficial del proyecto SADI, destinada a desarrolladores, administradores de sistemas y usuarios finales. Su objetivo es proporcionar una referencia centralizada para entender la arquitectura, funcionalidad y operación del sistema.

## 2. Estructura interna

-   `/v2`: Contiene la documentación más reciente, correspondiente a la nueva arquitectura del sistema.
    -   `architecture.md`: Describe en detalle la arquitectura MCP + MPA + WPA, los principios de diseño y el flujo de datos.
    -   `functional_manual.md`: Manual de usuario que describe las funcionalidades de la plataforma desde la perspectiva del usuario final.
    -   `technical_manual.md`: Manual técnico para desarrolladores, con detalles sobre la configuración del entorno, despliegue y APIs.

## 3. Flujos principales

Esta carpeta no participa en flujos de datos de la aplicación en tiempo de ejecución. Su flujo es puramente informativo y de consulta para el equipo de desarrollo y operaciones.

## 4. Reglas y convenciones del módulo

-   Toda la documentación debe mantenerse actualizada con los cambios realizados en el código.
-   Los documentos deben ser claros, concisos y utilizar el formato Markdown.
-   Nuevos documentos o cambios significativos deben ser revisados por el equipo.

## 5. Consideraciones de seguridad

-   La documentación no debe contener secretos, claves de API, contraseñas ni ninguna información de credenciales.
-   Debe evitarse documentar detalles de implementación que puedan facilitar ataques si se hacen públicos (ej. versiones exactas de software con vulnerabilidades conocidas).

## 6. Cambios relevantes

-   **Q4 2025:** Se creó el directorio `v2` para reflejar la documentación de la nueva arquitectura, separándola de la documentación heredada (si la hubiera).
