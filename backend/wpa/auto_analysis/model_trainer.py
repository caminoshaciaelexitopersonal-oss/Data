import pandas as pd
 
from sklearn.model_selection import cross_validate
from typing import Dict, Any
import mlflow
 

from backend.wpa.auto_analysis.pipeline_builder import get_classification_pipelines, get_regression_pipelines

class ModelTrainer:
 
    # ... (init and _determine_problem_type methods remain the same) ...
 
    def __init__(self, df: pd.DataFrame, target_variable: str, classified_types: Dict[str, str]):
        self.df = df
        self.target = target_variable
        self.classified_types = classified_types
        self.problem_type = self._determine_problem_type()

        self.features = [col for col in df.columns if col != target_variable]
        self.numeric_features = [col for col in self.features if self.classified_types.get(col, '').startswith('numeric')]
        self.categorical_features = [col for col in self.features if self.classified_types.get(col, '').startswith('categorical')]

    def _determine_problem_type(self) -> str:
 
        target_type = self.classified_types.get(self.target)
        if target_type in ['binary', 'categorical_nominal']: return 'classification'
        elif target_type.startswith('numeric'): return 'regression'
        else: raise ValueError(f"Unsupported target variable type: {target_type}")

    def run_training_and_evaluation(self) -> Dict[str, Any]:
        """Orchestrates model training, evaluation, and logging to MLflow."""
 
        X = self.df.drop(columns=[self.target])
        y = self.df[self.target]

        if self.problem_type == 'classification':
            pipelines = get_classification_pipelines(self.numeric_features, self.categorical_features)
            scoring_metrics = ['accuracy', 'f1_weighted', 'roc_auc_ovr']
 
            primary_metric = 'f1_weighted'
        else:
            pipelines = get_regression_pipelines(self.numeric_features, self.categorical_features)
            scoring_metrics = ['r2', 'neg_mean_absolute_error']
            primary_metric = 'r2'

        best_pipeline = None
        best_score = -float('inf')
        best_model_name = ""

        for name, pipeline in pipelines.items():
            with mlflow.start_run(nested=True, run_name=name) as nested_run:
                print(f"Evaluating model: {name}...")
                cv_results = cross_validate(pipeline, X, y, cv=3, scoring=scoring_metrics)

                metrics_to_log = {f"cv_{metric}": cv_results[f'test_{metric}'].mean() for metric in scoring_metrics}
                mlflow.log_metrics(metrics_to_log)

                current_score = metrics_to_log[f"cv_{primary_metric}"]
                if current_score > best_score:
                    best_score = current_score
                    best_model_name = name
                    best_pipeline = pipeline

        if best_pipeline is None:
            raise RuntimeError("Could not select a best model.")

        print(f"Best model selected: {best_model_name} with {primary_metric} of {best_score:.4f}")
        mlflow.set_tag("best_model", best_model_name)

        print(f"Training best model '{best_model_name}' on full dataset...")
        best_pipeline.fit(X, y)

        return {
            "best_model_name": best_model_name,
            "trained_pipeline": best_pipeline,
        }

def train_and_select_model(df: pd.DataFrame, target: str, classified_types: Dict[str, str]) -> Dict[str, Any]:
    trainer = ModelTrainer(df, target, classified_types)
    return trainer.run_training_and_evaluation()
 
