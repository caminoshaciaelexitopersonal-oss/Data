import pandas as pd
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from backend.report_generator import add_plot # Importar

plt.switch_backend('Agg')

def run_kmeans_tool(data: List[Dict[str, Any]], k: int, features: List[str]) -> Dict[str, Any]:
    try:
        df = pd.DataFrame(data)
        if df.empty: return {"error": "Los datos están vacíos."}
        # ... (resto de la lógica se mantiene igual)
        X = df[features].values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        assignments = kmeans.labels_.tolist()
        centroids = scaler.inverse_transform(kmeans.cluster_centers_).tolist()

        # --- Generar y guardar gráfico para el informe ---
        fig, ax = plt.subplots()
        scatter = ax.scatter(X_scaled[:, 0], X_scaled[:, 1], c=assignments, cmap='viridis')
        ax.set_title('Resultado del Clustering K-Means')
        ax.set_xlabel(features[0])
        ax.set_ylabel(features[1] if len(features) > 1 else 'Componente Principal 2')
        legend1 = ax.legend(*scatter.legend_elements(), title="Clusters")
        ax.add_artist(legend1)

        plot_buf = io.BytesIO()
        fig.savefig(plot_buf, format='png')
        plt.close(fig)
        add_plot("kmeans_clustering", plot_buf)
        # --- Fin de la sección del informe ---

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

        # --- Guardar gráfico para el informe ---
        plot_buf = io.BytesIO()
        fig.savefig(plot_buf, format='png')
        add_plot("correlation_heatmap", plot_buf)
        # --- Fin de la sección del informe ---

        # Preparar imagen para la UI
        plot_buf.seek(0)
        image_base64 = base64.b64encode(plot_buf.read()).decode('utf-8')
        plt.close(fig)

        return { "image_base64": image_base64, "description": "Aquí está el mapa de calor de correlación." }
    except Exception as e:
        return {"error": f"Error al generar el mapa de calor: {e}"}

# (Las demás funciones se modificarían de forma similar para guardar sus gráficos)
def run_linear_regression_tool(data: List[Dict[str, Any]], target: str, feature: str) -> Dict[str, Any]:
    try:
        df = pd.DataFrame(data)
        if df.empty: return {"error": "Los datos están vacíos."}
        # ... (resto de la lógica se mantiene igual)
        X = df[[feature]].values
        y = df[target].values
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        # --- Generar y guardar gráfico para el informe ---
        fig, ax = plt.subplots()
        ax.scatter(X_test, y_test, color='red', label='Datos Reales')
        ax.plot(X_test, y_pred, color='blue', linewidth=3, label='Línea de Regresión')
        ax.set_title('Regresión Lineal')
        ax.set_xlabel(feature)
        ax.set_ylabel(target)
        ax.legend()

        plot_buf = io.BytesIO()
        fig.savefig(plot_buf, format='png')
        plt.close(fig)
        add_plot("linear_regression", plot_buf)
        # --- Fin de la sección del informe ---

        line_x = [df[feature].min(), df[feature].max()]
        line_y = model.predict([[line_x[0]], [line_x[1]]]).tolist()
        return { "rSquared": r2, "mse": mse, "targetVariable": target, "featureVariables": [feature], "line_points": {"x": line_x, "y": line_y} }
    except Exception as e:
        return {"error": f"Error en la regresión lineal: {e}"}
 
def run_naive_bayes_tool(data: List[Dict[str, Any]], target: str, features: List[str]) -> Dict[str, Any]:
    try:
        df = pd.DataFrame(data)
        if df.empty: return {"error": "Los datos están vacíos."}
        # ... (resto de la lógica se mantiene igual)
        le = LabelEncoder()
        df[target] = le.fit_transform(df[target])
        X = df[features].values
        y = df[target].values
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        model = GaussianNB()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, target_names=le.classes_.tolist(), output_dict=True)

        return {
            "accuracy": accuracy,
            "classification_report": report,
            "targetVariable": target,
            "featureVariables": features,
            "algorithm": "Naive Bayes"
        }
    except Exception as e:
        return {"error": f"Error en el análisis de Naive Bayes: {e}"}
