# Informe de Auditoría de Importaciones

Este documento detalla todas las importaciones rotas encontradas en el backend y las correcciones necesarias.

---

### 1. `backend/celery_worker.py`

- **Importación Rota:** `from app.services.etl_multisource_service import run_full_etl_process`
- **Ruta Pretendida:** `app/services/etl_multisource_service.py`
- **Ubicación Real:** `backend/app/services/etl_multisource_service.py`
- **Corrección Necesaria:** `from backend.app.services.etl_multisource_service import run_full_etl_process`

---

### 2. `backend/tests/test_audit.py`

- **Importación Rota:** `from ..app.services import audit_service`
- **Ruta Pretendida:** Sube dos niveles desde `tests/` y luego entra a `app/services/`.
- **Ubicación Real:** `backend/app/services/audit_service.py`
- **Corrección Necesaria:** `from backend.app.services import audit_service`

---

### 3. `backend/tests/test_etl.py` (Línea 3)

- **Importación Rota:** `from ..app.services import etl_service`
- **Ruta Pretendida:** Sube dos niveles desde `tests/` y luego entra a `app/services/`.
- **Ubicación Real:** `backend/app/services/etl_service.py`
- **Corrección Necesaria:** `from backend.app.services import etl_service`

---

### 4. `backend/tests/test_etl.py` (Línea 4)

- **Importación Rota:** `from ..app.etl_providers import loader_jsonl, loader_tsv`
- **Ruta Pretendida:** Sube dos niveles desde `tests/` y luego entra a `app/etl_providers/`.
- **Ubicación Real:** `backend/app/etl_providers/`
- **Corrección Necesaria:** `from backend.app.etl_providers import loader_jsonl, loader_tsv`

---
