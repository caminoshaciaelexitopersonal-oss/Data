import pandas as pd
import shap
from sklearn.pipeline import Pipeline
from typing import Dict, Any, Optional
import matplotlib.pyplot as plt
import base64
import io

class ExplainabilityEngine:
    """
    Generates explainability artifacts (SHAP values, feature importance)
    for a trained machine learning pipeline.
    """
    def __init__(self, pipeline: Pipeline, X_train: pd.DataFrame, y_train: pd.Series):
        self.pipeline = pipeline
        self.X_train = X_train
        self.y_train = y_train
        self.preprocessor = self.pipeline.named_steps['preprocessor']
        self.model = self.pipeline.named_steps.get('classifier') or self.pipeline.named_steps.get('regressor')

        # Transform the training data for SHAP
        self.X_train_transformed = self.preprocessor.fit_transform(self.X_train)

    def generate_explanations(self) -> Dict[str, Any]:
        """
        Generates a dictionary of explainability artifacts, including SHAP plots.
        """
        print("Generating SHAP explanations...")

        # Using KernelExplainer for model-agnostic explanations, though TreeExplainer could be faster for tree models
        explainer = shap.KernelExplainer(self.model.predict, shap.sample(self.X_train_transformed, 50))
        shap_values = explainer.shap_values(shap.sample(self.X_train_transformed, 50))

        # Get feature names after one-hot encoding
        try:
            ohe_feature_names = self.preprocessor.named_transformers_['cat'].named_steps['onehot'].get_feature_names_out()
            numeric_features = self.preprocessor.transformers_[0][2]
            feature_names = list(numeric_features) + list(ohe_feature_names)
        except Exception:
            # Fallback if feature names can't be extracted
            feature_names = [f"feature_{i}" for i in range(self.X_train_transformed.shape[1])]


        summary_plot_b64 = self._create_shap_plot(shap.summary_plot, shap_values, self.X_train_transformed, feature_names, plot_type='dot')

        # Feature importance from tree-based models if available
        feature_importance = None
        if hasattr(self.model, 'feature_importances_'):
            feature_importance = pd.Series(self.model.feature_importances_, index=feature_names).sort_values(ascending=False).to_dict()

        return {
            "shap_summary_plot_base64": summary_plot_b64,
            "feature_importance": feature_importance
        }

    def _create_shap_plot(self, plot_function, *args, **kwargs) -> Optional[str]:
        """
        Generic function to create a SHAP plot and return it as a base64 encoded string.
        """
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            plot_function(*args, **kwargs, show=False)
            plt.tight_layout()

            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            img_b64 = base64.b64encode(buf.read()).decode('utf-8')
            plt.close(fig)
            return img_b64
        except Exception as e:
            print(f"Warning: Could not generate SHAP plot. Error: {e}")
            plt.close('all') # Ensure all figures are closed on error
            return None

def generate_model_explanations(pipeline: Pipeline, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
    """
    Entrypoint to run the full explainability process.
    """
    engine = ExplainabilityEngine(pipeline, X, y)
    explanations = engine.generate_explanations()

    # In a real scenario, this would be saved to a file/database.
    # For example:
    # with open(f"/data/processed/{job_id}/explainability/shap_summary.png", "wb") as f:
    #     f.write(base64.b64decode(explanations["shap_summary_plot_base64"]))

    return explanations
