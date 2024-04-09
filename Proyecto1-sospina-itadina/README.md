# Sistema de Archivos Distribuido en AWS

Este sistema de archivos distribuido está diseñado para funcionar en el entorno de AWS, permitiendo a los usuarios gestionar archivos en un entorno distribuido. A continuación, se detallan los pasos para acceder y utilizar el sistema.

## Pre-requisitos

- Tener acceso a una instancia de AWS con la imagen de Docker ya configurada y lista para usar.
- Poseer el archivo `.pem` necesario para acceder a la instancia mediante SSH.

## Conexión a la Instancia de AWS

1. Abre la terminal o línea de comandos.
2. Navega hasta el directorio donde tienes almacenado tu archivo `.pem`.
3. Ejecuta el siguiente comando para iniciar sesión en tu instancia de AWS:

    ```bash
    ssh -i st063.pem ubuntu@52.1.104.77
    ```

    Asegúrate de reemplazar `st063.pem` con el nombre de tu archivo `.pem` y `52.1.104.77` con la dirección IP pública de tu instancia de AWS.

## Ejecución del Cliente del Sistema de Archivos

Una vez dentro de la instancia de AWS, sigue estos pasos para iniciar el cliente del sistema de archivos distribuido:

1. Ejecuta el siguiente comando para iniciar la imagen de Docker que contiene el cliente:

    ```bash
    sudo docker run -it -p 18864:18864 sospinai7/st0263-dfs:client.1.0.0
    ```

2. Cuando se inicie el cliente, selecciona la opción `1` para conectar con la configuración de AWS.

## Uso del Sistema de Archivos

Después de conectarte, estarás en la interfaz de línea de comandos del sistema de archivos distribuido. Aquí puedes ejecutar varios comandos para interactuar con el sistema, tales como:

- `ls`: para listar directorios y archivos.
- `cd [directorio]`: para cambiar de directorio.
- `mkdir [nombre_del_directorio]`: para crear un nuevo directorio.
- `upload [ruta_local] [ruta_destino]`: para subir un archivo al sistema.
- `download [ruta_remota] [ruta_local]`: para descargar un archivo del sistema a tu máquina local.

## Cierre de Sesión

Para salir de la sesión interactiva y cerrar el cliente, puedes escribir:

```bash
quit
