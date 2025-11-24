import pandas as pd
from typing import Dict, Any, List
import os
import json

class IngestionAdapter:
    """
    Strengthens the existing ingestion pipeline by adding validation,
    metadata extraction, and type inference without modifying the core
    ingestion logic. It operates on the unified CSV produced by the
    current system.
    """

    def __init__(self, dataframe: pd.DataFrame):
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame.")
        self.df = dataframe.copy()

    def schema_validator(self) -> bool:
        """
        Validates the basic structure of the dataframe.
        """
        if self.df.empty:
            raise ValueError("DataFrame is empty. No data to process.")
        print("Schema validation successful: DataFrame is not empty.")
        return True

    def metadata_extractor(self) -> Dict[str, Any]:
        """
        Extracts and documents key metadata from the DataFrame.
        """
        metadata = {
            "num_rows": len(self.df),
            "num_columns": len(self.df.columns),
            "column_names": self.df.columns.tolist(),
            "inferred_types": self.column_type_inference(),
            "null_percentages": {
                col: (self.df[col].isnull().sum() / len(self.df)) * 100
                for col in self.df.columns
            },
            "cardinality": {
                col: self.df[col].nunique() for col in self.df.columns
            },
            "potential_risks": self._identify_risks()
        }
        print("Metadata extraction complete.")
        return metadata

    def column_type_inference(self) -> Dict[str, str]:
        """
        Infers the data type of each column based on its content.
        """
        inferred_types = {}
        for col in self.df.columns:
            numeric_col = pd.to_numeric(self.df[col], errors='coerce')
            if not numeric_col.isnull().all():
                inferred_types[col] = 'numeric'
            elif pd.api.types.is_datetime64_any_dtype(self.df[col]):
                 inferred_types[col] = 'datetime'
            else:
                inferred_types[col] = 'categorical'
        print("Column type inference complete.")
        return inferred_types

    def _identify_risks(self) -> List[str]:
        """
        Identifies potential risks in the dataset.
        """
        risks = []
        if self.df.duplicated().any():
            risks.append("Duplicate rows detected.")
        for col in self.df.columns:
            if self.df[col].nunique() == len(self.df):
                risks.append(f"Column '{col}' is a potential high-cardinality identifier.")
        pii_keywords = ['email', 'phone', 'ssn', 'address', 'nombre', 'id']
        for col in self.df.columns:
            if any(keyword in col.lower() for keyword in pii_keywords):
                risks.append(f"Column '{col}' may contain Personally Identifiable Information (PII).")
        print(f"Risk identification complete. Found {len(risks)} potential risks.")
        return risks

def strengthen_ingestion(df: pd.DataFrame, job_id: str) -> Dict[str, Any]:
    """
    Entrypoint function to run the full ingestion strengthening process and save metadata.
    """
    adapter = IngestionAdapter(df)
    adapter.schema_validator()
    metadata = adapter.metadata_extractor()

    output_dir = f"data/processed/{job_id}/"
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "metadata.json")
    with open(file_path, "w") as f:
        json.dump(metadata, f, indent=4, default=str)

    print(f"Metadata saved to {file_path}")
    return metadata
