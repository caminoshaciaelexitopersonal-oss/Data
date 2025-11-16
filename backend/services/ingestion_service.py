from fastapi import UploadFile, HTTPException
import pandas as pd
import io

SQL_DENYLIST = ["DROP", "DELETE", "UPDATE", "INSERT", "CREATE", "ALTER", "TRUNCATE"]

async def process_file(file: UploadFile) -> pd.DataFrame:
    """
    Reads an uploaded file and returns a pandas DataFrame.
    """
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
            # This case should be caught by the router's mimetype check
            raise HTTPException(status_code=415, detail="Tipo de archivo no soportado.")
        return df
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Error al procesar el archivo: {e}")

def validate_sql_query(query: str):
    """
    Validates the SQL query against a denylist of dangerous keywords.
    """
    if any(keyword in query.upper() for keyword in SQL_DENYLIST):
        raise HTTPException(status_code=403, detail="La consulta SQL contiene comandos no permitidos.")
