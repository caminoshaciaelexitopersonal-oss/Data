import pandas as pd
from typing import Dict, Any, List

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
        For now, it checks if the dataframe is not empty.
        """
        if self.df.empty:
            raise ValueError("DataFrame is empty. No data to process.")
        # Future enhancements could validate against a predefined schema.
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
        This is a simplified inference logic.
        """
        inferred_types = {}
        for col in self.df.columns:
            # Attempt to convert to numeric, ignoring errors
            numeric_col = pd.to_numeric(self.df[col], errors='coerce')

            if self.df[col].dtype in ['int64', 'float64'] or not numeric_col.isnull().all():
                if numeric_col.isnull().any():
                     # Mixed type, but predominantly numeric
                    inferred_types[col] = 'numeric'
                else:
                    # Purely numeric
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
        # Check for duplicate rows
        if self.df.duplicated().any():
            risks.append("Duplicate rows detected.")

        # Check for columns that might be identifiers
        for col in self.df.columns:
            if self.df[col].nunique() == len(self.df):
                risks.append(f"Column '{col}' is a potential high-cardinality identifier.")

        # Simple check for potential PII (Personally Identifiable Information)
        pii_keywords = ['email', 'phone', 'ssn', 'address', 'nombre', 'id']
        for col in self.df.columns:
            if any(keyword in col.lower() for keyword in pii_keywords):
                risks.append(f"Column '{col}' may contain Personally Identifiable Information (PII).")

        print(f"Risk identification complete. Found {len(risks)} potential risks.")
        return risks

def strengthen_ingestion(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Entrypoint function to run the full ingestion strengthening process.
    """
    adapter = IngestionAdapter(df)
    adapter.schema_validator()
    metadata = adapter.metadata_extractor()

    # The metadata dictionary serves as the documented output.
    # In a real scenario, this would be saved to a file.
    # For example:
    # with open(f"/data/processed/{job_id}/ingestion/metadata.json", "w") as f:
    #     json.dump(metadata, f, indent=4)

    return metadata
