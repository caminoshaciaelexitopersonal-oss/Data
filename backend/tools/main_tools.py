from langchain.tools import tool

# Import task functions from celery_worker
from backend.celery_worker import (
    run_kmeans_task,
    generate_correlation_heatmap_task,
    run_linear_regression_task,
    run_arima_forecast_task,
    fetch_api_data_task,
    explain_model_features_task
)

# In a real application, you would define your tools here.
# For example:
# @tool
# def my_custom_tool(input: str) -> str:
#     """A brief description of what my tool does."""
#     return "Result from my tool"

# This function will gather and return all defined tools.
def get_tools():
    # return [my_custom_tool]
    return []
