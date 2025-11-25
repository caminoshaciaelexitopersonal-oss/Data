import pandas as pd
from pathlib import Path
from fastapi import HTTPException

# --- Constants ---
# This path must be consistent with the IngestionOrchestrator from FASE 5
TEMP_STORAGE_PATH = Path("backend/data/.tmp/ingestion")

# --- Unified Analysis Engine Service ---

class UnifiedAnalysisEngine:
    """
    Consolidates EDA, ML, and data quality services into a single, unified pipeline.
    It operates on data persisted by the IngestionOrchestrator, identified by a session_id.
    """
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.df = self._load_data_from_session()

    def _load_data_from_session(self) -> pd.DataFrame:
        """
        Loads the persisted 'ingestion_result.csv' for a given session_id.
        """
        session_path = TEMP_STORAGE_PATH / self.session_id
        data_path = session_path / "ingestion_result.csv"

        if not data_path.exists():
            raise HTTPException(status_code=404, detail=f"No data found for session_id: {self.session_id}")

        try:
            return pd.read_csv(data_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load or parse data for session: {str(e)}")

    def run_data_quality_analysis(self) -> dict:
        """
        Placeholder for the full data quality analysis pipeline.
        In a full implementation, this would reuse logic from data_quality_service.py.
        """
        if self.df is None:
            raise HTTPException(status_code=400, detail="DataFrame not loaded.")

        missing_values = self.df.isnull().sum().to_dict()

        return {
            "status": "success",
            "analysis_type": "Data Quality",
            "results": {
                "missing_values_per_column": {k: int(v) for k, v in missing_values.items()},
                "total_rows": len(self.df)
            }
        }

    def run_exploratory_data_analysis(self) -> dict:
        """
        Placeholder for the full Exploratory Data Analysis (EDA) pipeline.
        In a full implementation, this would reuse logic from eda_intelligent_service.py.
        """
        if self.df is None:
            raise HTTPException(status_code=400, detail="DataFrame not loaded.")

        summary = self.df.describe().to_dict()

        return {
            "status": "success",
            "analysis_type": "EDA",
            "results": {
                "statistical_summary": summary
            }
        }

    def run_ml_modeling(self, model_type: str = "classification") -> dict:
        """
        Placeholder for the full ML modeling pipeline.
        """
        if self.df is None:
            raise HTTPException(status_code=400, detail="DataFrame not loaded.")

        return {
            "status": "success",
            "analysis_type": "ML Modeling",
            "message": f"Placeholder for '{model_type}' model training.",
            "dataset_shape": self.df.shape
        }
