# Client

## Descripción General

`Client` es el punto de partida en el proceso de interacción con el el sistema de archivos distribuido. Es la entidad encargada de exponer la interfaz de comunicación entre el usuario final y el DFS por medio de una aplicación CLI, las principales características que hacen parte el servicio son carga, descarga y creación de archivos. Hace uso de un protocolo de llamadas remotas conocido como RPyC (Remote Python Call) para lograr las operaciones de cara al NameNode y los DataNodes en los casos que más adelante se definen (Acciones Principales)

## Funcionalidades

- **Almacenamiento Remoto**: El cliente gestiona el flujo definido para el almacenamiento de archivos y directorios por medio de RPC, haciendo uso de los servicios expuestos por las demás entidades del sistema.
- **Recuperación de Archivos**: El cliente gestiona además el flujo definido para la recuperación de recursos, esto por medio de RPC (RPyC) punto a punto con los datanodes.
- **Navegación en el Sistema Remoto**: Soporta la navegación en la estructura remota de directorios de manera transparente para el usuario como se haría en cualquier gestor de archivos de un sistema operativo.

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

Estando en el directorio `/client` ejecuta el siguiente comando para iniciar una CLI session:

```bash
python3 client.py
```

### Acciones Principales

- `quit()`: Termina la sesión y conexión al DFS.
- `show(args)`: Muestra el estado actual del árbol de directorios, este método puedo ser llamado con acciones adicionales. Ej: `show mkdir <dir_name>`, esto mostrará el árbol de directorios después de la operación de creación de directorio.
- `init(args)`: Devuelve el DFS a su estado por default, esta operación elimina todos archivos y carpetas existentes dejando unicamente el root.
- `cd(directory)`: Encargado de la navegación entre los directorios del DFS.
- `ls(directory)`: Lista los elementos almacenados en el directorios actual del DFS, el formato de presentación de archivos y directorios es distinto.
- `mkdir(directory)`: Crea un directorio nuevo en la posición dada, la lógica de creación del directorio es transferida al name node quien se encarga de escribir la nueva carpeta en los data nodes (a nivel del sistema operativo)
- `mkfiles(files)`: Crea los archivos listados en la ejecución de la acción en el directorio actual.
- `delete(files)`: Elimina los elementos listados, la lógica de eliminación de los archivos/directorios es transferida al name node.
- `upload(args)`: Tiene como parametros el path del archivo local y el directorio objetivo remoto, método encargado de la transferencia de los bloques del archivo a los data nodes disponibles, esto siguiendo un factor de replicación específico.
- `download(args)`: Similar a la operación de upload, recibe como parámetros el path del archivo remoto alojado en el DFS y la ubicación local donde se hará la descarga. La comunicación se da de inicialmente con el name node quien retorna la lista de data nodes que contienen los bloques necesarios para la construcción del archivo, seguidamente el cliente se encarga de manejar la comunicación uno a uno con cada data node.
- `refresh(args)`: actualiza el árbol de directorios del cliente respecto al name node.

### Acciones Auxiliares

- `change_current_directory(directory)`: Encargado de actualizar la posición actual del cliente respecto a la estructura del DFS, crítico para varias operaciones como (ls, cd, upload y download).
- `print_directory(directory)`: Método usado por la acción `show()`, método recursivo que recorre la estructura del DFS (contenida en el name node como dfs_struct_map.json) para dibujar el árbol de directorios en la sesión del cliente.
