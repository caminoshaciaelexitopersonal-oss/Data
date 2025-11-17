import pandas as pd
from typing import Dict, Any
import uuid

from backend.wpa.db_ingestion.schemas import DbIngestionRequest
from backend.mpa.ingestion.service import IngestionService, ingestion_service
from backend.schemas import DbConnectionRequest

from backend.wpa.session_manager import SessionManager, session_manager

class DbIngestionService:
    """
    Service for the "DB Ingestion" Workflow (WPA).
    Orchestrates loading data from a database and storing it in a session.
    """
    def __init__(self, ingestion_service: IngestionService, session_manager: SessionManager):
        self.ingestion_service = ingestion_service
        self.session_manager = session_manager

    def ingest_from_db(self, request: DbIngestionRequest) -> Dict[str, Any]:
        """
        Executes the DB ingestion workflow.
        """
        db_conn = DbConnectionRequest(db_uri=request.db_uri, query=request.sql_query)
        df = self.ingestion_service.load_from_db(db_conn)

        # Create a new session and save the DataFrame to disk
        session_id = str(uuid.uuid4())
        self.session_manager.save_dataframe(session_id, df)

        return {
            "session_id": session_id,
            "data_preview": df.head().to_dict(orient="records")
        }
