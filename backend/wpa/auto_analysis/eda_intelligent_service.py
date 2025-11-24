import pandas as pd
from typing import Dict, Any, List

class EDAIntelligentService:
    """
    Performs automated Exploratory Data Analysis (EDA) on a given dataset.
    It automatically classifies variables and computes relevant summary statistics.
    """

    def __init__(self, dataframe: pd.DataFrame, inferred_types: Dict[str, str]):
        self.df = dataframe
        self.inferred_types = inferred_types
        self.classified_types = self._classify_variables()

    def _classify_variables(self) -> Dict[str, str]:
        """
        Refines the initial type inference into more specific statistical types.
        """
        classified = {}
        for col, base_type in self.inferred_types.items():
            if base_type == 'numeric':
                unique_count = self.df[col].nunique()
                if unique_count == 2:
                    classified[col] = 'binary'
                elif unique_count < 20:  # Arbitrary threshold for discrete
                    classified[col] = 'numeric_discrete'
                else:
                    classified[col] = 'numeric_continuous'
            elif base_type == 'categorical':
                # Simple nominal classification for now. Ordinal would require more context.
                classified[col] = 'categorical_nominal'
            else:
                 classified[col] = base_type # e.g., 'datetime'
        print("Variable classification complete.")
        return classified

    def run_automated_eda(self) -> Dict[str, Any]:
        """
        Generates a comprehensive EDA report for the dataset.
        """
        eda_results = {
            "variable_classification": self.classified_types,
            "summary_statistics": self._get_summary_stats(),
            "missing_values_report": self._get_missing_report(),
            "outlier_report": self._detect_outliers()
            # Correlation matrix and normality tests will be in stats_engine.py
        }
        print("Automated EDA run complete.")
        return eda_results

    def _get_summary_stats(self) -> Dict[str, Dict[str, Any]]:
        """

        Calculates descriptive statistics for all columns, tailored to their type.
        """
        stats = {}
        for col, var_type in self.classified_types.items():
            if var_type.startswith('numeric'):
                stats[col] = {
                    'mean': self.df[col].mean(),
                    'median': self.df[col].median(),
                    'std_dev': self.df[col].std(),
                    'skewness': self.df[col].skew(),
                    'kurtosis': self.df[col].kurt(),
                    'min': self.df[col].min(),
                    'max': self.df[col].max(),
                }
            elif var_type.startswith('categorical'):
                stats[col] = {
                    'mode': self.df[col].mode().iloc[0] if not self.df[col].mode().empty else 'N/A',
                    'value_counts': self.df[col].value_counts().to_dict()
                }
        return stats

    def _get_missing_report(self) -> Dict[str, Any]:
        """
        Generates a report on missing values.
        """
        missing_count = self.df.isnull().sum()
        missing_percent = (missing_count / len(self.df)) * 100
        report = {
            "total_missing_count": int(missing_count.sum()),
            "columns": {
                col: {"count": int(missing_count[col]), "percentage": missing_percent[col]}
                for col in self.df.columns
            }
        }
        return report

    def _detect_outliers(self, iqr_multiplier: float = 1.5) -> Dict[str, List[Any]]:
        """
        Detects outliers in numeric columns using the IQR method.
        """
        outliers = {}
        for col, var_type in self.classified_types.items():
            if var_type.startswith('numeric'):
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - iqr_multiplier * IQR
                upper_bound = Q3 + iqr_multiplier * IQR

                col_outliers = self.df[
                    (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
                ][col].tolist()

                if col_outliers:
                    outliers[col] = col_outliers
        return outliers

def run_eda(df: pd.DataFrame, inferred_types: Dict[str, str]) -> Dict[str, Any]:
    """
    Entrypoint function to run the full automated EDA process.
    """
    service = EDAIntelligentService(df, inferred_types)
    eda_report = service.run_automated_eda()

    # In a real scenario, this would be saved to a file.
    # For example:
    # with open(f"/data/processed/{job_id}/eda/eda_report.json", "w") as f:
    #     json.dump(eda_report, f, indent=4)

    return eda_report
