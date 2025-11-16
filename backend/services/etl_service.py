import pandas as pd
from typing import List, Dict, Any

def process_pipeline(df: pd.DataFrame, steps: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Processes a DataFrame through a series of transformation steps.
    """
    for step in steps:
        action = step.get("action")
        if action == "rename":
            df = df.rename(columns=step.get("columns", {}))
        elif action == "drop_nulls":
            df = df.dropna(subset=[step.get("column")])
        # Add other ETL actions here as needed
    return df
