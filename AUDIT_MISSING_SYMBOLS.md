# Auditoría de Símbolos de Importación Faltantes

Este documento detalla los símbolos que se intentan importar desde módulos donde no existen.

---

### Módulo de Origen: `backend/celery_worker.py`

#### 1. Símbolo Faltante: `run_classification_model_task`

- **Archivo que lo Importa:** `backend/tools/main_tools.py`
- **Línea Exacta:** `run_classification_model_task,`
- **Análisis:** No existe una tarea genérica con este nombre.
- **Símbolos Reales Disponibles (Alternativas):**
  - `train_random_forest_classifier_task`
  - `train_svm_classifier_task`
  - `train_decision_tree_classifier_task`
  - `train_mlp_classifier_task`
- **Corrección Sugerida:** La importación debe ser eliminada o reemplazada por una o varias de las tareas específicas. Dado que el objetivo es solo corregir, y no añadir funcionalidad, lo más seguro es eliminar esta línea.

---

#### 2. Símbolo Faltante: `run_pca_task`

- **Archivo que lo Importa:** `backend/tools/main_tools.py`
- **Línea Exacta:** `run_pca_task,`
- **Análisis:** No existe ninguna tarea relacionada con PCA en `celery_worker.py`.
- **Símbolos Reales Disponibles:** N/A.
- **Corrección Sugerida:** Eliminar la importación, ya que la tarea no existe.

---

#### 3. Símbolo Faltante: `generate_data_health_report_task`

- **Archivo que lo Importa:** `backend/tools/main_tools.py`
- **Línea Exacta:** `generate_data_health_report_task,`
- **Análisis:** No existe una tarea Celery para el reporte de salud de datos en `celery_worker.py`.
- **Símbolos Reales Disponibles:** N/A.
- **Corrección Sugerida:** Eliminar la importación.

---

#### 4. Símbolo Faltante: `get_shap_explanation_task`

- **Archivo que lo Importa:** `backend/tools/main_tools.py`
- **Línea Exacta:** `get_shap_explanation_task`
- **Análisis:** El nombre de la tarea es incorrecto.
- **Símbolos Reales Disponibles (Alternativa Clara):**
  - `explain_model_features_task`
- **Corrección Sugerida:** Reemplazar `get_shap_explanation_task` por `explain_model_features_task`.
