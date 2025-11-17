from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal
from uuid import UUID

from backend.mcp.schemas import TraceableRequest

class ModelTrainRequest(TraceableRequest):
    """
    Request model to train a new model.
    """
    model_type: Literal["random_forest", "svm", "decision_tree", "linear_regression"]
    target_column: str
    feature_columns: List[str]
    experiment_name: str = "WPA Model Training"
    session_id: str # To retrieve the correct dataset

class ModelTrainResponse(BaseModel):
    """
    Response model after training a model.
    """
    job_id: UUID
    message: str
    mlflow_run_id: str
    model_accuracy: float

class ModelPredictRequest(TraceableRequest):
    """
    Request model to make predictions using a trained model.
    """
    mlflow_run_id: str
    prediction_data: List[Dict[str, Any]]

class ModelPredictResponse(BaseModel):
    """
    Response model containing the predictions.
    """
    job_id: UUID
    message: str
    predictions: List[Any]
