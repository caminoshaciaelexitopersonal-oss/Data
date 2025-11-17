
import pandas as pd
import numpy as np
from typing import Dict, Any, List

class DataQualityService:
    """
    Service to assess the quality of a DataFrame.
    It provides a quality profile, a quality score, and suggestions for improvement.
    """

    def get_quality_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generates a full data quality report for the given DataFrame.
        """
        # 1. Calculate individual quality metrics
        missing_values = self._calculate_missing_values(df)
        duplicate_rows = self._calculate_duplicate_rows(df)
        outlier_report = self._detect_outliers(df)

        # 2. Calculate the overall quality score
        quality_score = self._calculate_quality_score(
            df, missing_values, duplicate_rows, outlier_report
        )

        # 3. Generate suggestions for improvement
        suggestions = self._generate_suggestions(
            missing_values, duplicate_rows, outlier_report
        )

        # 4. Assemble the final report
        report = {
            "quality_score": quality_score,
            "metrics": {
                "missing_values": missing_values,
                "duplicate_rows": duplicate_rows,
                "outliers": outlier_report,
            },
            "suggestions": suggestions,
        }
        return report

    def _calculate_missing_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates missing value statistics."""
        total_missing = int(df.isnull().sum().sum())
        # Cast numpy type to standard Python int for JSON serialization
        total_cells = int(np.prod(df.shape))
        missing_percentage = (total_missing / total_cells) * 100 if total_cells > 0 else 0

        per_column = {col: int(df[col].isnull().sum()) for col in df.columns if df[col].isnull().sum() > 0}

        return {
            "total_missing": total_missing,
            "total_cells": total_cells,
            "missing_percentage": round(missing_percentage, 2),
            "missing_by_column": per_column
        }

    def _calculate_duplicate_rows(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates duplicate row statistics."""
        total_duplicates = int(df.duplicated().sum())
        total_rows = len(df)
        duplicate_percentage = (total_duplicates / total_rows) * 100 if total_rows > 0 else 0

        return {
            "total_duplicates": total_duplicates,
            "total_rows": total_rows,
            "duplicate_percentage": round(duplicate_percentage, 2)
        }

    def _detect_outliers(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detects outliers in numerical columns using the IQR method."""
        outliers_by_column = {}
        total_outliers = 0
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
            if not outliers.empty:
                outliers_by_column[col] = len(outliers)
                total_outliers += len(outliers)

        return {
            "total_outliers": total_outliers,
            "outliers_by_column": outliers_by_column
        }

    def _calculate_quality_score(self, df: pd.DataFrame, missing: Dict, duplicates: Dict, outliers: Dict) -> float:
        """Calculates an overall quality score from 0 to 100."""
        # Weights for each metric
        completeness_weight = 0.4
        uniqueness_weight = 0.3
        validity_weight = 0.3 # Based on outliers for now

        completeness_score = 100 - missing["missing_percentage"]
        uniqueness_score = 100 - duplicates["duplicate_percentage"]

        total_numeric_cells = int(np.prod(df.select_dtypes(include=[np.number]).shape))
        outlier_percentage = (outliers["total_outliers"] / total_numeric_cells) * 100 if total_numeric_cells > 0 else 0
        validity_score = 100 - outlier_percentage

        # Weighted average
        final_score = (
            (completeness_score * completeness_weight) +
            (uniqueness_score * uniqueness_weight) +
            (validity_score * validity_weight)
        )
        return round(final_score, 2)

    def _generate_suggestions(self, missing: Dict, duplicates: Dict, outliers: Dict) -> List[str]:
        """Generates a list of suggestions to improve data quality."""
        suggestions = []
        if missing["total_missing"] > 0:
            suggestions.append(f"Address {missing['total_missing']} missing values. Consider imputation (mean, median, mode) or row removal.")
        if duplicates["total_duplicates"] > 0:
            suggestions.append(f"Remove {duplicates['total_duplicates']} duplicate rows to ensure data uniqueness.")
        if outliers["total_outliers"] > 0:
            suggestions.append(f"Investigate {outliers['total_outliers']} potential outliers. Consider capping, transformation, or removal if they are errors.")

        if not suggestions:
            suggestions.append("Data quality appears to be high. No immediate suggestions.")

        return suggestions

def get_data_quality_service() -> DataQualityService:
    """Dependency injector for the DataQualityService."""
    return DataQualityService()
