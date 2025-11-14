import pandas as pd
import re
from typing import Dict, Any, List, Callable

# --- Lógica de Conversión ---

def _to_snake_case(name: str) -> str:
    """Convierte un string a snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    return re.sub(r'[\s\-]+', '_', s2)

# --- Pasos de Transformación Modulares ---

def handle_null_values(df: pd.DataFrame, strategy: str = 'mean', subset: List[str] = None) -> pd.DataFrame:
    """Maneja los valores nulos en el DataFrame."""
    if strategy == 'drop':
        df.dropna(subset=subset, inplace=True)
    elif strategy in ['mean', 'median', 'mode']:
        for col in subset or df.columns:
            if df[col].isnull().any():
                if pd.api.types.is_numeric_dtype(df[col]):
                    fill_value = getattr(df[col], strategy)()
                    df[col].fillna(fill_value, inplace=True)
    return df

def convert_data_types(df: pd.DataFrame, type_mapping: Dict[str, str]) -> pd.DataFrame:
    """Convierte los tipos de datos de las columnas según el mapeo."""
    for col, new_type in type_mapping.items():
        if col in df.columns:
            try:
                if new_type == 'datetime':
                    df[col] = pd.to_datetime(df[col])
                else:
                    df[col] = df[col].astype(new_type)
            except (TypeError, ValueError) as e:
                print(f"No se pudo convertir la columna '{col}' a {new_type}: {e}")
    return df

def remove_duplicates(df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
    """Elimina filas duplicadas."""
    df.drop_duplicates(subset=subset, inplace=True)
    return df

def rename_columns(df: pd.DataFrame, rename_mapping: Dict[str, str]) -> pd.DataFrame:
    """Renombra las columnas según el mapeo."""
    df.rename(columns=rename_mapping, inplace=True)
    return df

def convert_columns_to_snake_case(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte todos los nombres de las columnas de un DataFrame a snake_case."""
    df.columns = [_to_snake_case(col) for col in df.columns]
    return df

# --- Mapeo de pasos del pipeline ---

PIPELINE_STEPS: Dict[str, Callable[..., pd.DataFrame]] = {
    'handle_nulls': handle_null_values,
    'convert_types': convert_data_types,
    'remove_duplicates': remove_duplicates,
    'rename_columns': rename_columns,
    'to_snake_case': convert_columns_to_snake_case,
}

# --- Orquestador del Pipeline ---

def run_normalization_pipeline(df: pd.DataFrame, config: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Ejecuta una serie de pasos de normalización en un DataFrame basados en una configuración.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("La entrada 'df' debe ser un DataFrame de pandas.")

    processed_df = df.copy()

    for step_config in config:
        step_name = step_config.get('step')
        params = step_config.get('params', {})

        if step_name in PIPELINE_STEPS:
            transform_function = PIPELINE_STEPS[step_name]
            try:
                # Pasar solo 'processed_df' si no hay 'params'
                if not params:
                    processed_df = transform_function(processed_df)
                else:
                    processed_df = transform_function(processed_df, **params)
            except Exception as e:
                print(f"Error en el paso del pipeline '{step_name}': {e}")
        else:
            print(f"Advertencia: Paso del pipeline '{step_name}' no reconocido y será omitido.")

    return processed_df
