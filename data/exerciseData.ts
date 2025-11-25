export const exerciseNotebook = {
  "células": [
    {
      "tipo_celda": "markdown",
      "fuente": [
        "# El Proceso Completo del Análisis de Datos\n",
        "El análisis de datos moderno se basa en la capacidad de convertir información cruda en conocimiento útil. Para lograrlo, se emplea un proceso estructurado que comienza con la extracción, transformación y carga (ETL) de los datos, seguido de su limpieza y normalización, y culmina con la aplicación de modelos de Machine Learning que permiten clasificar, agrupar o predecir comportamientos.\n\n",
        "El objetivo es obtener datos reales, confiables y estructurados que puedan alimentar herramientas como Power BI, Tableau o sistemas inteligentes desarrollados en Python."
      ]
    },
    {
      "tipo_celda": "markdown",
      "fuente": [
        "## Proceso ETL (Extracción, Transformación y Carga)\n",
        "La extracción es el primer paso del proceso ETL (Extract, Transform, Load) y consiste en obtener datos desde múltiples fuentes —estructuradas o no estructuradas— para centralizarlos en un único entorno de análisis.\n\n",
        "En esta fase, el objetivo es recolectar toda la información relevante sin alterar su contenido original, garantizando la integridad de los datos."
      ]
    },
    {
      "tipo_celda": "markdown",
      "fuente": [
        "### 🧩 Fuentes más comunes de extracción\n",
        "**Archivos CSV y de texto plano:**\n",
        "Son los formatos más ligeros y ampliamente utilizados para el intercambio de datos tabulares."
      ]
    },
    {
      "tipo_celda": "código",
      "fuente": [
        "import pandas as pd\n",
        "datos_csv = pd.read_csv(\"datos.csv\", encoding=\"utf-8\")"
      ]
    },
    {
      "tipo_celda": "markdown",
      "fuente": [
        "Estos archivos sirven luego como base estandarizada para integrar datos de otras fuentes.\n\n",
        "**Archivos Excel (una o varias hojas):**\n",
        "Es común que una organización maneje múltiples hojas con información distinta (por ejemplo: ventas, clientes, inventario).\n",
        "Cada hoja puede extraerse de manera independiente o consolidarse en un solo DataFrame:"
      ]
    },
    {
      "tipo_celda": "código",
      "fuente": [
        "archivo_excel = pd.ExcelFile(\"datos_empresariales.xlsx\")\n",
        "hoja1 = pd.read_excel(archivo_excel, \"Ventas\")\n",
        "hoja2 = pd.read_excel(archivo_excel, \"Clientes\")\n",
        "hoja3 = pd.read_excel(archivo_excel, \"Inventario\")\n",
        "\n",
        "# Combinar todas las hojas\n",
        "datos_excel = pd.concat([hoja1, hoja2, hoja3], ignore_index=True)"
      ]
    },
    {
      "tipo_celda": "markdown",
      "fuente": [
        "Esta práctica permite unificar la información dispersa antes de continuar con la transformación.\n\n",
        "**Archivos JSON (estructurados en jerarquías):**\n",
        "Comunes en servicios web y APIs. Se convierten fácilmente en estructuras tabulares:"
      ]
    },
    {
      "tipo_celda": "código",
      "fuente": [
        "datos_json = pd.read_json(\"api_response.json\")"
      ]
    },
    {
        "tipo_celda": "markdown",
        "fuente": [
            "**Bases de datos SQL y MySQL (y sus derivados como PostgreSQL, MariaDB, SQLite, etc.):**\n",
            "Permiten acceder a información almacenada de manera relacional.\n",
            "Python, mediante `sqlalchemy` o `mysql.connector`, puede conectarse directamente y ejecutar consultas SQL:"
        ]
    },
    {
        "tipo_celda": "código",
        "fuente": [
            "import mysql.connector\n",
            "import pandas as pd\n\n",
            "conexion = mysql.connector.connect(\n",
            "    host=\"localhost\",\n",
            "    user=\"usuario\",\n",
            "    password=\"contraseña\",\n",
            "    database=\"nombre_bd\"\n",
            ")\n\n",
            "query = \"SELECT * FROM ventas;\"\n",
            "datos_sql = pd.read_sql(query, conexion)\n",
            "conexion.close()"
        ]
    },
    {
        "tipo_celda": "markdown",
        "fuente": [
            "Esta conexión se adapta fácilmente a otros sistemas como PostgreSQL, SQL Server o SQLite modificando el conector y la cadena de conexión.\n\n",
            "**APIs (interfaces de servicios externos):**\n",
            "Se utilizan para extraer datos dinámicos o actualizados en tiempo real (por ejemplo, precios, clima, redes sociales).\n",
            "Con la librería `requests`:"
        ]
    },
    {
        "tipo_celda": "código",
        "fuente": [
            "import requests\n\n",
            "respuesta = requests.get(\"https://api.ejemplo.com/datos\")\n",
            "datos_api = pd.json_normalize(respuesta.json())"
        ]
    },
    {
        "tipo_celda": "markdown",
        "fuente": [
            "### Conversión y consolidación\n",
            "Una vez extraídos los datos desde Excel, SQL, APIs o JSON, es buena práctica convertirlos a un formato unificado (CSV) antes de continuar con la fase de transformación.\n",
            "Esto garantiza compatibilidad con herramientas de análisis (Power BI, Tableau, etc.) y facilita la trazabilidad del proceso ETL."
        ]
    },
    {
        "tipo_celda": "código",
        "fuente": [
            "# Guardar los datos consolidados en un CSV limpio\n",
            "datos_consolidados = pd.concat([datos_csv, datos_excel, datos_sql, datos_api], ignore_index=True)\n",
            "datos_consolidados.to_csv(\"datos_unificados.csv\", index=False, encoding=\"utf-8\")"
        ]
    },
    {
        "tipo_celda": "markdown",
        "fuente": [
            "Con esto, el analista dispone de un solo archivo `datos_unificados.csv` listo para iniciar la transformación y limpieza, asegurando que toda la información (de hojas Excel, bases SQL y APIs) esté integrada en un formato estándar."
        ]
    },
    {
        "tipo_celda": "markdown",
        "fuente": [
            "## 3. Limpieza y transformación de datos\n",
            "Esta etapa busca asegurar la calidad y consistencia. Las tareas principales incluyen:\n\n",
            "| Tarea | Objetivo | Ejemplo |\n",
            "|---|---|---|\n",
            "| Eliminación de nulos | Evitar errores en modelos | `df.dropna()` |\n",
            "| Detección de outliers | Evitar distorsión estadística | Boxplot, z-score |\n",
            "| Codificación categórica| Transformar texto en números | `pd.get_dummies(df)` |\n",
            "| Estandarización de formato | Uniformar valores | Convertir a mayúsculas, fechas uniformes |"
        ]
    },
    {
        "tipo_celda": "markdown",
        "fuente": [
            "## 🔹 4. Normalización, afinación y aceleración\n",
            "### 4.1. Normalización\n",
            "Normalizar es ajustar los valores numéricos a una misma escala, lo cual mejora la precisión de los modelos.\n\n",
            "**Min-Max Scaling:** lleva los datos entre 0 y 1.\n",
            "`X' = (X - X_min) / (X_max - X_min)`\n\n",
            "**Z-score (estandarización):**\n",
            "`X' = (X - μ) / σ`\n",
            "donde `μ` es la media y `σ` la desviación estándar."
        ]
    },
    {
        "tipo_celda": "código",
        "fuente": [
            "from sklearn.preprocessing import StandardScaler\n",
            "scaler = StandardScaler()\n",
            "df_scaled = scaler.fit_transform(df[['edad', 'ingresos']])"
        ]
    },
    {
      "tipo_celda": "markdown",
      "fuente": [
        "### 4.2. Afinación\n",
        "La afinación consiste en optimizar los parámetros del modelo para obtener mejor rendimiento. En Machine Learning, esto se logra con técnicas como:\n",
        "- GridSearchCV (búsqueda exhaustiva)\n",
        "- RandomSearchCV (búsqueda aleatoria)\n",
        "- Cross Validation\n"
      ]
    },
    {
      "tipo_celda": "código",
      "fuente": [
        "from sklearn.model_selection import GridSearchCV\n",
        "\n",
        "// Sirve para ajustar variables como número de clusters (en K-Means) o parámetros de suavizado (en Naive Bayes)."
      ]
    },
    {
      "tipo_celda": "markdown",
      "fuente": [
        "### 4.3. Aceleración\n",
        "Busca reducir tiempos de procesamiento mediante:\n",
        "- Procesamiento paralelo (joblib, dask, pyspark).\n",
        "- Reducción de dimensionalidad (PCA).\n",
        "- Filtrado de datos irrelevantes antes del modelado."
      ]
    },
    {
      "tipo_celda": "markdown",
      "fuente": [
        "## 🔹 5. Machine Learning\n",
        "El aprendizaje automático permite que los sistemas aprendan patrones de los datos. Se divide en tres grandes tipos:\n\n",
        "| Tipo | Característica | Ejemplo |\n",
        "|---|---|---|\n",
        "| Supervisado | Usa datos etiquetados (con respuesta) | Clasificación, regresión |\n",
        "| No supervisado | Agrupa sin etiquetas previas | Clustering, K-Means |\n",
        "| Por refuerzo | Aprende por prueba y error | Robots, videojuegos, trading |"
      ]
    },
    {
      "tipo_celda": "markdown",
      "fuente": [
        "## 🔹 6. Algoritmo Naive Bayes\n",
        "### 6.1. Concepto\n",
        "Basado en el Teorema de Bayes, este método calcula la probabilidad de que una observación pertenezca a una clase, asumiendo independencia entre variables.\n",
        "`P(A|B) = (P(B|A) * P(A)) / P(B)`\n\n",
        "En clasificación:\n",
        "`P(Clase|Datos) = (P(Datos|Clase) * P(Clase)) / P(Datos)`"
      ]
    },
    {
      "tipo_celda": "markdown",
      "fuente": [
        "### 6.2. Ejemplo práctico — Clasificación de correos “Spam” o “No Spam”\n",
        "Tenemos 5 correos:\n",
        "- 3 Spam → `P(Spam) = 0.6`\n",
        "- 2 No Spam → `P(NoSpam) = 0.4`\n\n",
        "**Probabilidades condicionales:**\n\n",
        "| Palabra | P(x|Spam) | P(x|NoSpam) |\n",
        "|---|---|---|\n",
        "| Gratis | 0.67 | 0 |\n",
        "| Oferta | 0.67 | 0.5 |\n",
        "| Urgente | 0.67 | 0.5 |\n\n",
        "**Cálculo:**\n",
        "`P(Spam|Gratis,Oferta,Urgente) = 0.6 * 0.67 * 0.67 * 0.67 = 0.179`\n",
        "`P(NoSpam|Gratis,Oferta,Urgente) = 0.4 * 0 * 0.5 * 0.5 = 0`\n\n",
        "✅ **Conclusión:** El correo se clasifica como Spam."
      ]
    },
    {
      "tipo_celda": "markdown",
      "fuente": [
        "### 6.3. Implementación básica en Python"
      ]
    },
    {
      "tipo_celda": "código",
      "fuente": [
        "from sklearn.naive_bayes import MultinomialNB\n",
        "from sklearn.feature_extraction.text import CountVectorizer\n\n",
        "textos = [\"Oferta urgente gratis\", \"Reunión de trabajo\", \"Promoción oferta gratis urgente\"]\n",
        "y = [1, 0, 1]  # 1 = Spam, 0 = NoSpam\n\n",
        "vectorizador = CountVectorizer()\n",
        "X = vectorizador.fit_transform(textos)\n\n",
        "modelo = MultinomialNB()\n",
        "modelo.fit(X, y)\n\n",
        "nuevo = vectorizador.transform([\"Oferta gratis\"])\n",
        "print(modelo.predict(nuevo))  # Resultado: Spam (1)"
      ]
    },
    {
      "tipo_celda": "markdown",
      "fuente": [
        "## 🔹 7. Algoritmo K-Means (Agrupamiento)\n",
        "### 7.1. Concepto\n",
        "K-Means es un método no supervisado que agrupa datos similares en K grupos (clusters). Su objetivo es minimizar la distancia entre los puntos y el centroide de su grupo.\n\n",
        "`J = Σ (de i=1 a K) Σ (para xj en Ci) ||xj - μi||²`"
      ]
    },
    {
      "tipo_celda": "markdown",
      "fuente": [
        "### 7.2. Proceso\n",
        "1. Elegir **K** (número de clusters).\n",
        "2. Inicializar centroides aleatorios.\n",
        "3. Asignar cada punto al cluster más cercano (según distancia euclidiana).\n",
        "4. Recalcular centroides.\n",
        "5. Repetir hasta converger."
      ]
    },
    {
      "tipo_celda": "markdown",
      "fuente": [
        "### 7.3. Ejemplo en Python"
      ]
    },
    {
      "tipo_celda": "código",
      "fuente": [
        "from sklearn.cluster import KMeans\n",
        "import matplotlib.pyplot as plt\n\n",
        "X = [[1,2],[1,4],[1,0],[10,2],[10,4],[10,0]]\n",
        "kmeans = KMeans(n_clusters=2, random_state=0).fit(X)\n\n",
        "plt.scatter([x[0] for x in X], [x[1] for x in X], c=kmeans.labels_)\n",
        "plt.scatter(kmeans.cluster_centers_[:,0], kmeans.cluster_centers_[:,1], color='red', marker='X')\n",
        "plt.show()"
      ]
    },
    {
      "tipo_celda": "markdown",
      "fuente": [
        "Este algoritmo agrupa datos similares (por ejemplo, clientes con comportamientos parecidos)."
      ]
    },
    {
      "tipo_celda": "markdown",
      "fuente": [
        "## 🔹 8. Diferencias entre Naive Bayes y K-Means\n\n",
        "| Aspecto | Naive Bayes | K-Means |\n",
        "|---|---|---|\n",
        "| Tipo | Supervisado | No supervisado |\n",
        "| Objetivo | Clasificar | Agrupar |\n",
        "| Entrada | Datos con etiquetas | Datos sin etiquetas |\n",
        "| Fundamento | Probabilidad (Teorema de Bayes) | Distancias (Euclidianas) |\n",
        "| Resultado | Probabilidad de clase | Clusters definidos |\n",
        "| Uso común | Detección de spam, análisis de texto | Segmentación de clientes, patrones |\n\n",
        "Ambos son complementarios: Bayes predice clases, mientras K-Means descubre patrones ocultos."
      ]
    },
    {
      "tipo_celda": "markdown",
      "fuente": [
        "## Interpretabilidad y sesgos\n",
        "Un punto crucial del análisis de datos es entender cómo el modelo toma decisiones y qué sesgos pueden existir. Por ejemplo:\n\n",
        "- En **Naive Bayes**, una palabra con probabilidad cero puede eliminar completamente una clase (por eso se usa suavizado de Laplace).\n",
        "- En **K-Means**, la elección del número de clusters puede cambiar totalmente los resultados.\n\n",
        "Por ello, se recomienda:\n",
        "- Validar con métricas objetivas.\n",
        "- Aplicar visualización de resultados.\n",
        "- Evaluar impactos éticos o de sesgo en datos sensibles."
      ]
    },
    {
      "tipo_celda": "markdown",
      "fuente": [
        "## 🔹 11. Conclusión general\n",
        "El proceso completo —desde la extracción y limpieza de datos (ETL) hasta la aplicación de modelos de Machine Learning (Naive Bayes y K-Means)— constituye la base de la analítica moderna orientada a la toma de decisiones.\n\n",
        "Cada etapa cumple un papel específico:\n",
        "- **ETL:** Garantiza que los datos sean válidos y coherentes.\n",
        "- **Normalización:** Mejora la precisión de los modelos.\n",
        "- **Naive Bayes:** Clasifica según evidencia probabilística.\n",
        "- **K-Means:** Descubre patrones ocultos sin etiquetas.\n\n",
        "Ambos algoritmos, junto con una correcta preparación y afinación de datos, permiten crear sistemas inteligentes capaces de analizar información real, detectar comportamientos y generar visualizaciones de alto valor estratégico."
      ]
    }
  ],
  "metadatos": {
    "colaboración": {
      "procedencia": []
    }
  },
  "nbformat": 4,
  "nbformat_minor": 5
}
