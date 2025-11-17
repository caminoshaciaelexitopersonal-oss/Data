# Usa una imagen oficial de Python como imagen base
FROM python:3.12-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Añade el directorio de la aplicación a PYTHONPATH
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Copia el archivo de requerimientos al directorio de trabajo
COPY ./requirements.txt .

# Instala los requerimientos
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación al directorio de trabajo
COPY . .

# Expone el puerto 8000 para que FastAPI sea accesible
EXPOSE 8000

# Comando para correr la aplicación. Uvicorn es un servidor ASGI.
# El host 0.0.0.0 hace que el servidor sea accesible desde fuera del contenedor.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
