import pandas as pd
import mlflow
from typing import Dict, Any, List
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, mean_squared_error

from backend.wpa.modeling.schemas import ModelTrainRequest
from backend.wpa.session_manager import SessionManager

class ModelingService:
    """
    Service for the "Modeling" Workflow (WPA).
    Orchestrates model training and prediction.
    """
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager

    def _get_model(self, model_type: str):
        if model_type == "random_forest":
            return RandomForestClassifier(n_estimators=100)
        elif model_type == "svm":
            return SVC()
        elif model_type == "decision_tree":
            return DecisionTreeClassifier()
        elif model_type == "linear_regression":
            return LinearRegression()
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    def train_model(self, request: ModelTrainRequest) -> Dict[str, Any]:
        """
        Executes the model training workflow.
        """
        # Load the DataFrame from the session manager
        df = self.session_manager.load_dataframe(request.session_id)
        if df is None:
             raise ValueError(f"No data found for session_id: {request.session_id}")

        X = df[request.feature_columns]
        y = df[request.target_column]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

        model = self._get_model(request.model_type)

        mlflow.set_experiment(request.experiment_name)
        with mlflow.start_run() as run:
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)

            if request.model_type in ["linear_regression"]:
                metric = mean_squared_error(y_test, predictions)
                metric_name = "mse"
            else:
                metric = accuracy_score(y_test, predictions)
                metric_name = "accuracy"

            mlflow.log_param("model_type", request.model_type)
            mlflow.log_metric(metric_name, metric)
            mlflow.sklearn.log_model(model, "model")

            return {
                "mlflow_run_id": run.info.run_id,
                "model_accuracy": metric
            }

    def predict(self, run_id: str, data: List[Dict[str, Any]]) -> List[Any]:
        """
        Makes predictions using a logged MLflow model.
        """
        model = mlflow.sklearn.load_model(f"runs:/{run_id}/model")
        df = pd.DataFrame(data)
        predictions = model.predict(df)
        return predictions.tolist()
