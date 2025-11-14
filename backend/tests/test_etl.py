import pytest
from unittest.mock import patch
from backend.app.services import etl_service
from backend.app.etl_providers import loader_jsonl, loader_tsv

@patch('backend.app.services.audit_service.write_audit_log')
def test_orchestrate_etl_calls_audit_service(mock_write_audit_log):
    """Tests that the ETL orchestrator calls the audit service."""
    sources = [{"name": "source1.csv", "type": "csv"}]
    etl_service.orchestrate_etl(sources)
    mock_write_audit_log.assert_called_once()

def test_jsonl_loader_with_mock_data(tmp_path):
    """Tests the JSONL loader."""
    content = '{"a": 1}\n{"a": 2}'
    mock_file = tmp_path / "test.jsonl"
    mock_file.write_text(content)
    df, _ = loader_jsonl.load(str(mock_file))
    assert len(df) == 2

def test_tsv_loader_with_mock_data(tmp_path):
    """Tests the TSV loader."""
    content = "col1\tcol2\nval1\tval2"
    mock_file = tmp_path / "test.tsv"
    mock_file.write_text(content)
    df, _ = loader_tsv.load(str(mock_file))
    assert len(df) == 1
