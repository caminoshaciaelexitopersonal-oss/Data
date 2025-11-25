import pandas as pd
from typing import Dict, Any, Optional

class TargetDetector:
    """
    Intelligently detects the most likely target variable in a dataset
    based on a set of heuristics.
    """

    def __init__(self, dataframe: pd.DataFrame, metadata: Dict[str, Any]):
        self.df = dataframe
        self.metadata = metadata
        self.classified_types = metadata.get("inferred_types", {}) # Using inferred for broader compatibility

    def detect_target(self) -> Optional[str]:
        """
        Runs a scoring algorithm to find the best candidate for the target variable.

        Heuristics:
        1.  **Name-based:** Columns with names like 'target', 'label', 'class', 'output', 'prediction' get a high score.
        2.  **Low Cardinality (for Classification):** Categorical columns with low cardinality (2-20 unique values) are good candidates.
        3.  **High Correlation (for Regression):** Numeric columns that have a high average correlation with other numeric columns.
        4.  **Low Nulls:** Columns with a low percentage of missing values are preferred.
        5.  **Not an ID:** Columns identified as potential IDs (unique for every row) are penalized.
        """
        scores: Dict[str, float] = {col: 0.0 for col in self.df.columns}

        # 1. Name-based scoring
        target_keywords = ['target', 'label', 'class', 'output', 'prediction', 'objetivo', 'respuesta']
        for col in self.df.columns:
            if any(keyword in col.lower() for keyword in target_keywords):
                scores[col] += 50

        # 2. Cardinality scoring
        for col, card in self.metadata.get("cardinality", {}).items():
            if self.classified_types.get(col) == 'categorical':
                if 2 <= card <= 20:
                    scores[col] += 30  # Good for classification
                elif card > 20:
                    scores[col] -= 20 # Too many classes, less likely to be a simple target

        # 3. Correlation scoring
        corr_matrix = self.df[self.metadata.get("column_names", [])].select_dtypes(include='number').corr().abs()
        if not corr_matrix.empty:
            avg_corr = corr_matrix.mean()
            for col in avg_corr.index:
                scores[col] += avg_corr[col] * 20 # Weighted score

        # 4. Low nulls scoring
        for col, null_pct in self.metadata.get("null_percentages", {}).items():
            scores[col] -= null_pct # Penalize for missing values

        # 5. Penalize IDs
        potential_risks = self.metadata.get("potential_risks", [])
        for risk in potential_risks:
            if "high-cardinality identifier" in risk:
                col_name = risk.split("'")[1]
                if col_name in scores:
                    scores[col_name] -= 100 # Heavy penalty

        # Find the best candidate
        if not scores:
            return None

        best_target = max(scores, key=scores.get)
        print(f"Target detection complete. Best candidate: '{best_target}' with score {scores[best_target]:.2f}")

        return best_target

def detect_target_variable(df: pd.DataFrame, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entrypoint function to run the target detection process.
    """
    detector = TargetDetector(df, metadata)
    target = detector.detect_target()

    result = {"detected_target": target}

    # In a real scenario, this would be saved to a file.
    # For example:
    # with open(f"/data/processed/{job_id}/target.json", "w") as f:
    #     json.dump(result, f, indent=4)

    return result
