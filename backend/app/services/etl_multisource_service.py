import pandas as pd
import os
from typing import Dict, Any, List, Union

from backend.app.etl_providers import (
    load_csv, load_excel, load_json, load_parquet,
    load_tsv, load_jsonl, load_yaml
)
from backend.app.services.normalization_pipeline import run_normalization_pipeline
from backend.app.services.data_exporter import unify_dataframes, export_data
from backend.app.services.compression_handler import decompress_files
from backend.app.etl_audit import log_etl_event

# --- Mapeo de Extensiones a Funciones de Carga ---
DATA_LOADERS = {
    'csv': load_csv,
    'xlsx': load_excel,
    'xls': load_excel,
    'json': load_json,
    'parquet': load_parquet,
    'tsv': load_tsv,
    'jsonl': load_jsonl,
    'yaml': load_yaml,
    'yml': load_yaml,
}

# --- Lógica del Servicio de Orquestación Actualizada ---

def _process_dataframe(df: pd.DataFrame, source_name: str) -> Union[pd.DataFrame, None]:
    """
    Función auxiliar para normalizar, auditar y exportar un único DataFrame.
    """
    try:
        # --- Auditoría Pre-Procesamiento ---
        initial_row_count = len(df)
        initial_columns = list(df.columns)
        log_etl_event(f"Iniciando procesamiento para '{source_name}'.", extra_data={
            "source": source_name,
            "initial_rows": initial_row_count,
            "initial_columns": initial_columns
        })

        # --- Normalización ---
        # Añadir pasos obligatorios al pipeline
        normalization_config = [
            {'step': 'to_snake_case'},
            {'step': 'remove_duplicates'}
        ]
        processed_df = run_normalization_pipeline(df, normalization_config)

        # --- Auditoría Post-Procesamiento ---
        final_row_count = len(processed_df)
        final_columns = list(processed_df.columns)
        column_mapping = {
            initial: final for initial, final in zip(initial_columns, final_columns)
            if initial != final
        }

        log_etl_event(f"Finalizado el procesamiento para '{source_name}'.", extra_data={
            "source": source_name,
            "rows_before": initial_row_count,
            "rows_after": final_row_count,
            "rows_removed": initial_row_count - final_row_count,
            "column_mapping": column_mapping,
            "final_columns": final_columns
        })

        # --- Exportación Individual ---
        # Sanitizar el nombre de la fuente para evitar problemas con subdirectorios
        sanitized_source_name = os.path.basename(source_name)
        individual_output_path = f"data/output/processed_{os.path.splitext(sanitized_source_name)[0]}"
        export_data(processed_df, individual_output_path, 'parquet')
        log_etl_event(f"'{source_name}' exportado individualmente a '{individual_output_path}.parquet'.")

        return processed_df
    except Exception as e:
        error_msg = f"Error procesando la fuente de datos '{source_name}': {e}"
        log_etl_event(error_msg, level='error', extra_data={"source": source_name})
        return None

def run_full_etl_process(file_contents: Dict[str, bytes]) -> Dict[str, Any]:
    """
    Orquesta el pipeline ETL para múltiples archivos, manejando Excel con múltiples hojas.
    """
    os.makedirs("data/output", exist_ok=True)
    processed_dfs = []
    individual_results = {}

    log_etl_event("Inicio del proceso ETL multi-archivo.", extra_data={"file_count": len(file_contents)})

    files_to_process = list(file_contents.items())

    i = 0
    while i < len(files_to_process):
        filename, content = files_to_process[i]
        i += 1

        try:
            log_etl_event(f"Procesando: {filename}")

            if filename.lower().endswith(('.zip', '.tar.gz', '.tgz')):
                log_etl_event(f"Detectado archivo comprimido: {filename}. Descomprimiendo...")
                try:
                    extracted_files = decompress_files(filename, content)
                    files_to_process.extend(extracted_files.items())
                    log_etl_event(f"{len(extracted_files)} archivos extraídos de {filename}.")
                    continue
                except Exception as e:
                    log_etl_event(f"Error al descomprimir '{filename}': {e}", level='error')
                    continue

            extension = filename.split('.')[-1].lower()

            if extension not in DATA_LOADERS:
                log_etl_event(f"Archivo '{filename}' omitido: tipo de archivo no soportado.", level='warning')
                continue

            loader_func = DATA_LOADERS[extension]
            loaded_data = loader_func(content)

            data_sources: Dict[str, pd.DataFrame] = {}
            if isinstance(loaded_data, pd.DataFrame):
                data_sources[filename] = loaded_data
            elif isinstance(loaded_data, dict):
                for sheet_name, df in loaded_data.items():
                    source_name = f"{os.path.splitext(filename)[0]}_{sheet_name}"
                    data_sources[source_name] = df

            for source_name, df in data_sources.items():
                processed_df = _process_dataframe(df, source_name)
                if processed_df is not None:
                    processed_dfs.append(processed_df)
                    individual_results[source_name] = f"data/output/processed_{os.path.splitext(source_name)[0]}.parquet"
                else:
                    individual_results[source_name] = {"error": f"Fallo el procesamiento para {source_name}"}

        except Exception as e:
            error_msg = f"Error crítico procesando el archivo '{filename}': {e}"
            log_etl_event(error_msg, level='error')
            individual_results[filename] = {"error": error_msg}

    if not processed_dfs:
        log_etl_event("No se procesaron datos, no se realizará la unificación.", level='warning')
        master_file_path = None
    else:
        log_etl_event("Iniciando unificación de todos los DataFrames procesados.")
        unified_df = unify_dataframes(processed_dfs)
        master_file_path = "data/output/master_dataset"
        export_data(unified_df, master_file_path, 'parquet')
        log_etl_event(f"DataFrame unificado exportado a {master_file_path}.parquet.", extra_data={"total_rows": len(unified_df)})
        master_file_path += ".parquet"

    log_etl_event("Proceso ETL multi-archivo completado.")

    return {
        "individual_files": individual_results,
        "master_dataset": master_file_path
    }
