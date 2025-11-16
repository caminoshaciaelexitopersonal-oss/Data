from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy import create_engine, text
import pandas as pd
import io
from typing import List

from backend.schemas import DbConnectionRequest
from backend.services.ingestion_service import process_file, validate_sql_query

router = APIRouter()

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB
ALLOWED_MIMETYPES = [
    "text/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/json",
    "application/parquet",
]

@router.post("/upload-data/")
async def upload_data(file: UploadFile = File(...)):
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="El archivo es demasiado grande.")
    if file.content_type not in ALLOWED_MIMETYPES:
        raise HTTPException(status_code=415, detail="Tipo de archivo no soportado o corrupto.")

    df = await process_file(file)
    return {
        "filename": file.filename,
        "data": df.head().to_dict(orient="records"),
    }

@router.post("/load-from-db/")
async def load_from_db(conn_request: DbConnectionRequest):
    validate_sql_query(conn_request.query)
    try:
        engine = create_engine(conn_request.db_uri)
        with engine.connect() as connection:
            df = pd.read_sql(text(conn_request.query), connection)
        return {"data": df.head().to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar o ejecutar la consulta: {e}")
