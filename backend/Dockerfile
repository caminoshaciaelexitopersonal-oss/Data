# Usa una imagen oficial de Python como imagen base
FROM python:3.12-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Añade el directorio de la aplicación a PYTHONPATH
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Copia el archivo de requerimientos al directorio de trabajo
COPY ./requirements.txt .

# Instala los requerimientos
RUN pip install setuptools
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación a un subdirectorio 'backend'
COPY . ./backend

# Expone el puerto 8000 para que FastAPI sea accesible
EXPOSE 8000

# Comando para correr la aplicación directamente a través del intérprete de Python,
# que ejecutará el bloque 'if __name__ == "__main__"' en main.py.
CMD ["python", "-m", "backend.main"]
