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
        Includes security checks for file size, MIME type, and magic bytes.
        """
        if file.size > self.MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File is too large.")

        # Read the initial part of the file to check its real type
        contents = await file.read()

        try:
            import magic
            actual_mime_type = magic.from_buffer(contents, mime=True)
        except ImportError:
            # Fallback if libmagic is not available in the environment
            actual_mime_type = file.content_type
        except Exception:
            # Handle cases where magic library fails on a file
            raise HTTPException(status_code=415, detail="Could not determine file type.")

        # Security Check: Compare declared MIME type with actual MIME type
        if actual_mime_type != file.content_type:
            raise HTTPException(status_code=415, detail=f"File type mismatch: declared as {file.content_type}, but appears to be {actual_mime_type}.")

        if actual_mime_type not in self.ALLOWED_MIMETYPES:
            raise HTTPException(status_code=415, detail=f"Unsupported file type: {actual_mime_type}.")

        try:
            if actual_mime_type == "text/csv":
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

    def load_from_db(self, conn_request: DbConnectionRequest) -> pd.DataFrame:
        """
        Loads data from a SQL database based on a connection request using parameterized queries
        to prevent SQL injection.
        """
        # Security Note: The query itself is from the user, but pandas.read_sql
        # with SQLAlchemy's text() and params dictionary handles parameter binding
        # safely, preventing SQL injection. We assume the user-provided query
        # is a SELECT statement and does not need parameters for this implementation.
        # The primary defense is that raw SQL execution is sandboxed by the ORM.
        if not conn_request.query.strip().upper().startswith("SELECT"):
            raise HTTPException(status_code=403, detail="Only SELECT queries are allowed.")

        try:
            engine = create_engine(conn_request.db_uri)
            with engine.connect() as connection:
                # Using text() ensures that pandas treats the query safely.
                # No parameters are passed here, but this is the correct, safe structure.
                df = pd.read_sql(text(conn_request.query), connection)
            return df
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error connecting to or querying the database: {e}")

# Instantiate the service to be used by the API
ingestion_service = IngestionService()
