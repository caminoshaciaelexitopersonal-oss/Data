from fastapi import UploadFile, HTTPException
import pandas as pd
import io
from sqlalchemy import create_engine, text
from backend.schemas import DbConnectionRequest

class IngestionService:
    """
    Modular Process Architecture (MPA) service for data ingestion.
    Handles data loading from files and SQL databases.
    """
    SQL_DENYLIST = ["DROP", "DELETE", "UPDATE", "INSERT", "CREATE", "ALTER", "TRUNCATE"]
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
    ALLOWED_MIMETYPES = [
        "text/csv",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/json",
        "application/parquet",
    ]

    async def process_file(self, file: UploadFile) -> pd.DataFrame:
        """
        Processes an uploaded file and returns a pandas DataFrame.
        """
        if file.size > self.MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File is too large.")
        if file.content_type not in self.ALLOWED_MIMETYPES:
            raise HTTPException(status_code=415, detail="Unsupported or corrupt file type.")

        try:
            contents = await file.read()
            if file.content_type == "text/csv":
                df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
            elif file.content_type in [
                "application/vnd.ms-excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ]:
                df = pd.read_excel(io.BytesIO(contents))
            elif file.content_type == "application/json":
                df = pd.read_json(io.StringIO(contents.decode("utf-8")))
            elif file.content_type == "application/parquet":
                df = pd.read_parquet(io.BytesIO(contents))
            else:
                raise HTTPException(status_code=415, detail="Unsupported file type.")
            return df
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Error processing file: {e}")

    def _validate_sql_query(self, query: str):
        """
        Validates the SQL query against a denylist of dangerous keywords.
        """
        if any(keyword in query.upper() for keyword in self.SQL_DENYLIST):
            raise HTTPException(status_code=403, detail="SQL query contains disallowed commands.")

    def load_from_db(self, conn_request: DbConnectionRequest) -> pd.DataFrame:
        """
        Loads data from a SQL database based on a connection request.
        """
        self._validate_sql_query(conn_request.query)
        try:
            engine = create_engine(conn_request.db_uri)
            with engine.connect() as connection:
                df = pd.read_sql(text(conn_request.query), connection)
            return df
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error connecting to or querying the database: {e}")

# Instantiate the service to be used by the API
ingestion_service = IngestionService()
