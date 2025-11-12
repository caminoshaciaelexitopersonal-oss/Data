import pandas as pd
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

plt.switch_backend('Agg')

def run_kmeans_tool(data: List[Dict[str, Any]], k: int, features: List[str]) -> Dict[str, Any]:
    try:
        df = pd.DataFrame(data)
        if df.empty: return {"error": "Los datos están vacíos."}
        for feature in features:
            if feature not in df.columns: return {"error": f"La característica '{feature}' no se encuentra en los datos."}
        X = df[features].values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        assignments = kmeans.labels_.tolist()
        centroids = scaler.inverse_transform(kmeans.cluster_centers_).tolist()
        return { "assignments": assignments, "centroids": centroids, "featureNames": features, "algorithm": "kmeans" }
    except Exception as e:
        return {"error": f"Error en el análisis de K-Means: {e}"}

def generate_correlation_heatmap_tool(data: List[Dict[str, Any]]) -> Dict[str, str]:
    try:
        df = pd.DataFrame(data)
        if df.empty: return {"error": "No hay datos para generar el mapa de calor."}
        numeric_df = df.select_dtypes(include=['number'])
        if numeric_df.shape[1] < 2:
            return {"error": "Se necesitan al menos dos características numéricas para un mapa de calor de correlación."}
        corr_matrix = numeric_df.corr()
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='coolwarm', ax=ax)
        ax.set_title('Mapa de Calor de Correlación')
        plt.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        return { "image_base64": image_base64, "description": "Aquí está el mapa de calor de correlación." }
    except Exception as e:
        return {"error": f"Error al generar el mapa de calor: {e}"}

def run_linear_regression_tool(data: List[Dict[str, Any]], target: str, feature: str) -> Dict[str, Any]:
    try:
        df = pd.DataFrame(data)
        if df.empty: return {"error": "Los datos están vacíos."}
        if target not in df.columns or feature not in df.columns:
            return {"error": "Las variables no se encuentran en los datos."}
        X = df[[feature]].values
        y = df[target].values
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        line_x = [df[feature].min(), df[feature].max()]
        line_y = model.predict([[line_x[0]], [line_x[1]]]).tolist()
        return { "rSquared": r2, "mse": mse, "targetVariable": target, "featureVariables": [feature], "line_points": {"x": line_x, "y": line_y} }
    except Exception as e:
        return {"error": f"Error en la regresión lineal: {e}"}
