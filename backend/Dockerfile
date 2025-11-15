# Usa una imagen oficial de Python como imagen base
FROM public.ecr.aws/c7n9m6p7/devops/python:3.9-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo de requerimientos al directorio de trabajo
COPY backend/requirements.txt ./backend/

# Instala los requerimientos
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copia el resto del código de la aplicación al directorio de trabajo
COPY backend/ ./backend/

# Expone el puerto 8000 para que FastAPI sea accesible
EXPOSE 8000

# Comando para correr la aplicación. Uvicorn es un servidor ASGI.
# El host 0.0.0.0 hace que el servidor sea accesible desde fuera del contenedor.
CMD ["sh", "-c", "export PYTHONPATH=$PYTHONPATH:/app:/app/backend; uvicorn backend.main:app --host 0.0.0.0 --port 8000"]
