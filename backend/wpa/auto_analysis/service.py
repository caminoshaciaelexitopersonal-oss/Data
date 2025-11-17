import pandas as pd
from typing import Dict, Any

from backend.wpa.schemas import WpaAutoAnalysisRequest
from backend.mpa.ingestion.service import IngestionService
from backend.mpa.etl.service import EtlService
from backend.mpa.eda.service import EdaService

class WpaAutoAnalysisService:
    """
    Service for the "Automated Analysis" Workflow (WPA).
    Orchestrates the ingestion -> etl -> eda flow.
    """
    def __init__(
        self,
        ingestion_service: IngestionService,
        etl_service: EtlService,
        eda_service: EdaService,
    ):
        self.ingestion_service = ingestion_service
        self.etl_service = etl_service
        self.eda_service = eda_service

    def execute(self, request: WpaAutoAnalysisRequest) -> Dict[str, Any]:
        """
        Executes the full workflow.
        """
        # 1. Ingestion Step (Simplified for this flow)
        df = pd.DataFrame(request.data)

        # 2. ETL Step
        processed_df = self.etl_service.process_pipeline(df, request.etl_steps)

        # 3. EDA Step
        eda_report = self.eda_service.generate_advanced_eda(processed_df)

        return eda_report
