# StorageServer

## Descripción General

`StorageServer` es un componente clave de nuestro sistema de archivos distribuido, diseñado para facilitar la gestión eficiente de archivos y directorios a través de una red de servidores. Este servidor utiliza RPyC (Remote Python Call) para permitir operaciones remotas de archivo, proporcionando una interfaz sencilla para el almacenamiento y recuperación de datos. Es la entidad encargada de interactuar de forma directa con las operaciones de gestión de archivos del sistema operativo.

## Funcionalidades

- **Almacenamiento de Bloques de Datos**: Almacena datos en forma de bloques en el servidor, utilizando identificadores únicos para cada bloque para evitar conflictos.
- **Recuperación de Datos**: Recupera bloques de datos previamente almacenados en el servidor.
- **Transferencia de Bloques**: Soporta la transferencia de datos entre diferentes servidores dentro del sistema distribuido.
- **Gestión de Estructura de Directorios**: Sincroniza y modifica la estructura de directorios del servidor de acuerdo con un esquema definido externamente.

## Requisitos

- Python 3.x
- RPyC

## Instalación

Clona el repositorio y instala las dependencias necesarias:

```bash
pip install -r requirements.py
```

## Uso

### Iniciar el Servidor

Ejecuta el siguiente comando para iniciar el servidor, especificando un puerto si es necesario (el predeterminado es 18861):

```bash
python3 storageserver.py [puerto]
```

### Métodos Disponibles

- `put(block_path, data)`: Guarda los datos en la ruta de bloque especificada.
- `get(block_path)`: Obtiene los datos de la ruta de bloque especificada.
- `send_my_block(origin_block_path, destination, destination_block_path)`: Envía un bloque de datos desde este servidor a otro servidor especificado.
- `adapt_this_directory_structure(struct)`: Ajusta la estructura de directorios del servidor para coincidir con una estructura definida en JSON.

## Ejemplos de Uso

```python
import rpyc
conn = rpyc.connect('localhost', 18861)
conn.root.put("/path/to/block", b"data to store")
data = conn.root.get("/path/to/block")
```
