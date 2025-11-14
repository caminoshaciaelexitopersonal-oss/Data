# backend/app/etl_providers/__init__.py

"""
Este paquete contiene todos los cargadores de datos modulares para el sistema ETL.

Cada módulo se especializa en un tipo de fuente de datos (e.g., CSV, SQL, API).
Las funciones aquí expuestas están diseñadas para ser llamadas por el servicio de orquestación ETL.
"""

from .csv_loader import load_csv
from .excel_loader import load_excel
from .json_loader import load_json
from .parquet_loader import load_parquet
from .api_ingestor import ingest_from_api
from .sql_ingestor import ingest_from_sql
from .tsv_loader import load_tsv
from .jsonl_loader import load_jsonl
from .yaml_loader import load_yaml

__all__ = [
    'load_csv',
    'load_excel',
    'load_json',
    'load_parquet',
    'ingest_from_api',
    'ingest_from_sql',
    'load_tsv',
    'load_jsonl',
    'load_yaml'
]
