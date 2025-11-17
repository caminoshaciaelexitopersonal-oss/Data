from typing import Dict, Any, List

def select_pipeline(metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Selecciona un pipeline de ETL basado en los metadatos del dataset y el objetivo.

    Args:
        metadata (Dict[str, Any]): Un diccionario con 'dataset_shape', 'columns',
                                   'numerical_columns', 'categorical_columns',
                                   y 'user_intent'.

    Returns:
        List[Dict[str, Any]]: Una lista de pasos que definen el pipeline de ETL.
    """
    num_rows, num_cols = metadata.get('dataset_shape', (0, 0))
    user_intent = metadata.get('user_intent', 'unknown')

    pipeline_steps = []

    # --- Pipeline Simple (Default) ---
    pipeline_steps.extend([
        {"action": "drop_nulls", "column": "default_column_to_check"},
        {"action": "fill_nulls", "column": "another_column", "value": 0}
    ])

    # --- Pipeline Avanzado (para datasets más grandes o intención de ML) ---
    if num_rows > 1000 or user_intent == 'ML':
        pipeline_steps.append(
            {"action": "normalize", "columns": metadata.get('numerical_columns', [])}
        )
        if len(metadata.get('categorical_columns', [])) > 0:
            pipeline_steps.append(
                {"action": "one_hot_encode", "columns": metadata.get('categorical_columns', [])}
            )

    # --- Pipeline de Feature Engineering (si la intención es ML) ---
    if user_intent == 'ML':
        # Ejemplo: Crear una nueva característica a partir de dos existentes
        if 'age' in metadata.get('columns', []) and 'income' in metadata.get('columns', []):
            pipeline_steps.append(
                {"action": "create_feature", "name": "income_per_age", "expression": "income / age"}
            )

    # Lógica de ejemplo para personalizar el pipeline
    if 'product_name' in metadata.get('columns', []):
        pipeline_steps.append(
            {"action": "rename", "columns": {"product_name": "nombre_producto"}}
        )

    return pipeline_steps
