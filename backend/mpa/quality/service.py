import pandas as pd
from pydantic import BaseModel
from typing import Dict, Any, List

class QualityReport(BaseModel):
    """Pydantic model for the data quality report."""
    overview: Dict[str, Any]
    column_details: Dict[str, Any]
    health_score: float

class DataQualityService:
    """
    Modular Process Architecture (MPA) service for assessing data quality.
    This service is self-contained and does not depend on legacy code.
    """
    def get_quality_report(self, df: pd.DataFrame) -> QualityReport:
        """
        Generates a comprehensive data quality report from a pandas DataFrame.
        Converts numpy numeric types to native Python types for JSON serialization.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame.")

        # --- Overview ---
        num_rows, num_cols = df.shape
        total_cells = num_rows * num_cols
        missing_cells = df.isnull().sum().sum()
        missing_percentage = (missing_cells / total_cells) * 100 if total_cells > 0 else 0
        duplicate_rows = df.duplicated().sum()

        overview = {
            "num_rows": int(num_rows),
            "num_cols": int(num_cols),
            "total_cells": int(total_cells),
            "missing_cells": int(missing_cells),
            "missing_percentage": float(round(missing_percentage, 2)),
            "duplicate_rows": int(duplicate_rows),
        }

        # --- Column Details ---
        column_details = {}
        for col in df.columns:
            series = df[col]
            dtype = str(series.dtype)
            missing = series.isnull().sum()
            missing_pct = (missing / num_rows) * 100 if num_rows > 0 else 0
            unique_values = series.nunique()

            stats = {
                "dtype": dtype,
                "missing_values": int(missing),
                "missing_percentage": float(round(missing_pct, 2)),
                "unique_values": int(unique_values),
            }

            if pd.api.types.is_numeric_dtype(series):
                stats["mean"] = float(series.mean())
                stats["std_dev"] = float(series.std())
                stats["min"] = float(series.min())
                stats["max"] = float(series.max())

            column_details[str(col)] = stats

        # --- Health Score Calculation ---
        score = 100.0
        score -= missing_percentage * 1.5
        score -= (duplicate_rows / num_rows) * 100 if num_rows > 0 else 0

        for col_data in column_details.values():
            if col_data["missing_percentage"] > 50:
                score -= 5

        health_score = float(max(0, round(score, 2)))

        return QualityReport(
            overview=overview,
            column_details=column_details,
            health_score=health_score
        )

# --- Dependency Injection ---
data_quality_service = DataQualityService()

def get_data_quality_service() -> DataQualityService:
    return data_quality_service
