import pandas as pd
from typing import List, Dict, Any

class EtlService:
    """
    Modular Process Architecture (MPA) service for ETL (Extract, Transform, Load).
    Applies a series of transformation steps to a DataFrame.
    """
    def process_pipeline(self, df: pd.DataFrame, steps: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Processes a DataFrame through a series of transformation steps.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input 'df' must be a pandas DataFrame.")

        for step in steps:
            action = step.get("action")
            if not action:
                continue

            if action == "rename":
                columns = step.get("columns")
                if isinstance(columns, dict):
                    df = df.rename(columns=columns)

            elif action == "drop_nulls":
                column = step.get("column")
                if isinstance(column, str):
                    df = df.dropna(subset=[column])

            elif action == "fill_nulls":
                column = step.get("column")
                value = step.get("value")
                if isinstance(column, str) and value is not None:
                    df[column] = df[column].fillna(value)

            # Future ETL actions can be added here as new elif blocks.

        return df

# Instantiate the service to be used by the API
etl_service = EtlService()
