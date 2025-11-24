import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from backend.wpa.auto_analysis.ingestion_adapter import strengthen_ingestion
from backend.wpa.auto_analysis.eda_intelligent_service import run_eda

# Create a sample DataFrame for testing
@pytest.fixture
def sample_dataframe():
    data = {
        'ID': range(10),
        'Age': [25, 30, 22, 45, 30, 50, 25, 22, 45, 50],
        'Category': ['A', 'B', 'A', 'C', 'B', 'C', 'A', 'A', 'C', 'B'],
        'Value': [1.1, 2.2, 1.5, 3.3, 2.5, 4.0, 1.8, 1.2, 3.8, 4.2],
        'Target': [0, 1, 0, 1, 1, 1, 0, 0, 1, 1]
    }
    return pd.DataFrame(data)

def test_ingestion_adapter(sample_dataframe):
    """
    Tests the ingestion adapter to ensure it extracts metadata correctly.
    """
    job_id = "test_ingestion"
    with patch('os.makedirs'), patch('builtins.open', new_callable=MagicMock):
        metadata = strengthen_ingestion(sample_dataframe, job_id)

    assert metadata is not None
    assert metadata['num_rows'] == 10
    assert metadata['num_columns'] == 5
    assert 'Age' in metadata['inferred_types']
    assert metadata['inferred_types']['Age'] == 'numeric'
    assert 'Category' in metadata['inferred_types']
    assert metadata['inferred_types']['Category'] == 'categorical'

def test_eda_service(sample_dataframe):
    """
    Tests the EDA service to ensure it generates reports and visualizations.
    """
    job_id = "test_eda"
    inferred_types = {'ID': 'numeric', 'Age': 'numeric', 'Category': 'categorical', 'Value': 'numeric', 'Target': 'numeric'}

    with patch('os.makedirs'), patch('builtins.open', new_callable=MagicMock), patch('matplotlib.pyplot.savefig'):
        # We don't need to check the return, just that it runs without error
        run_eda(sample_dataframe, inferred_types, job_id)

# A more complete test suite would mock the full pipeline in api.py
# and verify that each module is called in sequence. For this plan,
# we are focusing on unit tests for the core components.
