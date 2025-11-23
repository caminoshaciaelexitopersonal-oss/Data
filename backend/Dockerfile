# Usa una imagen oficial de Python como imagen base
FROM python:3.12-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Añade el directorio /app a PYTHONPATH para que los imports absolutos (desde 'backend') funcionen
ENV PYTHONPATH=/app

# Instala libmagic, la dependencia del sistema para python-magic
RUN apt-get update && apt-get install -y libmagic1

# Copia el archivo de requerimientos al directorio de trabajo
COPY ./requirements.txt .

# Instala los requerimientos
RUN pip install setuptools
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación a un subdirectorio 'backend'
COPY . ./backend

# Expone el puerto 8000 para que FastAPI sea accesible
EXPOSE 8000

# El directorio de trabajo permanece en /app, que es la raíz del proyecto para Python.

# Comando para correr la aplicación usando uvicorn, apuntando al módulo correcto.
# Esto asegura que todos los imports 'from backend...' funcionen correctamente.
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
