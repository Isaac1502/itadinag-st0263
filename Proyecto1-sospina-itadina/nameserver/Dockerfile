# Utiliza una imagen base de Python
FROM python:3.11.7-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos necesarios al contenedor
COPY nameserver.py /app/
COPY dfs_struct_map.json /app/
COPY nameserver.conf /app/
COPY ss_blocks_map.json /app/

# Instala las dependencias necesarias
RUN pip install rpyc

# Expone el puerto que el nameserver utilizará
EXPOSE 18860

# Comando para ejecutar el nameserver
CMD ["python", "nameserver.py"]
