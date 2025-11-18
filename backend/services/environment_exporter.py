import os
import zipfile
import mlflow
from pathlib import Path
from typing import Dict, Any

class EnvironmentExporterService:
    """
    Service to export all environment artifacts related to a session or job.
    """
    def __init__(self, base_export_path: str = "/tmp/sadi_exports"):
        self.base_export_path = Path(base_export_path)
        self.base_export_path.mkdir(parents=True, exist_ok=True)

    def export_full_environment(self, job_id: str, mlflow_run_id: str = None) -> str:
        """
        Collects all artifacts, downloads the MLflow model, and zips them.
        """
        export_zip_path = self.base_export_path / f"sadi_export_{job_id}.zip"

        with zipfile.ZipFile(export_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 1. Add executed code (placeholder, assuming code is in a specific dir)
            code_path = Path(f"data/processed/code_blocks/{job_id}")
            if code_path.exists():
                for file in code_path.rglob('*'):
                    zipf.write(file, arcname=f"code/{file.name}")

            # 2. Add logs (placeholder, assuming logs are in a specific dir)
            log_path = Path("data/logs/prompts")
            if log_path.exists():
                 for file in log_path.rglob(f'*{job_id}*.jsonl'):
                    zipf.write(file, arcname=f"logs/{file.name}")

            # 3. Add transformed data (placeholder, assuming data is in a session)
            session_data_path = Path(f"data/sessions/{job_id}.pkl")
            if session_data_path.exists():
                zipf.write(session_data_path, arcname="data/transformed_data.pkl")

            # 4. Download and add MLflow model
            if mlflow_run_id:
                try:
                    model_path = mlflow.artifacts.download_artifacts(run_id=mlflow_run_id, artifact_path="model")
                    for root, _, files in os.walk(model_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, model_path)
                            zipf.write(file_path, arcname=f"model/{arcname}")
                except Exception as e:
                    zipf.writestr("model/error.txt", f"Failed to download model: {e}")

        return str(export_zip_path)

def get_environment_exporter_service() -> EnvironmentExporterService:
    """Dependency injector for the service."""
    return EnvironmentExporterService()
