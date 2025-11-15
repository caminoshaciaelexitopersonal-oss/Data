
# Informe de Análisis de Riesgos de SADI

**Fecha:** 2025-11-15
**Autor:** Jules

## 1. Resumen Ejecutivo

Este documento detalla los riesgos técnicos y de mantenibilidad identificados durante la auditoría profunda del sistema SADI. El objetivo es proporcionar una visión clara de los puntos débiles que podrían afectar la estabilidad, seguridad o escalabilidad futura del proyecto.

---

## 2. Riesgos Identificados

### 2.1. Fallo Crítico de Arranque del Servidor (Riesgo Muy Alto)

-   **Descripción:** El backend es actualmente **inoperable**. No puede arrancar debido a un `ImportError` en `backend/main.py` relacionado con la biblioteca `langchain-experimental`. Una actualización en esta dependencia ha roto la compatibilidad del código.
-   **Impacto:**
    -   **Total:** Bloquea toda la funcionalidad de la aplicación, ya que el frontend no tiene un backend al que conectarse.
    -   **Inmediato:** Impide cualquier prueba de extremo a extremo, desarrollo de nuevas funcionalidades o despliegue.
-   **Causa Raíz:** Dependencia de una biblioteca externa sin un versionado estricto (`pinning`) y falta de un pipeline de integración continua (CI) que detecte este tipo de roturas automáticamente.
-   **Recomendación:**
    1.  **Inmediata:** Corregir el `ImportError` en `backend/main.py` para restaurar la funcionalidad del servidor.
    2.  **A Mediano Plazo:** Revisar el archivo `backend/requirements.txt` y fijar las versiones de las dependencias críticas (especialmente las que están en desarrollo activo como `langchain-experimental`) para evitar roturas inesperadas.
    3.  **Estratégico:** Implementar un pipeline de CI con pruebas automatizadas que se ejecuten en cada cambio de código.

### 2.2. Contratos de API Implícitos (Riesgo Medio)

-   **Descripción:** La estructura de los datos JSON que se intercambian entre el frontend y el backend no está validada de forma estricta. Se basa en una convención implícita que ambos lados deben seguir manualmente.
-   **Impacto:** Un cambio en el nombre de un campo en la API del backend puede causar fallos silenciosos en el frontend que son difíciles de depurar. Aumenta la carga cognitiva de los desarrolladores, que deben mantener la sincronización manualmente.
-   **Causa Raíz:** Falta de un esquema de validación de datos compartido.
-   **Recomendación:**
    1.  **Buena Práctica:** Utilizar al máximo las capacidades de Pydantic en FastAPI para definir modelos de respuesta (`response_model`) explícitos para todos los endpoints.
    2.  **Avanzado:** Considerar la generación automática de un cliente de API para TypeScript a partir de la especificación OpenAPI de FastAPI, lo que garantizaría que los contratos de datos estén siempre sincronizados.

### 2.3. Calidad de Código y Tipado Inconsistente (Riesgo Bajo)

-   **Descripción:** El análisis estático con `flake8` y `mypy` reveló numerosas violaciones de estilo y, más importante, una falta generalizada de stubs de tipos para librerías externas.
-   **Impacto:**
    -   El código es más difícil de leer y mantener.
    -   La falta de un tipado estricto reduce la capacidad del sistema para detectar errores en tiempo de desarrollo, lo que puede llevar a errores en tiempo de ejecución.
    -   El autocompletado y la navegación en los IDEs son menos efectivos.
-   **Causa Raíz:** Falta de un estándar de linting y chequeo de tipos aplicado de forma consistente.
-   **Recomendación:**
    1.  **Configuración:** Crear archivos de configuración para `flake8` y `mypy` (`.flake8`, `mypy.ini`) en la raíz del proyecto para definir reglas y excluir los errores de stubs faltantes.
    2.  **Automatización:** Integrar `flake8` y `mypy` en un hook de pre-commit para asegurar que todo el código nuevo cumpla con los estándares de calidad antes de ser incorporado.

### 2.4. Dependencia de Entorno para Verificación (Riesgo Bajo)

-   **Descripción:** La verificación de ciertas funcionalidades (como la integración con MLflow y la lógica de SHAP) es muy difícil de realizar sin un entorno completo y activo que simule la producción (con todos los servicios de Docker Compose corriendo).
-   **Impacto:** Dificulta la creación de pruebas unitarias y de integración verdaderamente aisladas, lo que puede ralentizar el desarrollo y la depuración.
-   **Causa Raíz:** Acoplamiento de la lógica de negocio con servicios externos como MLflow.
-   **Recomendación:**
    -   **Pruebas Unitarias:** Continuar y expandir el uso de `mocks` (simulaciones) para aislar las unidades de código de los servicios externos durante las pruebas.
    -   **Pruebas de Integración:** Crear un entorno de pruebas de integración dedicado (ej. un `docker-compose.test.yml`) que levante los servicios necesarios para ejecutar pruebas más completas en un entorno controlado.
