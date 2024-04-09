FROM python:3.11.7-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el script del servidor de almacenamiento al directorio de trabajo
COPY storageserver.py /app/

# Instalar sudo, actualizar pip e instalar rpyc
RUN apt-get update && \
    apt-get install -y sudo && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir rpyc

# Expone el puerto por defecto del servidor de almacenamiento y el puerto adicional
EXPOSE 18861 18862

# Comando para ejecutar el servidor de almacenamiento cuando se inicie el contenedor
CMD ["python", "storageserver.py"]
