import pandas as pd
from sklearn.model_selection import cross_validate, train_test_split
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, mean_absolute_error, mean_squared_error, r2_score
from typing import Dict, Any, Tuple

from backend.wpa.auto_analysis.pipeline_builder import get_classification_pipelines, get_regression_pipelines

class ModelTrainer:
    """
    Trains, evaluates, and selects the best machine learning pipeline
    for a given dataset and target.
    """
    def __init__(self, df: pd.DataFrame, target_variable: str, classified_types: Dict[str, str]):
        self.df = df
        self.target = target_variable
        self.classified_types = classified_types
        self.problem_type = self._determine_problem_type()

        self.features = [col for col in df.columns if col != target_variable]
        self.numeric_features = [col for col in self.features if self.classified_types.get(col, '').startswith('numeric')]
        self.categorical_features = [col for col in self.features if self.classified_types.get(col, '').startswith('categorical')]

    def _determine_problem_type(self) -> str:
        """Determines if the problem is classification or regression."""
        target_type = self.classified_types.get(self.target)
        if target_type in ['binary', 'categorical_nominal']:
            return 'classification'
        elif target_type.startswith('numeric'):
            return 'regression'
        else:
            raise ValueError(f"Unsupported target variable type: {target_type}")

    def run_training_and_evaluation(self) -> Dict[str, Any]:
        """
        Orchestrates the model training, evaluation, and selection process.
        """
        X = self.df.drop(columns=[self.target])
        y = self.df[self.target]

        if self.problem_type == 'classification':
            pipelines = get_classification_pipelines(self.numeric_features, self.categorical_features)
            scoring_metrics = ['accuracy', 'f1_weighted', 'roc_auc_ovr']
        else: # regression
            pipelines = get_regression_pipelines(self.numeric_features, self.categorical_features)
            scoring_metrics = ['r2', 'neg_mean_absolute_error', 'neg_mean_squared_error']

        evaluation_results = {}
        for name, pipeline in pipelines.items():
            print(f"Evaluating model: {name}...")
            cv_results = cross_validate(pipeline, X, y, cv=5, scoring=scoring_metrics, return_train_score=False)
            evaluation_results[name] = {
                metric: cv_results[f'test_{metric}'].mean() for metric in scoring_metrics
            }

        best_model_name, best_model_results = self._select_best_model(evaluation_results)

        # Train the best model on the full dataset
        print(f"Training best model '{best_model_name}' on full dataset...")
        best_pipeline = pipelines[best_model_name]
        best_pipeline.fit(X, y)

        return {
            "problem_type": self.problem_type,
            "evaluation_results": evaluation_results,
            "best_model_name": best_model_name,
            "best_model_metrics": best_model_results,
            "trained_pipeline": best_pipeline,
        }

    def _select_best_model(self, results: Dict[str, Dict[str, float]]) -> Tuple[str, Dict[str, float]]:
        """Selects the best model based on a primary metric."""
        if self.problem_type == 'classification':
            primary_metric = 'f1_weighted'
        else: # regression
            primary_metric = 'r2'

        best_model = None
        best_score = -float('inf')

        for name, metrics in results.items():
            score = metrics.get(primary_metric)
            if score is not None and score > best_score:
                best_score = score
                best_model = name

        if best_model is None:
            raise RuntimeError("Could not select a best model from evaluation results.")

        print(f"Best model selected: {best_model} with {primary_metric} of {best_score:.4f}")
        return best_model, results[best_model]

def train_and_select_model(df: pd.DataFrame, target: str, classified_types: Dict[str, str]) -> Dict[str, Any]:
    """
    Entrypoint to run the full model training and selection process.
    """
    trainer = ModelTrainer(df, target, classified_types)
    results = trainer.run_training_and_evaluation()

    # In a real scenario, the trained pipeline would be serialized and saved.
    # import joblib
    # joblib.dump(results['trained_pipeline'], f"/data/processed/{job_id}/models/best_model.pkl")

    return results
