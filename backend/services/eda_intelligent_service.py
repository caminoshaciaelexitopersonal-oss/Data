
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any, List
import matplotlib.pyplot as plt
import io
import base64

class EdaIntelligentService:
    """
    A service for providing intelligent Exploratory Data Analysis (EDA).
    This service offers advanced, automated analysis of a DataFrame.
    """

    def auto_detect_distributions(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Automatically detects the distribution of numerical columns using the Shapiro-Wilk test for normality.
        """
        distributions = {}
        for col in df.select_dtypes(include=[np.number]).columns:
            if df[col].nunique() > 1: # Test requires more than one unique value
                stat, p_value = stats.shapiro(df[col].dropna())
                if p_value > 0.05:
                    distributions[col] = "Potentially Normally Distributed"
                else:
                    distributions[col] = "Not Normally Distributed"
            else:
                distributions[col] = "Constant Value"
        return distributions

    def auto_detect_outliers(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """
        Automatically detects outliers in numerical columns using the IQR method.
        Returns the list of outliers and the count.
        """
        outliers_info = {}
        for col in df.select_dtypes(include=[np.number]).columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
            outliers_info[col] = {
                "count": len(outliers),
                "values": outliers.tolist()
            }
        return outliers_info

    def auto_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generates an advanced summary of the DataFrame, ensuring all values are JSON serializable.
        """
        summary = {
            "shape": df.shape,
            "memory_usage": int(df.memory_usage(deep=True).sum()),
            "duplicate_rows": int(df.duplicated().sum()),
            "column_details": {}
        }

        for col in df.columns:
            col_summary = {
                "dtype": str(df[col].dtype),
                "missing_values": int(df[col].isnull().sum()),
                "unique_values": int(df[col].nunique()),
            }
            if pd.api.types.is_numeric_dtype(df[col]):
                # Cast numpy types to standard Python types for JSON serialization
                col_summary.update({
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "std_dev": float(df[col].std()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                })
            else:
                 col_summary.update({
                    "mode": df[col].mode().tolist()
                 })
            summary["column_details"][col] = col_summary
        return summary

    def auto_visualizations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Generates a list of relevant visualizations (as base64 strings) based on data types.
        """
        visualizations = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns

        # Histograms for numeric columns
        for col in numeric_cols:
            plt.figure(figsize=(8, 5))
            df[col].hist()
            plt.title(f'Histogram of {col}')
            plt.xlabel(col)
            plt.ylabel('Frequency')

            visualizations.append(self._fig_to_base64(plt, "histogram", f"Distribution of {col}"))
            plt.close()

        # Bar charts for categorical columns
        for col in categorical_cols:
             if df[col].nunique() < 20: # Only create bar charts for columns with a manageable number of unique values
                plt.figure(figsize=(10, 6))
                df[col].value_counts().plot(kind='bar')
                plt.title(f'Bar Chart of {col}')
                plt.xlabel(col)
                plt.ylabel('Count')
                plt.xticks(rotation=45)

                visualizations.append(self._fig_to_base64(plt, "bar_chart", f"Frequency of {col}"))
                plt.close()

        return visualizations

    def _fig_to_base64(self, plt_instance, chart_type: str, title: str) -> Dict[str, Any]:
        """Converts a matplotlib figure to a base64 encoded string."""
        buf = io.BytesIO()
        plt_instance.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        return {
            "chart_type": chart_type,
            "title": title,
            "image_base64": img_str
        }

def get_eda_intelligent_service() -> EdaIntelligentService:
    """
    Dependency injector for the EdaIntelligentService.
    """
    return EdaIntelligentService()
