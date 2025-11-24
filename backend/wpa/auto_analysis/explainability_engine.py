import pandas as pd
import shap
from sklearn.pipeline import Pipeline
 
import matplotlib.pyplot as plt
import os
import mlflow

class ExplainabilityEngine:
    """
    Generates and saves explainability artifacts (SHAP values, feature importance)
    for a trained machine learning pipeline.
    """
    def __init__(self, pipeline: Pipeline, X_train: pd.DataFrame, job_id: str):
        self.pipeline = pipeline
        self.X_train = X_train
        self.job_id = job_id
        self.output_dir = f"data/processed/{job_id}/explainability/"
        os.makedirs(self.output_dir, exist_ok=True)

        self.preprocessor = self.pipeline.named_steps['preprocessor']
        self.model = self.pipeline.named_steps.get('classifier') or self.pipeline.named_steps.get('regressor')
        self.X_train_transformed = self.preprocessor.fit_transform(self.X_train)

    def generate_and_save_explanations(self):
        """Generates, saves, and logs SHAP and feature importance artifacts."""
        print("Generating SHAP explanations...")
        explainer = shap.KernelExplainer(self.model.predict, shap.sample(self.X_train_transformed, 50))
        shap_values = explainer.shap_values(shap.sample(self.X_train_transformed, 50))

        # --- SHAP Summary Plot ---
        plot_path = os.path.join(self.output_dir, "shap_summary.png")
        plt.figure()
        shap.summary_plot(shap_values, self.X_train_transformed, show=False)
        plt.tight_layout()
        plt.savefig(plot_path)
        plt.close()
        mlflow.log_artifact(plot_path, "explainability")
        print(f"SHAP summary plot saved to {plot_path} and logged to MLflow.")

        # --- Feature Importance ---
        if hasattr(self.model, 'feature_importances_'):
            try:
                ohe_features = self.preprocessor.named_transformers_['cat'].named_steps['onehot'].get_feature_names_out()
                num_features = self.preprocessor.transformers_[0][2]
                feature_names = list(num_features) + list(ohe_features)

                importance_df = pd.DataFrame({'feature': feature_names, 'importance': self.model.feature_importances_})
                importance_df = importance_df.sort_values('importance', ascending=False)

                importance_path = os.path.join(self.output_dir, "feature_importance.csv")
                importance_df.to_csv(importance_path, index=False)
                mlflow.log_artifact(importance_path, "explainability")
                print(f"Feature importance saved to {importance_path} and logged to MLflow.")
            except Exception as e:
                print(f"Could not extract and save feature importance. Error: {e}")

def generate_model_explanations(pipeline: Pipeline, X: pd.DataFrame, job_id: str):
    """Entrypoint to run the full explainability process."""
    engine = ExplainabilityEngine(pipeline, X, job_id)
    engine.generate_and_save_explanations()
 
