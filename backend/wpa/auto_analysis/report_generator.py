from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any
import os

class ReportGenerator:
    """
    Generates a comprehensive HTML report from the analysis artifacts.
    """

    def __init__(self, job_id: str, analysis_results: Dict[str, Any]):
        self.job_id = job_id
        self.results = analysis_results

        # Setup Jinja2 environment
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        if not os.path.exists(template_dir):
            os.makedirs(template_dir)

        self.env = Environment(loader=FileSystemLoader(template_dir))
        self._create_default_template_if_not_exists(os.path.join(template_dir, 'report_template.html'))

    def _create_default_template_if_not_exists(self, template_path: str):
        """Creates a default Jinja2 template if one doesn't exist."""
        if not os.path.exists(template_path):
            default_template = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Auto-Analysis Report for Job {{ job_id }}</title>
                <style>
                    body { font-family: sans-serif; margin: 2em; }
                    h1, h2 { color: #333; }
                    .section { margin-bottom: 2em; padding: 1em; border: 1px solid #ddd; border-radius: 5px; }
                    pre { background-color: #f4f4f4; padding: 1em; border-radius: 3px; white-space: pre-wrap; }
                    img { max-width: 100%; height: auto; border: 1px solid #ccc; }
                </style>
            </head>
            <body>
                <h1>Automated Data Analysis Report</h1>
                <p><strong>Job ID:</strong> {{ job_id }}</p>

                <div class="section">
                    <h2>1. Dataset Metadata</h2>
                    <pre>{{ results.metadata | tojson(indent=4) }}</pre>
                </div>

                <div class="section">
                    <h2>2. Exploratory Data Analysis (EDA)</h2>
                    <pre>{{ results.eda_report | tojson(indent=4) }}</pre>
                </div>

                <div class="section">
                    <h2>3. Target Variable Detection</h2>
                    <p>Detected Target: <strong>{{ results.target_detection.detected_target }}</strong></p>
                </div>

                <div class="section">
                    <h2>4. Model Training & Evaluation</h2>
                    <p>Problem Type: {{ results.model_results.problem_type }}</p>
                    <h3>Best Model: {{ results.model_results.best_model_name }}</h3>
                    <pre>{{ results.model_results.best_model_metrics | tojson(indent=4) }}</pre>
                    <h3>All Model Evaluations:</h3>
                    <pre>{{ results.model_results.evaluation_results | tojson(indent=4) }}</pre>
                </div>

                <div class="section">
                    <h2>5. Model Explainability</h2>
                    <h3>SHAP Summary Plot</h3>
                    <img src="data:image/png;base64,{{ results.explanations.shap_summary_plot_base64 }}" alt="SHAP Summary Plot">
                    {% if results.explanations.feature_importance %}
                        <h3>Feature Importance</h3>
                        <pre>{{ results.explanations.feature_importance | tojson(indent=4) }}</pre>
                    {% endif %}
                </div>
            </body>
            </html>
            """
            with open(template_path, "w") as f:
                f.write(default_template)

    def generate_html_report(self) -> str:
        """
        Renders the analysis results into an HTML string.
        """
        template = self.env.get_template('report_template.html')
        html_content = template.render(
            job_id=self.job_id,
            results=self.results
        )
        print("HTML report generated successfully.")
        return html_content

def generate_report(job_id: str, results: Dict[str, Any]) -> str:
    """
    Entrypoint to run the report generation process.
    """
    generator = ReportGenerator(job_id, results)
    html_report = generator.generate_html_report()

    # In a real scenario, this would be saved to a file.
    # report_path = f"/data/processed/{job_id}/reports/analysis_report.html"
    # os.makedirs(os.path.dirname(report_path), exist_ok=True)
    # with open(report_path, "w") as f:
    #     f.write(html_report)

    return html_report
