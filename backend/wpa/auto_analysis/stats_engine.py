import pandas as pd
from scipy.stats import shapiro, kstest, chi2_contingency, f_oneway, kruskal
from typing import Dict, Any, Tuple, List

class StatsEngine:
    """
    Handles advanced statistical analysis, including normality tests,
    correlation matrices, and automated selection of hypothesis tests.
    """

    def __init__(self, dataframe: pd.DataFrame, classified_types: Dict[str, str]):
        self.df = dataframe
        self.classified_types = classified_types
        self.numeric_cols = [col for col, v_type in classified_types.items() if v_type.startswith('numeric')]

    def run_advanced_stats(self) -> Dict[str, Any]:
        """
        Runs the full suite of advanced statistical analyses.
        """
        stats_report = {
            "normality_tests": self._run_normality_tests(),
            "correlation_matrix": self._calculate_correlation_matrix(),
        }
        print("Advanced statistical analysis complete.")
        return stats_report

    def _run_normality_tests(self, alpha: float = 0.05) -> Dict[str, Dict[str, Any]]:
        """
        Performs Shapiro-Wilk and Kolmogorov-Smirnov tests for normality on numeric columns.
        """
        normality_results = {}
        for col in self.numeric_cols:
            # Drop NA for testing
            data = self.df[col].dropna()

            # Shapiro-Wilk is good for n < 5000
            if len(data) > 3 and len(data) < 5000:
                stat_sw, p_sw = shapiro(data)
                is_normal_sw = p_sw > alpha
            else:
                stat_sw, p_sw, is_normal_sw = None, None, None

            # Kolmogorov-Smirnov is a general goodness-of-fit test
            stat_ks, p_ks = kstest(data, 'norm', args=(data.mean(), data.std()))
            is_normal_ks = p_ks > alpha

            normality_results[col] = {
                "shapiro_wilk": {"statistic": stat_sw, "p_value": p_sw, "is_normal": is_normal_sw},
                "kolmogorov_smirnov": {"statistic": stat_ks, "p_value": p_ks, "is_normal": is_normal_ks},
            }
        return normality_results

    def _calculate_correlation_matrix(self) -> Dict[str, Dict[str, float]]:
        """
        Calculates both Pearson and Spearman correlation matrices for numeric columns.
        """
        # Ensure we only use numeric columns for correlation
        numeric_df = self.df[self.numeric_cols]

        pearson_corr = numeric_df.corr(method='pearson')
        spearman_corr = numeric_df.corr(method='spearman')

        return {
            "pearson": pearson_corr.to_dict(),
            "spearman": spearman_corr.to_dict()
        }

    def select_and_run_test(self, var1: str, var2: str) -> Dict[str, Any]:
        """
        Automatically selects and runs the appropriate statistical test based on
        the variable types.
        """
        type1 = self.classified_types.get(var1)
        type2 = self.classified_types.get(var2)

        if not type1 or not type2:
            raise ValueError("One or both variables not found in dataset.")

        # --- Test Selection Logic ---
        if type1.startswith('categorical') and type2.startswith('categorical'):
            # Chi-Squared test for independence
            contingency_table = pd.crosstab(self.df[var1], self.df[var2])
            chi2, p, dof, ex = chi2_contingency(contingency_table)
            return {
                "test_name": "Chi-Squared Test of Independence",
                "justification": "Comparing two categorical variables.",
                "statistic": chi2,
                "p_value": p,
                "degrees_of_freedom": dof
            }

        elif type1.startswith('categorical') and type2.startswith('numeric'):
            var_cat, var_num = var1, var2
        elif type1.startswith('numeric') and type2.startswith('categorical'):
            var_cat, var_num = var2, var1
        else: # Both numeric
            # Handled by correlation matrix, but we can return a specific value
            pearson_corr = self.df[[var1, var2]].corr(method='pearson').iloc[0, 1]
            return {
                "test_name": "Pearson Correlation",
                "justification": "Comparing two numeric variables.",
                "correlation_coefficient": pearson_corr,
            }

        # Logic for Categorical vs. Numeric
        # Check normality of the numeric variable for each category
        groups = [group[var_num].dropna() for name, group in self.df.groupby(var_cat)]

        # Simple normality check using Shapiro on the first group as a heuristic
        is_normal = len(groups[0]) > 3 and shapiro(groups[0])[1] > 0.05

        if is_normal and len(groups) > 1:
            # ANOVA
            f_stat, p_val = f_oneway(*groups)
            return {
                "test_name": "ANOVA",
                "justification": "Comparing means of a numeric variable across multiple categories (assuming normality).",
                "f_statistic": f_stat,
                "p_value": p_val
            }
        elif len(groups) > 1:
            # Kruskal-Wallis (non-parametric alternative)
            h_stat, p_val = kruskal(*groups)
            return {
                "test_name": "Kruskal-Wallis H-test",
                "justification": "Comparing distributions of a numeric variable across multiple categories (non-parametric).",
                "h_statistic": h_stat,
                "p_value": p_val
            }
        else:
             return {"test_name": "Test not applicable", "justification": "Insufficient groups for comparison."}
