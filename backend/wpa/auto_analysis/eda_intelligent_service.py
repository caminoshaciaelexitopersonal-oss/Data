import pandas as pd
from typing import Dict, Any, List
import os
import json
import matplotlib.pyplot as plt

class EDAIntelligentService:
    """
    Performs automated Exploratory Data Analysis (EDA) on a given dataset,
    saving reports and visualizations to disk.
    """

    def __init__(self, dataframe: pd.DataFrame, inferred_types: Dict[str, str], job_id: str):
        self.df = dataframe
        self.inferred_types = inferred_types
        self.job_id = job_id
        self.output_dir = f"data/processed/{job_id}/eda/"
        os.makedirs(self.output_dir, exist_ok=True)
        self.classified_types = self._classify_variables()

    def _classify_variables(self) -> Dict[str, str]:
        """Refines the initial type inference into more specific statistical types."""
        classified = {}
        for col, base_type in self.inferred_types.items():
            if base_type == 'numeric':
                unique_count = self.df[col].nunique()
                if unique_count == 2:
                    classified[col] = 'binary'
                elif unique_count < 20:
                    classified[col] = 'numeric_discrete'
                else:
                    classified[col] = 'numeric_continuous'
            else:
                classified[col] = base_type
        print("Variable classification complete.")
        return classified

    def run_automated_eda(self):
        """Generates and saves a comprehensive EDA report."""
        eda_results = {
            "variable_classification": self.classified_types,
            "summary_statistics": self._get_summary_stats(),
            "missing_values_report": self._get_missing_report(),
            "outlier_report": self._detect_outliers()
        }

        # Save JSON report
        report_path = os.path.join(self.output_dir, "eda_report.json")
        with open(report_path, "w") as f:
            json.dump(eda_results, f, indent=4, default=str)
        print(f"EDA report saved to {report_path}")

        # Generate and save visualizations
        self._generate_visualizations()

    def _get_summary_stats(self) -> Dict[str, Dict[str, Any]]:
        """Calculates descriptive statistics for all columns."""
        stats = {}
        for col, var_type in self.classified_types.items():
            if var_type.startswith('numeric'):
                stats[col] = self.df[col].describe().to_dict()
            elif var_type.startswith('categorical'):
                stats[col] = self.df[col].describe().to_dict()
        return stats

    def _get_missing_report(self) -> Dict[str, Any]:
        """Generates a report on missing values."""
        missing_count = self.df.isnull().sum()
        missing_percent = (missing_count / len(self.df)) * 100
        return {col: {"count": int(missing_count[col]), "percentage": missing_percent[col]} for col in self.df.columns}

    def _detect_outliers(self, iqr_multiplier: float = 1.5) -> Dict[str, List[Any]]:
        """Detects outliers in numeric columns using the IQR method."""
        outliers = {}
        for col, var_type in self.classified_types.items():
            if var_type.startswith('numeric'):
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - iqr_multiplier * IQR
                upper_bound = Q3 + iqr_multiplier * IQR
                col_outliers = self.df[(self.df[col] < lower_bound) | (self.df[col] > upper_bound)][col].tolist()
                if col_outliers:
                    outliers[col] = col_outliers
        return outliers

    def _generate_visualizations(self):
        """Generates and saves plots for relevant columns."""
        for col, var_type in self.classified_types.items():
            try:
                plt.figure(figsize=(10, 6))
                if var_type.startswith('numeric'):
                    self.df[col].hist(bins=30)
                    plt.title(f"Histogram of {col}")
                    plt.xlabel(col)
                    plt.ylabel("Frequency")
                elif var_type.startswith('categorical') and self.df[col].nunique() < 50:
                    self.df[col].value_counts().plot(kind='bar')
                    plt.title(f"Bar Chart of {col}")
                    plt.xlabel(col)
                    plt.ylabel("Count")

                plt.tight_layout()
                plot_path = os.path.join(self.output_dir, f"{col}_distribution.png")
                plt.savefig(plot_path)
                plt.close()
                print(f"Saved plot: {plot_path}")
            except Exception as e:
                print(f"Could not generate plot for column '{col}'. Error: {e}")
                plt.close('all')

def run_eda(df: pd.DataFrame, inferred_types: Dict[str, str], job_id: str):
    """
    Entrypoint function to run the full automated EDA process.
    """
    service = EDAIntelligentService(df, inferred_types, job_id)
    service.run_automated_eda()
