# backend/visualizations.py
from typing import Dict, Any

# Este diccionario actuará como nuestro almacén de datos de visualización en memoria.
# Cada clave representará un tipo de gráfico (ej. 'etl_summary', 'kmeans_clusters').
visualization_data: Dict[str, Any] = {}

def clear_visualizations():
    """Limpia todos los datos de visualización almacenados."""
    visualization_data.clear()
    print("Datos de visualización limpiados.")

def add_visualization(name: str, data: Any):
    """
    Añade o actualiza los datos de una visualización específica.

    :param name: El nombre clave de la visualización (ej. 'kmeans_clusters').
    :param data: Los datos a almacenar, usualmente una lista de diccionarios.
    """
    visualization_data[name] = data
    print(f"Visualización '{name}' añadida/actualizada.")

def get_all_visualizations() -> Dict[str, Any]:
    """
    Devuelve todos los datos de visualización almacenados.
    """
    # Para asegurar que la respuesta siempre tenga una estructura consistente,
    # podemos devolver datos de ejemplo si no se ha generado nada aún.
    if not visualization_data:
        return get_mock_visualizations()
    return visualization_data

def get_mock_visualizations() -> Dict[str, Any]:
    """
    Devuelve un conjunto de datos de ejemplo para desarrollo y pruebas del frontend.
    """
    return {
        "etl_summary": [
            {"feature": "mean_radius", "mean": 14.1, "std": 3.5},
            {"feature": "mean_texture", "mean": 19.3, "std": 4.4},
            {"feature": "mean_perimeter", "mean": 91.9, "std": 24.2},
        ],
        "kmeans_clusters": [
            {"cluster": "Grupo 1", "count": 357, "color": "#22c55e"},
            {"cluster": "Grupo 2", "count": 212, "color": "#ef4444"},
        ],
        "classification_accuracy": [
            {"modelo": "Naive Bayes", "accuracy": 0.94},
            {"modelo": "Random Forest (Ejemplo)", "accuracy": 0.97},
        ],
        "regression_plot": [
            {"x": 1, "y_real": 3.2, "y_pred": 3.1},
            {"x": 2, "y_real": 4.5, "y_pred": 4.4},
            {"x": 3, "y_real": 5.1, "y_pred": 5.2},
            {"x": 4, "y_real": 6.8, "y_pred": 6.7},
        ]
    }
