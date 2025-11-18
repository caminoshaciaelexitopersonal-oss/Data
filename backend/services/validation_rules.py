import pandas as pd
from typing import List, Dict, Any

class ValidationService:
    """
    A service to define and execute validation rules on a DataFrame.
    """
    def __init__(self, rules: List[Dict[str, Any]]):
        self.rules = rules
        self.errors = []

    def validate(self, df: pd.DataFrame) -> bool:
        """
        Executes all defined validation rules against the DataFrame.
        """
        self.errors = []
        for rule in self.rules:
            rule_type = rule.get("type")
            if rule_type == "required_columns":
                self._check_required_columns(df, rule.get("columns", []))
            elif rule_type == "column_format":
                self._check_column_format(df, rule.get("column"), rule.get("regex"))
            # More rules can be added here

        return len(self.errors) == 0

    def get_errors(self) -> List[str]:
        """Returns the list of validation errors found."""
        return self.errors

    def _check_required_columns(self, df: pd.DataFrame, required_cols: List[str]):
        """Checks if all required columns are present in the DataFrame."""
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            self.errors.append(f"Missing required columns: {', '.join(missing_cols)}")

    def _check_column_format(self, df: pd.DataFrame, column: str, regex: str):
        """Checks if a column's values match a given regex."""
        if column not in df.columns:
            return # Handled by required_columns check

        mismatched = df[~df[column].astype(str).str.match(regex, na=False)]
        if not mismatched.empty:
            self.errors.append(f"Column '{column}' has format errors. Found {len(mismatched)} mismatched rows.")

def get_validation_service(rules: List[Dict[str, Any]]) -> ValidationService:
    """Dependency injector for the service."""
    return ValidationService(rules)
