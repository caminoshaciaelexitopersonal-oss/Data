from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from typing import List, Optional
import pandas as pd
import os

from backend.wpa.intelligent_merge.service import IntelligentMergeService, intelligent_merge_service, LOG_FILE_PATH
from backend.wpa.intelligent_merge.schemas import IntelligentMergeResponse
from backend.mpa.ingestion.service import IngestionService, ingestion_service as mpa_ingestion_service

# API Router for the Intelligent Merge WPA
router = APIRouter(prefix="/wpa/intelligent-merge", tags=["WPA - Intelligent Merge"])

# Dependency injection for the services
def get_intelligent_merge_service() -> IntelligentMergeService:
    return intelligent_merge_service

def get_ingestion_service() -> IngestionService:
    return mpa_ingestion_service

@router.post("/upload-and-merge", response_model=IntelligentMergeResponse)
async def upload_and_merge_files(
    files: List[UploadFile] = File(..., description="Multiple files to be intelligently merged."),
    required_columns: Optional[List[str]] = Query(None, description="A list of column names that must be present and non-null."),
    merge_service: IntelligentMergeService = Depends(get_intelligent_merge_service),
    ingestion_service: IngestionService = Depends(get_ingestion_service)
):
    """
    Orchestrates the entire intelligent merge workflow from file uploads.
    Allows specifying required columns for data validation.
    """
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Please upload at least two files to merge.")

    dataframes = []
    filenames = []

    # Use the existing Ingestion MPA to process uploaded files
    for file in files:
        try:
            # We need to read the file content into memory to pass it to the service
            # This is because UploadFile is an async iterator
            df = await ingestion_service.process_file(file)
            dataframes.append(df)
            filenames.append(file.filename)
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing file {file.filename}: {e}")

    try:
        # Run the main pipeline, passing the required columns
        merged_df, report_path = merge_service.run_merge_pipeline(
            dataframes, filenames, required_columns=required_columns
        )

        # Export to all formats
        csv_path = merge_service.export_to_csv(merged_df, filename="merged_output.csv")
        parquet_path = merge_service.export_to_parquet(merged_df, filename="merged_output.parquet")
        sql_path = merge_service.export_to_sql(merged_df, filename="merged_output.sqlite")

        return IntelligentMergeResponse(
            message="Intelligent merge process completed successfully.",
            quality_report_path=report_path,
            exported_files={
                "csv": csv_path,
                "parquet": parquet_path,
                "sqlite": sql_path,
            },
            log_file_path=LOG_FILE_PATH
        )
    except Exception as e:
        # Catch errors from the merge pipeline itself
        raise HTTPException(status_code=500, detail=f"An error occurred during the merge pipeline: {e}")
