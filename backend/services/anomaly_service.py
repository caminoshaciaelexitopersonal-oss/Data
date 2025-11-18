
import pandas as pd
from sklearn.ensemble import IsolationForest
from typing import Dict, Any, List

class AnomalyService:
    """
    Service for detecting anomalies in a dataset using IsolationForest.
    """

    def detect_anomalies(self, df: pd.DataFrame, columns: List[str], contamination: float = 0.1) -> Dict[str, Any]:
        """
        Detects anomalies in the specified columns of a DataFrame.

        Args:
            df (pd.DataFrame): The input DataFrame.
            columns (List[str]): A list of column names to use for anomaly detection.
            contamination (float): The proportion of outliers in the data set.

        Returns:
            Dict[str, Any]: A dictionary containing the indices of the anomalies
                            and the anomaly scores for each data point.
        """
        if not all(col in df.columns for col in columns):
            raise ValueError("One or more specified columns are not in the DataFrame.")

        # Select only the numeric data from the specified columns for the model
        data_for_detection = df[columns].select_dtypes(include=['number'])

        if data_for_detection.empty:
            return {
                "anomalies_indices": [],
                "scores": [],
                "message": "No numeric columns selected for anomaly detection."
            }

        model = IsolationForest(contamination=contamination, random_state=42)
        predictions = model.fit_predict(data_for_detection)

        # Anomalies are marked as -1 by the model
        anomaly_indices = df.index[predictions == -1].tolist()
        scores = model.decision_function(data_for_detection).tolist()

        return {
            "anomalies_indices": anomaly_indices,
            "scores": scores
        }

def get_anomaly_service() -> AnomalyService:
    """Dependency injector for the AnomalyService."""
    return AnomalyService()
