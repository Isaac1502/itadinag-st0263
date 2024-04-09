# Utiliza una imagen oficial de Python como imagen padre
FROM python:3.11.7-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el contenido del directorio actual a /app en el contenedor
COPY . /app

# Instala las dependencias
RUN pip install --no-cache-dir prompt_toolkit rpyc tqdm

# Hace que el puerto 18864 esté disponible para el mundo exterior
EXPOSE 18864

# Ejecuta client.py cuando el contenedor se lance
CMD ["python", "client.py"]
