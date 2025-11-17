import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from typing import List, Dict, Any

class EdaService:
    """
    Modular Process Architecture (MPA) service for Exploratory Data Analysis (EDA).
    Provides advanced statistics, data health reports, and visualizations.
    """
    def __init__(self):
        # Ensure matplotlib uses a non-interactive backend
        plt.switch_backend('Agg')

    def _calculate_advanced_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        stats = {}
        numerical_cols = df.select_dtypes(include=['number']).columns
        for col in numerical_cols:
            desc = df[col].describe()
            skewness = df[col].skew()
            kurtosis = df[col].kurt()
            iqr = desc['75%'] - desc['25%']
            lower_bound = desc['25%'] - 1.5 * iqr
            upper_bound = desc['75%'] + 1.5 * iqr
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)].shape[0]
            stats[col] = {
                'mean': desc.get('mean'), 'std': desc.get('std'), 'min': desc.get('min'),
                '25%': desc.get('25%'), '50%': desc.get('50%'), '75%': desc.get('75%'),
                'max': desc.get('max'), 'skewness': skewness, 'kurtosis': kurtosis,
                'iqr': iqr, 'outliers_count': outliers
            }
        return stats

    def _generate_plot_base64(self, fig) -> str:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    def _generate_eda_plots(self, df: pd.DataFrame) -> Dict[str, str]:
        plots = {}
        numerical_cols = df.select_dtypes(include=['number']).columns
        for col in numerical_cols:
            fig_hist, ax_hist = plt.subplots(figsize=(8, 5))
            df[col].hist(ax=ax_hist, bins=20, grid=False, color='skyblue')
            ax_hist.set_title(f'Histogram for {col}')
            plots[f'histogram_{col}'] = self._generate_plot_base64(fig_hist)
            fig_box, ax_box = plt.subplots(figsize=(8, 5))
            df.boxplot(column=[col], ax=ax_box, grid=False, patch_artist=True)
            ax_box.set_title(f'Boxplot for {col}')
            plots[f'boxplot_{col}'] = self._generate_plot_base64(fig_box)
        return plots

    def generate_advanced_eda(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return {"error": "No data provided for EDA analysis."}
        try:
            stats = self._calculate_advanced_stats(df)
            plots = self._generate_eda_plots(df)
            return {"status": "success", "advanced_statistics": stats, "plots_base64": plots}
        except Exception as e:
            return {"status": "error", "message": f"An error occurred during EDA generation: {e}"}

    def _calculate_missing_values(self, df: pd.DataFrame) -> Dict[str, Any]:
        missing_percentage = (df.isnull().sum() / len(df)) * 100
        return {"total_percentage": missing_percentage.mean(), "by_column": missing_percentage.to_dict()}

    def _calculate_duplicates(self, df: pd.DataFrame) -> Dict[str, Any]:
        duplicate_count = df.duplicated().sum()
        duplicate_percentage = (duplicate_count / len(df)) * 100 if len(df) > 0 else 0
        return {"count": duplicate_count, "percentage": duplicate_percentage}

    def _summarize_data_types(self, df: pd.DataFrame) -> Dict[str, int]:
        return df.dtypes.astype(str).value_counts().to_dict()

    def _calculate_cardinality(self, df: pd.DataFrame) -> Dict[str, Any]:
        cardinality_report = {}
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            cardinality_report[col] = df[col].nunique()
        return cardinality_report

    def generate_data_health_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return {"error": "DataFrame is empty."}
        try:
            missing = self._calculate_missing_values(df)
            duplicates = self._calculate_duplicates(df)
            data_types = self._summarize_data_types(df)
            cardinality = self._calculate_cardinality(df)
            score = 100 - (missing['total_percentage'] * 1.5) - duplicates['percentage']
            for col, num_unique in cardinality.items():
                if num_unique <= 1 and len(df) > 1:
                    score -= 5
            health_score = max(0, round(score, 2))
            return {
                "status": "success", "health_score": health_score,
                "report": {
                    "missing_values": missing, "duplicates": duplicates,
                    "data_types_summary": data_types, "cardinality_summary": cardinality,
                }
            }
        except Exception as e:
            return {"status": "error", "message": f"An error occurred during health report generation: {e}"}

# Instantiate the service
eda_service = EdaService()
