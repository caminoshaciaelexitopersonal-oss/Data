# backend/interoperability/mpa_controller.py

"""
MPA Controller for the Interoperability Layer.

This controller acts as a functional bridge to the various MPA services,
encapsulating the logic to load session data and execute business tasks.
"""
import pandas as pd
from backend.app.services.state_store import StateStore, get_state_store
from backend.services.data_quality_service import DataQualityService, get_data_quality_service
from pathlib import Path

# This path is based on the logic in the legacy IngestionOrchestrator and unified_router.
# A more robust solution would be to get this path from a centralized config.
TEMP_STORAGE_PATH = Path("backend/data/.tmp/ingestion")

class MpaController:
    """
    Orchestrates calls to MPA (Modular Process Architecture) services.
    """
    def __init__(self, session: dict):
        self.session = session
        self.session_id = session['session_id']
        self.state_store: StateStore = get_state_store()
        self.data_quality_service: DataQualityService = get_data_quality_service()

    def _load_session_data(self) -> pd.DataFrame:
        """
        Loads the dataset associated with the current session from the persistent storage.
        """
        # The data is stored by the legacy IngestionOrchestrator in a predictable path.
        file_path = TEMP_STORAGE_PATH / self.session_id / "ingestion_result.csv"
        if not file_path.exists():
            raise FileNotFoundError(f"No data file found for session ID: {self.session_id}")

        return pd.read_csv(file_path)

    def execute_quality_report(self) -> dict:
        """
        Executes the data quality service for the session's data.
        """
        try:
            df = self._load_session_data()
            report = self.data_quality_service.get_quality_report(df)

            # Persist the result to the state store for traceability
            self.state_store.log_step(
                session_id=self.session_id,
                description="Generated Data Quality Report",
                code=f"data_quality_service.get_quality_report(dataframe)"
            )

            return report
        except FileNotFoundError as e:
            return {"error": str(e)}
        except Exception as e:
            # Log the error and return a user-friendly message
            self.state_store.log_step(
                session_id=self.session_id,
                description=f"Failed to generate Data Quality Report: {e}",
                code=""
            )
            return {"error": "An unexpected error occurred while generating the quality report."}
