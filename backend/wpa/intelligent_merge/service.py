import pandas as pd
import jellyfish
from rapidfuzz import fuzz, process
from typing import List, Dict, Set, Any, Tuple
import unicodedata
import re
import logging
import json
import os
from datetime import datetime
import sqlite3

# ... [Configuration and Setup] ...
LOG_DIRECTORY = "/tmp/sadi_logs"
EXPORT_DIRECTORY = "/tmp/sadi_exports"
LOG_FILE_PATH = os.path.join(LOG_DIRECTORY, 'intelligent_merge.log')
REPORT_FILE_PATH = os.path.join(LOG_DIRECTORY, 'reporte_calidad_unificacion.json')
os.makedirs(LOG_DIRECTORY, exist_ok=True); os.makedirs(EXPORT_DIRECTORY, exist_ok=True)
logger = logging.getLogger('intelligent_merge')
if not logger.handlers:
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(LOG_FILE_PATH)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

class IntelligentMergeService:
    # ... (Constants)
    LEVENSHTEIN_THRESHOLD = 80 # This will be replaced by a weighted score threshold
    SIMILARITY_THRESHOLD = 0.55 # Adjusted threshold
    HIGH_NULL_THRESHOLD = 0.7

    # Semantic synonym groups for column name matching
    SYNONYM_GROUPS = [
        {'id', 'identifier', 'key', 'code', 'number', 'numero', 'codigo'},
        {'customer', 'client', 'user', 'patron', 'cliente', 'usuario'},
        {'name', 'fullname', 'nombre', 'nombre_completo', 'full_name'},
        {'firstname', 'givenname', 'fname', 'primer_nombre'},
        {'lastname', 'surname', 'lname', 'apellido'},
        {'email', 'emailaddress', 'mail', 'correo'},
        {'phone', 'phonenumber', 'telephone', 'telefono'},
        {'address', 'location', 'street', 'direccion'},
        {'city', 'town', 'municipality', 'ciudad'},
        {'state', 'province', 'region', 'estado', 'provincia'},
        {'zip', 'zipcode', 'postalcode', 'codigo_postal'},
        {'country', 'nation', 'pais'},
        {'date', 'timestamp', 'time', 'fecha'},
        {'amount', 'value', 'price', 'total', 'monto', 'valor', 'precio'},
        {'quantity', 'qty', 'count', 'cantidad'},
    ]

    def __init__(self):
        # Normalize the synonym map for efficient lookup
        self.SYNONYM_MAP = {self._normalize_string(word): i for i, group in enumerate(self.SYNONYM_GROUPS) for word in group}

    def _normalize_string(self, s: str) -> str:
        if not isinstance(s, str): return ""
        s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
        s = re.sub(r'[^a-z0-9]', '', s.lower().replace('_', ''))
        return s

    def _get_probable_dtype(self, series: pd.Series) -> str:
        series = series.dropna().sample(n=min(100, len(series.dropna())), random_state=1)
        if series.empty: return "empty"
        if series.astype(str).str.lower().isin(['true', 'false', '1', '0', 't', 'f', 'y', 'n', 'yes', 'no']).all():
            return "boolean"
        try:
            numeric_series = pd.to_numeric(series)
            return "integer" if (numeric_series % 1 == 0).all() else "float"
        except (ValueError, TypeError):
            pass
        try:
            pd.to_datetime(series, errors='raise'); return "datetime"
        except (ValueError, TypeError): pass
        return "string"

    def _calculate_similarity_score(self, col1_norm: str, col2_norm: str, dtype1: str, dtype2: str) -> float:
        """Calculates a weighted similarity score between two columns."""
        # 1. Levenshtein (WRatio) - Weight: 0.5
        lev_score = fuzz.WRatio(col1_norm, col2_norm) / 100.0

        # 2. Phonetic (Jaro-Winkler) - Weight: 0.2
        phonetic_score = jellyfish.jaro_winkler_similarity(col1_norm, col2_norm)

        # 3. Semantic (Synonym) - Weight: 0.2
        synonym_score = 0.0
        col1_group = self.SYNONYM_MAP.get(col1_norm)
        col2_group = self.SYNONYM_MAP.get(col2_norm)
        if col1_group is not None and col1_group == col2_group:
            synonym_score = 1.0

        # 4. Data Type Match - Weight: 0.1
        type_score = 1.0 if dtype1 == dtype2 and dtype1 != "empty" else 0.0

        # Weighted average with adjusted weights
        total_score = (lev_score * 0.4) + (phonetic_score * 0.1) + (synonym_score * 0.4) + (type_score * 0.1)

        return total_score

    def generate_column_map(self, dataframes: List[pd.DataFrame]) -> Dict[str, List[str]]:
        if not dataframes: return {}

        # Use the first dataframe's columns as the canonical standard
        canonical_df = dataframes[0]
        canonical_columns = list(canonical_df.columns)
        column_map: Dict[str, List[str]] = {col: [col] for col in canonical_columns}

        # Pre-calculate dtypes and normalized names for the canonical columns
        canonical_info = {
            col: (self._normalize_string(col), self._get_probable_dtype(canonical_df[col]))
            for col in canonical_columns
        }

        # Iterate through the rest of the dataframes to map their columns
        for df in dataframes[1:]:
            for col in df.columns:
                # Skip if column is already perfectly mapped to a canonical one
                if col in canonical_columns:
                    continue
                # Skip if it has been mapped as an alias already
                if any(col in v for v in column_map.values()):
                    continue

                col_norm = self._normalize_string(col)
                col_dtype = self._get_probable_dtype(df[col])

                best_match_score = -1.0
                best_match_canon = None

                for canon_col, (canon_norm, canon_dtype) in canonical_info.items():
                    score = self._calculate_similarity_score(col_norm, canon_norm, col_dtype, canon_dtype)
                    if score > best_match_score:
                        best_match_score = score
                        best_match_canon = canon_col

                if best_match_canon and best_match_score >= self.SIMILARITY_THRESHOLD:
                    column_map[best_match_canon].append(col)
                    logger.info(f"Mapped column '{col}' to canonical '{best_match_canon}' with score {best_match_score:.2f}")
                else:
                    logger.warning(f"Column '{col}' could not be confidently mapped. Best score: {best_match_score:.2f}")

        unmapped_final = {col for df in dataframes for col in df.columns} - {item for sublist in column_map.values() for item in sublist}
        if unmapped_final: logger.warning(f"Unmapped columns: {list(unmapped_final)}")
        return column_map

    def _get_source_precedence(self, filename: str) -> int:
        """Assigns a numerical precedence based on file extension."""
        ext = os.path.splitext(filename)[1].lower()
        if 'xls' in ext: return 0 # Excel
        if 'csv' in ext: return 1 # CSV
        if 'json' in ext: return 2 # JSON
        # Assuming SQL sources will be identified differently, but for now:
        if 'sql' in ext or 'db' in ext: return 3 # SQL
        return 99 # Other types

    def _resolve_conflicts_for_group(self, group: pd.DataFrame) -> pd.Series:
        """Resolves conflicts for a group of rows based on source precedence and value frequency."""
        # Sort by the defined source precedence (lower is better)
        group = group.sort_values('__source_precedence', ascending=True)

        final_record = {}
        for col in group.columns:
            if col in ['__source_precedence', '__id_column']:  # Exclude helper columns
                continue

            valid_values = group[col].dropna()

            if valid_values.empty:
                final_record[col] = None
                continue

            # If there's more than one valid value, decide based on frequency
            if len(valid_values) > 1:
                value_counts = valid_values.value_counts()
                # If the most frequent value is unique, use it
                if len(value_counts) > 1 and value_counts.iloc[0] > value_counts.iloc[1]:
                    final_record[col] = value_counts.index[0]
                else:
                    # If frequencies are tied, fall back to the highest precedence source
                    final_record[col] = valid_values.iloc[0]
            else:
                # If only one valid value, use it
                final_record[col] = valid_values.iloc[0]

        return pd.Series(final_record)

    def merge_dataframes(self, dataframes: List[pd.DataFrame], column_map: Dict[str, List[str]], source_filenames: List[str]) -> pd.DataFrame:
        processed_dfs = []
        for i, df in enumerate(dataframes):
            rename_dict = {alias: canon for canon, aliases in column_map.items() for alias in aliases if alias in df.columns}
            df_renamed = df.rename(columns=rename_dict)

            original_filename = source_filenames[i]
            df_renamed['__source_precedence'] = self._get_source_precedence(original_filename)
            processed_dfs.append(df_renamed)

        concatenated_df = pd.concat(processed_dfs, ignore_index=True)

        id_column = next((col for col in column_map if "id" in self._normalize_string(col)), None)
        if id_column:
            logger.info(f"Using '{id_column}' for conflict resolution.")
            # Use a stable sort to maintain original order for tie-breaking
            concatenated_df = concatenated_df.sort_values('__source_precedence', kind='mergesort')
            merged_df = concatenated_df.groupby(id_column, group_keys=False).apply(self._resolve_conflicts_for_group)
            merged_df = merged_df.reset_index(drop=True) # Reset index after groupby.apply
        else:
            logger.warning("No ID column found. Using simple duplicate removal based on precedence.")
            # Sort by precedence and then drop duplicates, keeping the first (highest precedence)
            concatenated_df = concatenated_df.sort_values('__source_precedence', kind='mergesort')
            # Determine all columns except the helper one
            final_columns = [col for col in concatenated_df.columns if col != '__source_precedence']
            merged_df = concatenated_df.drop_duplicates(subset=final_columns, keep='first')

        # Clean up helper column
        if '__source_precedence' in merged_df.columns:
            merged_df = merged_df.drop(columns=['__source_precedence'])

        # Ensure all canonical columns are present in the final dataframe
        final_columns_set = set(column_map.keys())
        for col in final_columns_set:
            if col not in merged_df.columns:
                merged_df[col] = pd.NA

        # Reorder columns to match the canonical order
        ordered_columns = [col for col in column_map.keys() if col in merged_df.columns]
        merged_df = merged_df[ordered_columns]

        final_df = self._normalize_and_clean(merged_df)
        logger.info(f"Merge complete. Initial: {len(concatenated_df)}, Final: {len(final_df)}")
        return final_df
    def _normalize_and_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        df_copy = df.copy()
        for col in df_copy.columns:
            dtype = self._get_probable_dtype(df_copy[col])
            if dtype == 'datetime': df_copy[col] = pd.to_datetime(df_copy[col], errors='coerce').dt.strftime('%Y-%m-%dT%H:%M:%S')
            elif dtype in ['integer', 'float']: df_copy[col] = pd.to_numeric(df_copy[col].astype(str).str.replace(r'[$,%]', '', regex=True), errors='coerce')
            elif dtype == 'boolean':
                df_copy[col] = df_copy[col].astype(str).str.lower().isin(['true', '1', 't', 'y', 'yes']).astype(bool)
            elif dtype == 'string':
                df_copy[col] = df_copy[col].astype(str).str.strip().str.lower()
                df_copy[col] = df_copy[col].apply(lambda x: ''.join(c for c in unicodedata.normalize('NFD', x) if unicodedata.category(c) != 'Mn') if isinstance(x, str) else x)
        return df_copy
    def _validate_and_log(self, dataframes: List[pd.DataFrame], filenames: List[str], column_map: Dict[str, List[str]], required_columns: List[str] = None) -> Dict[str, Any]:
        validation_results = {"issues": [], "high_null_columns": [], "missing_required_columns": [], "type_inconsistencies": [], "corrupt_rows_report": []}
        logger.info("--- Starting Pre-Merge Validation ---")

        mapped_canonical_cols = set(column_map.keys())

        # 1. Check for missing required columns from the entire dataset
        if required_columns:
            for req_col in required_columns:
                if req_col not in mapped_canonical_cols:
                    issue = f"Required column '{req_col}' is missing in all files."
                    logger.error(issue)
                    validation_results["missing_required_columns"].append(req_col)

        # 2. Check for type inconsistencies across different files for the same canonical column
        for canon_col, aliases in column_map.items():
            col_types = set()
            for i, df in enumerate(dataframes):
                for alias in aliases:
                    if alias in df.columns:
                        col_types.add(self._get_probable_dtype(df[alias]))
            if len(col_types) > 1 and 'empty' not in col_types:
                issue = f"Canonical column '{canon_col}' has inconsistent types: {list(col_types)}"
                logger.warning(issue); validation_results["type_inconsistencies"].append(issue)
        # 3. Detailed per-file validation (high nulls, corrupt rows)
        for i, df in enumerate(dataframes):
            filename = filenames[i]

            # Create a renamed version for consistent checking of required columns
            rename_dict = {alias: canon for canon, aliases in column_map.items() for alias in aliases if alias in df.columns}
            df_renamed = df.rename(columns=rename_dict)

            # Check for corrupt rows (nulls in required columns)
            if required_columns:
                corrupt_rows = df_renamed[df_renamed[required_columns].isnull().any(axis=1)]
                if not corrupt_rows.empty:
                    count = len(corrupt_rows)
                    report = f"In '{filename}', found {count} rows with missing data in required columns."
                    logger.warning(report)
                    validation_results["corrupt_rows_report"].append({"file": filename, "corrupt_rows_count": count})

            if df.empty:
                issue = f"File '{filename}' is empty."
                logger.warning(issue); validation_results["issues"].append(issue)
                continue
            null_ratios = df.isnull().sum() / len(df)
            for col, ratio in null_ratios.items():
                if ratio >= self.HIGH_NULL_THRESHOLD:
                    issue = f"In '{filename}', col '{col}' has high null rate: {ratio:.2%}"
                    logger.warning(issue); validation_results["high_null_columns"].append(f"{filename} -> {col}")
        logger.info("--- Pre-Merge Validation Finished ---")
        return validation_results
    def run_merge_pipeline(self, dataframes: List[pd.DataFrame], filenames: List[str], required_columns: List[str] = None) -> Tuple[pd.DataFrame, str]:
        logger.info("Starting intelligent merge pipeline...")
        column_map = self.generate_column_map(dataframes)
        validation_results = self._validate_and_log(dataframes, filenames, column_map, required_columns)
        if validation_results["missing_required_columns"]:
            raise ValueError(f"Halted: Missing required columns: {validation_results['missing_required_columns']}")
        all_columns = {col for df in dataframes for col in df.columns}; mapped_columns = {alias for aliases in column_map.values() for alias in aliases}
        unmapped_columns = list(all_columns - mapped_columns)
        merged_df = self.merge_dataframes(dataframes, column_map, filenames)
        stats = {
            "filenames": filenames, "initial_total_rows": sum(len(df) for df in dataframes), "final_rows": len(merged_df),
            "column_map": column_map, "unmapped_columns": unmapped_columns, "validation_issues": validation_results
        }
        self._generate_quality_report(stats)
        logger.info("Intelligent merge pipeline finished successfully.")
        return merged_df, REPORT_FILE_PATH
    def _generate_quality_report(self, stats: Dict[str, Any]):
        quality_score = 100
        quality_score -= len(stats.get("unmapped_columns", [])) * 5
        quality_score -= len(stats.get("validation_issues", {}).get("high_null_columns", [])) * 2
        quality_score -= len(stats.get("validation_issues", {}).get("missing_required_columns", [])) * 25
        quality_score -= len(stats.get("validation_issues", {}).get("type_inconsistencies", [])) * 10
        quality_score = max(0, quality_score)
        report = {
            "report_generated_at": datetime.utcnow().isoformat(),
            "processed_files": stats.get("filenames", []), "total_files": len(stats.get("filenames", [])),
            "initial_total_rows": stats.get("initial_total_rows", 0),
            "final_merged_rows": stats.get("final_rows", 0),
            "unified_columns_map": stats.get("column_map", {}), "discarded_columns": stats.get("unmapped_columns", []),
            "conflicts_resolved": stats.get("initial_total_rows", 0) - stats.get("final_rows", 0),
            "validation_issues": stats.get("validation_issues", {}), "final_quality_score_percent": quality_score,
        }
        with open(REPORT_FILE_PATH, 'w') as f: json.dump(report, f, indent=4)
        logger.info(f"Quality report generated at {REPORT_FILE_PATH}")
    def export_to_csv(self, df: pd.DataFrame, filename: str = "output.csv") -> str:
        path = os.path.join(EXPORT_DIRECTORY, filename)
        try: df.to_csv(path, index=False); logger.info(f"Successfully exported to CSV: {path}"); return path
        except Exception as e: logger.error(f"Failed to export to CSV: {e}"); raise
    def export_to_parquet(self, df: pd.DataFrame, filename: str = "output.parquet") -> str:
        path = os.path.join(EXPORT_DIRECTORY, filename)
        try: df.to_parquet(path, index=False); logger.info(f"Successfully exported to Parquet: {path}"); return path
        except Exception as e: logger.error(f"Failed to export to Parquet: {e}"); raise
    def export_to_sql(self, df: pd.DataFrame, filename: str = "output.sqlite", table_name: str = "merged_data") -> str:
        path = os.path.join(EXPORT_DIRECTORY, filename)
        try:
            conn = sqlite3.connect(path); df.to_sql(table_name, conn, if_exists='replace', index=False); conn.close()
            logger.info(f"Successfully exported to SQLite DB: {path} (table: {table_name})"); return path
        except Exception as e: logger.error(f"Failed to export to SQLite: {e}"); raise

intelligent_merge_service = IntelligentMergeService()
