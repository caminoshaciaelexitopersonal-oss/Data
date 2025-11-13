import pandas as pd
from typing import List, Dict, Any
from sklearn.preprocessing import StandardScaler, MinMaxScaler

def run_pipeline(data: pd.DataFrame, steps: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Ejecuta un pipeline de transformaciones sobre un DataFrame de pandas.

    :param data: El DataFrame de entrada.
    :param steps: Una lista de diccionarios, donde cada uno representa un paso.
    :return: El DataFrame transformado.
    """
    df = data.copy()

    for step in steps:
        action = step.get("action")
        column = step.get("column")

        if not action or not column or column not in df.columns:
            print(f"Omitiendo paso inválido: {step}")
            continue

        print(f"Ejecutando paso del pipeline: {action} en la columna '{column}'")

        if action == "drop_nulls":
            df.dropna(subset=[column], inplace=True)

        elif action == "fill_nulls":
            strategy = step.get("strategy", "mean") # mean, median, mode
            if strategy == "mean":
                fill_value = df[column].mean()
            elif strategy == "median":
                fill_value = df[column].median()
            elif strategy == "mode":
                fill_value = df[column].mode()[0]
            else:
                fill_value = 0 # Valor por defecto
            df[column].fillna(fill_value, inplace=True)

        elif action == "normalize":
            method = step.get("method", "z-score") # z-score, min-max
            scaler = StandardScaler() if method == "z-score" else MinMaxScaler()

            # Reshape es necesario para una sola columna
            df[column] = scaler.fit_transform(df[[column]])

        elif action == "one_hot_encode":
            # Usar pd.get_dummies para una implementación robusta
            dummies = pd.get_dummies(df[column], prefix=column)
            df = pd.concat([df.drop(column, axis=1), dummies], axis=1)

        elif action == "drop_column":
            df.drop(columns=[column], inplace=True)

        else:
            print(f"Acción desconocida en el pipeline: {action}")

    return df
