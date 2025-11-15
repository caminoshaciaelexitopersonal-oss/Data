import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import io
import base64
from typing import List, Dict, Any

plt.switch_backend('Agg')

def _generate_plot_base64(fig) -> str:
    """Convierte una figura de matplotlib a un string base64."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def _create_explained_variance_plot(pca: PCA) -> str:
    """Genera un gráfico de varianza explicada acumulada."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(range(1, len(pca.explained_variance_ratio_) + 1), pca.explained_variance_ratio_.cumsum(), marker='o', linestyle='--')
    ax.set_title('Varianza Explicada Acumulada por Componente')
    ax.set_xlabel('Número de Componentes')
    ax.set_ylabel('Varianza Explicada Acumulada')
    ax.grid(True)
    return _generate_plot_base64(fig)

def perform_pca_analysis(data: List[Dict[str, Any]], n_components: int = None) -> Dict[str, Any]:
    """
    Realiza un Análisis de Componentes Principales (PCA) en los datos.

    :param data: Datos de entrada como una lista de diccionarios.
    :param n_components: El número de componentes a retener. Si es None, se retienen todos.
    :return: Un diccionario con los resultados del PCA.
    """
    if not data:
        return {"error": "No se proporcionaron datos para el análisis PCA."}

    try:
        df = pd.DataFrame(data)
        numerical_cols = df.select_dtypes(include=['number']).columns

        if len(numerical_cols) < 2:
            return {"error": "Se requieren al menos dos columnas numéricas para realizar PCA."}

        # Estandarizar los datos antes de PCA
        X = df[numerical_cols]
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Aplicar PCA
        if n_components:
            if n_components > len(numerical_cols):
                return {"error": f"El número de componentes ({n_components}) no puede ser mayor que el número de características numéricas ({len(numerical_cols)})."}
            pca = PCA(n_components=n_components)
        else:
            pca = PCA()

        principal_components = pca.fit_transform(X_scaled)

        # Crear un DataFrame con los componentes principales
        pc_columns = [f'PC_{i+1}' for i in range(principal_components.shape[1])]
        pc_df = pd.DataFrame(data=principal_components, columns=pc_columns)

        # Generar gráfico de varianza explicada
        explained_variance_plot = _create_explained_variance_plot(pca)

        return {
            "status": "success",
            "principal_components": pc_df.to_dict(orient='records'),
            "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
            "cumulative_explained_variance": pca.explained_variance_ratio_.cumsum().tolist(),
            "plots": {
                "explained_variance_plot": explained_variance_plot
            }
        }
    except Exception as e:
        return {"status": "error", "message": f"Ocurrió un error durante el análisis PCA: {e}"}
