# FASE 0 — Reglas de operación (obligatorias para Jules)

Estas reglas ya existen y NO se pueden alterar. Se integran aquí oficialmente para que formen parte del plan rector.

*   NO tocar ingesta existente.
*   NO modificar módulos críticos sin tu autorización explícita.
*   Cada cambio debe seguir el protocolo:
    *   Mostrar archivo
    *   Mostrar modificación propuesta
    *   Preguntar: “¿Autoriza este cambio?”
*   Eliminaciones solo con la frase: `AUTORIZO ELIMINAR [ruta_archivo]`
*   Creación de carpetas solo con: `AUTORIZO CREAR CARPETA [ruta]`
*   Comandos Git/Docker solo con: `AUTORIZO EJECUTAR COMANDO DOCKER:` o `AUTORIZO EJECUTAR COMANDO GIT:`
*   Acciones irreversibles requieren: “Esta acción es irreversible, ¿deseas continuar?”
*   Registro obligatorio por cada acción.

---

# PROTOCOLO OFICIAL PARA MANEJO DE RUTAS (OBLIGATORIO)

Este procedimiento aplica para:
*   `/api/*`
*   `/mpa/*`
*   `/agent/*`
*   Cualquier endpoint FastAPI
*   Cualquier ruta Next.js (pages, app router)
*   Cualquier archivo de router o módulo de negocio

## 1. PROHIBIDO crear una ruta nueva sin autorización

Antes de crear cualquier endpoint o modificar uno existente, debes:

**PASO 1 — Verificar si ya existe**

Debes inspeccionar:
*   `backend/app/api/**/*.py`
*   `backend/app/api/unified_router.py`
*   `backend/app/mpa/**/*.py`
*   `backend/app/agent/**/*.py`

Si la ruta ya existe (aunque esté incompleta o inactiva), debes:
*   No crear una nueva
*   Solicitar permiso para modificar la existente

Formato obligatorio del mensaje:
> Detecté que la ruta X ya existe en Y.
> ¿Autoriza fortalecerla o corregirla sin crear una ruta duplicada?

## 2. Si la ruta NO existe, debes CONFIRMAR con evidencia antes de crearla

Debes enviar un mensaje del siguiente formato:
> Verifiqué en estas ubicaciones:
> - backend/app/api/...
> - unified_router.py
> - módulos MPA
> - módulos Agent
> - módulos ETL/EDA/ML
>
> No existe ninguna ruta que atienda: `/endpoint/propuesto`
>
> ¿Autoriza CREAR la nueva ruta en la ubicación: [ruta_archivo] ?

Solo podrás crearla si recibes explícitamente: `AUTORIZO CREAR ROUTE [ruta]`

## 3. PROHIBIDO modificar o borrar rutas sin permiso

Cualquier cambio debe pedir autorización:
> Propuesta de modificación para la ruta X ubicada en Y:
>
> [mostrar código actual]
> [mostrar modificación propuesta]
>
> ¿Autoriza aplicar este cambio?

Si se desea eliminar un endpoint, el único comando válido es: `AUTORIZO ELIMINAR [ruta_archivo]`

## 4. Duplicación de rutas = FALLO CRÍTICO

Está estrictamente prohibido:
*   Crear rutas paralelas
*   Reescribir rutas existentes bajo otro folder
*   Crear routers paralelos sin autorización
*   Copiar y pegar módulos como alternativa

Cualquier violación debe detener TODO el trabajo y solicitar revisión.

## 5. Todas las rutas deben ser registradas únicamente en unified_router.py

Esta es la fuente oficial de verdad para el backend.

Prohibido:
*   Registrar routers fuera de `unified_router` sin autorización.
*   Crear routers alternos no mencionados en el plan maestro.
*   Crear subrutas sin validación.
