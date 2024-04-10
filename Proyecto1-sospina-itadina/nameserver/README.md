# NameServer o NameNode

## Descripción General

`NameServer` parte fundamental del sistema de archivos distribuido (DFS). Es responsable de gestionar la estructura de directorios y archivos del DFS, así como de coordinar las operaciones de almacenamiento y recuperación de datos entre los nodos de datos (DataNodes) y las peticiones de los clientes. Este servicio expone una interfaz para interactuar con el DFS a través de llamadas remotas y proporciona funciones para la inicialización del sistema, navegación en el árbol de directorios, creación y eliminación de archivos y directorios, entre otras.

## Funcionalidades

- **Gestión de Estructura de Directorios**: El NameNode gestiona la estructura de directorios del DFS, permitiendo la creación, eliminación y navegación en la jerarquía de directorios.
- **Asignación de Bloques de Datos**: Asigna y administra los bloques de datos almacenados en los DataNodes, manteniendo un mapeo de qué bloques residen en qué nodos.
- **Mantenimiento de la Salud del Sistema**: Supervisa la disponibilidad y el estado de los nodos de datos, marcando los nodos como "vivos" o "muertos" según su accesibilidad.
- **Sincronización de Estructura entre Nodos**: Se encarga de sincronizar la estructura de directorios entre los nodos de datos activos para garantizar la coherencia del sistema.

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

Estando en el directorio `/nameserver` ejecuta el siguiente comando para inciar el NameNode:

```bash
python3 nameserver.py
```

### Acciones Principales

- `refresh()`: Actualiza la configuración y archivos de estructra del DFS (mapa de estructura y mapa de bloques)
- `initialize(forced)`: Inicializa el sistema de archivos, creando la estructura de directorios por defecto y marcando todos los nodos de datos como "vivos".
- `get(path)`: Obtiene información sobre el recurso en la ruta especificada.
- `mkdir(path)`: Crea un nuevo directorio en la ubicación especificada.
- `new_file(struct_path, ss_block_map)`: Crea un nuevo archivo en la ubicación especificada y asigna los bloques de datos a los nodos de datos según el mapeo proporcionado.
- `delete(path, part_of_moving, force_delete)`: Elimina el recurso en la ruta especificada, ya sea un archivo o un directorio.

### Acciones Auxiliares

- `get_alive_servers(max_needed)`: Obtiene la lista de nodos de datos activos, con opción para especificar el número máximo requerido.
- `mark_new_block(block_id, dn)`: Marca un nuevo bloque de datos en un nodo de datos específico.
- `get_dn_having_this_block(block_id, max_needed, to_exclude)`: Retorna una lista de DataNodes que contienen un bloque específico.
- `files_in_directory(dir, struct_content, max_needed)`: Lista los archivos y directorios contenidos en el directorio especificado.
- `delete_block_from_dn(block_id, dn)`: Elimina un bloque de datos de un nodo de datos específico.
