import pytest
import pandas as pd
from backend.wpa.intelligent_merge.service import IntelligentMergeService

@pytest.fixture
def merge_service():
    return IntelligentMergeService()

@pytest.fixture
def sample_dataframes():
    # Covers different scenarios: synonyms, typos, different data types
    df_excel = pd.DataFrame({
        'ID': [1, 2, 3],
        'Nombre Completo': ['Alice Smith', 'Bob Johnson', 'Charlie Brown'],
        'email': ['alice@example.com', 'bob@example.com', 'charlie@example.com'],
        'Monto': [100, 200, 150]
    })

    df_csv = pd.DataFrame({
        'Identifier': [1, 2, 4],
        'Full Name': ['Alice Smith', 'Robert Johnson', 'David Davis'],
        'correo': ['alice@example.com', 'bob_j@example.com', 'dave@example.com'],
        'Amount': [105, 200, 300]
    })

    df_json = pd.DataFrame({
        'codigo': [1, 3, 5],
        'nombre': ['Alicia Smith', 'Charles Brown', 'Eve Williams'],
        'mail': ['alice_s@example.com', 'charlie_b@example.com', 'eve@example.com'],
        'valor': [100, 155, 500]
    })

    return [df_excel, df_csv, df_json]

@pytest.fixture
def file_names():
    return ["data.xlsx", "data.csv", "data.json"]

def test_intelligent_column_mapping(merge_service, sample_dataframes):
    column_map = merge_service.generate_column_map(sample_dataframes)

    assert 'ID' in column_map
    assert 'Identifier' in column_map['ID']
    assert 'codigo' in column_map['ID']

    assert 'Nombre Completo' in column_map
    assert 'Full Name' in column_map['Nombre Completo']
    assert 'nombre' in column_map['Nombre Completo']

    assert 'email' in column_map
    assert 'correo' in column_map['email']
    assert 'mail' in column_map['email']

    assert 'Monto' in column_map
    assert 'Amount' in column_map['Monto']
    assert 'valor' in column_map['Monto']

def test_conflict_resolution_with_hierarchy_and_frequency(merge_service, sample_dataframes, file_names):
    column_map = merge_service.generate_column_map(sample_dataframes)
    merged_df = merge_service.merge_dataframes(sample_dataframes, column_map, file_names)

    # ID 1: Alice Smith exists in all 3. Excel name should be chosen. Amount has 2x 100, 1x 105. 100 should win.
    alice_record = merged_df[merged_df['ID'] == 1].iloc[0]
    assert alice_record['Nombre Completo'] == 'alice smith' # Normalized
    assert alice_record['Monto'] == 100
    assert alice_record['email'] == 'alice@example.com' # Excel has precedence

    # ID 2: Bob Johnson vs Robert Johnson. Amount is 200 in both. Email: Excel has precedence
    bob_record = merged_df[merged_df['ID'] == 2].iloc[0]
    assert bob_record['Nombre Completo'] == 'bob johnson' # Excel has precedence
    assert bob_record['Monto'] == 200
    assert bob_record['email'] == 'bob@example.com' # Excel has precedence

    # ID 3: Charlie Brown vs Charles Brown. Monto: 150 vs 155. Excel has precedence.
    charlie_record = merged_df[merged_df['ID'] == 3].iloc[0]
    assert charlie_record['Nombre Completo'] == 'charlie brown' # Excel has precedence
    assert charlie_record['Monto'] == 150 # Excel has precedence

def test_corrupt_row_validation(merge_service):
    df1 = pd.DataFrame({'ID': [1, 2, 3], 'Name': ['A', 'B', None]})
    df2 = pd.DataFrame({'Identifier': [4, 5], 'Name': ['D', 'E']})

    dataframes = [df1, df2]
    filenames = ['file1.csv', 'file2.csv']
    column_map = merge_service.generate_column_map(dataframes)

    validation_results = merge_service._validate_and_log(dataframes, filenames, column_map, required_columns=['ID', 'Name'])

    assert len(validation_results['corrupt_rows_report']) == 1
    assert validation_results['corrupt_rows_report'][0]['file'] == 'file1.csv'
    assert validation_results['corrupt_rows_report'][0]['corrupt_rows_count'] == 1

def test_quality_report_bug_fix(merge_service, sample_dataframes, file_names):
    # This test implicitly checks the bug fix by running the full pipeline
    # and ensuring the report can be generated without errors and has correct keys.
    _, report_path = merge_service.run_merge_pipeline(sample_dataframes, file_names)

    import json
    with open(report_path, 'r') as f:
        report = json.load(f)

    initial_total_rows = sum(len(df) for df in sample_dataframes)
    assert report['initial_total_rows'] == initial_total_rows
    assert report['conflicts_resolved'] == initial_total_rows - report['final_merged_rows']
    assert 'corrupt_rows_report' in report['validation_issues']
