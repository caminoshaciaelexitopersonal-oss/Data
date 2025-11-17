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
    LEVENSHTEIN_THRESHOLD = 80 # Lowered slightly for flexibility
    HIGH_NULL_THRESHOLD = 0.7

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

    def generate_column_map(self, dataframes: List[pd.DataFrame]) -> Dict[str, List[str]]:
        if not dataframes: return {}
        canonical_columns = list(dataframes[0].columns)
        column_map: Dict[str, List[str]] = {col: [col] for col in canonical_columns}

        # Normalize the canonical columns for matching
        normalized_canonical = {self._normalize_string(c): c for c in canonical_columns}

        for df in dataframes[1:]:
            for col in df.columns:
                if col in canonical_columns or col in (item for sublist in column_map.values() for item in sublist):
                    continue

                normalized_col = self._normalize_string(col)

                # Use rapidfuzz to find the best match from the normalized canonical names
                result = process.extractOne(normalized_col, normalized_canonical.keys(), scorer=fuzz.WRatio, score_cutoff=self.LEVENSHTEIN_THRESHOLD)

                if result:
                    best_match_normalized = result[0]
                    original_canonical_name = normalized_canonical[best_match_normalized]
                    column_map[original_canonical_name].append(col)
                    logger.info(f"Mapped '{col}' to canonical column '{original_canonical_name}' with score {result[1]}")

        unmapped_final = {col for df in dataframes for col in df.columns} - {item for sublist in column_map.values() for item in sublist}
        if unmapped_final: logger.warning(f"Unmapped columns: {list(unmapped_final)}")
        return column_map

    # ... [Rest of the class uses the previous correct logic] ...
    def _resolve_conflicts_for_group(self, group: pd.DataFrame) -> pd.Series:
        group = group.sort_values('__source_precedence')
        final_record = {}
        for col in group.columns:
            if col == '__source_precedence': continue
            valid_values = group[col].dropna()
            if valid_values.empty:
                final_record[col] = None
                continue
            final_record[col] = valid_values.iloc[0]
        return pd.Series(final_record)
    def merge_dataframes(self, dataframes: List[pd.DataFrame], column_map: Dict[str, List[str]], source_precedence: List[str]) -> pd.DataFrame:
        processed_dfs = []
        precedence_map = {name: i for i, name in enumerate(source_precedence)}
        for i, df in enumerate(dataframes):
            rename_dict = {alias: canon for canon, aliases in column_map.items() for alias in aliases if alias in df.columns}
            df_renamed = df.rename(columns=rename_dict)
            original_filename = source_precedence[i]
            df_renamed['__source_precedence'] = precedence_map[original_filename]
            processed_dfs.append(df_renamed)
        concatenated_df = pd.concat(processed_dfs, ignore_index=True)
        id_column = next((col for col in column_map if "id" in self._normalize_string(col)), None)
        if id_column:
            logger.info(f"Using '{id_column}' for conflict resolution.")
            merged_df = concatenated_df.groupby(id_column, group_keys=False).apply(self._resolve_conflicts_for_group)
            merged_df = merged_df.reset_index(drop=True)
        else:
            logger.warning("No ID column found. Using simple duplicate removal.")
            merged_df = concatenated_df.drop_duplicates(keep='first').drop(columns=['__source_precedence'])
        final_columns = list(column_map.keys())
        for col in final_columns:
            if col not in merged_df.columns: merged_df[col] = pd.NA
        merged_df = merged_df[final_columns]
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
        validation_results = {"issues": [], "high_null_columns": [], "missing_required_columns": [], "type_inconsistencies": []}
        logger.info("--- Starting Pre-Merge Validation ---")
        mapped_canonical_cols = set(column_map.keys())
        if required_columns:
            for req_col in required_columns:
                if req_col not in mapped_canonical_cols:
                    issue = f"Required column '{req_col}' is missing in all files."
                    logger.error(issue); validation_results["missing_required_columns"].append(req_col)
        for canon_col, aliases in column_map.items():
            col_types = set()
            for i, df in enumerate(dataframes):
                for alias in aliases:
                    if alias in df.columns:
                        col_types.add(self._get_probable_dtype(df[alias]))
            if len(col_types) > 1 and 'empty' not in col_types:
                issue = f"Canonical column '{canon_col}' has inconsistent types: {list(col_types)}"
                logger.warning(issue); validation_results["type_inconsistencies"].append(issue)
        for i, df in enumerate(dataframes):
            filename = filenames[i]
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
            "initial_total_rows": stats.get("initial_rows", 0),
            "final_merged_rows": stats.get("final_rows", 0),
            "unified_columns_map": stats.get("column_map", {}), "discarded_columns": stats.get("unmapped_columns", []),
            "conflicts_resolved": stats.get("initial_rows", 0) - stats.get("final_rows", 0),
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
