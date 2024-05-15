
# Proyecto 2 - Cluster Kubernetes

Para el segundo proyecto de la maateria 'Tópicos Especiales de Telemática' se propne un clúster de alta disponibilidad en Kubernetes, utilizando la distribución microk8s y configurando un entorno de Infraestructura como Servicio (IaaS) en Google Cloud Platform. La aplicación a desplegar es un sistema de gestión de contenidos Wordpress.

## Objetivos

- Desplegar un clúster de Kubernetes utilizando la distribución microk8s en al menos tres máquinas virtuales en Google Cloud Platform.
- Configurar el clúster para garantizar alta disponibilidad en la capa de aplicación, base de datos y almacenamiento.
- Implementar un balanceador de cargas para distribuir el tráfico entre los nodos del clúster.
- Desplegar una base de datos de alta disponibilidad en Kubernetes.
- Configurar un servidor NFS en el clúster para el almacenamiento de archivos compartidos.



## Desripción Arquitectural

Para la implementación del sistema de gestión de contenidos en una infraestructura tipo clúster, se utilizaron cuatro máquinas virtuales de GCP, con la siguiente descripción:

- **Machine Type:** e2-medium
- **CPU Platform:** Intel Broadwell
- **Architecture:** x86/64

![App Screenshot](https://i.ibb.co/sQp5MbJ/Image-15-05-24-at-12-09-PM.jpg)

Se utilizó una microk8s como servicio base para crear el cluster de kubernetes con las máquinas virtuales, la distribución de las VM es la siguiente:

### microk8s-master
Máquina virtual master o principal del clúster. Es la máquina que permite la conexión al cluster de otras máquinas (workers), además es de ser la que expone el punto de entrada a los pods de servicio (Ingress).

### microk8s-worker-*
Para efectos prácticos se utilizaron 2 máquinas virtuales a modo de workers en el cluster, las cuales alojan pods de servicio tanto de wordpress como de mysql.

### microk8s-nfs
Es la máquina virtual dedicada al servicio de almacenamiento de archivos, se utiliza nfs-kernel-server y expone un directorio para almacenar pvc el cual puede ser usado por otros nodos de la subnet.


## Manifiestos utilizados

### General purpose

#### sc-nfs.yaml

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-csi
provisioner: nfs.csi.k8s.io
parameters:
  server: 10.128.0.16
  share: /srv/nfs
reclaimPolicy: Delete
volumeBindingMode: Immediate
mountOptions:
  - hard
  - nfsvers=4.1
```
Este archivo YAML define una clase de almacenamiento (StorageClass) llamada nfs-csi que utiliza el controlador CSI de NFS para provisionar volúmenes en Kubernetes. En dicho archivo se define además el servidor NFS y el directorio raíz que está expuesto para el servicio de almacenamiento.

#### kustomization.yaml

```yaml
secretGenerator:
  - name: mysql-pass
    literals:
      - password=password

resources:
  - mysql-pvc.yaml
  - mysql-deployment.yaml
  - mysql-service.yaml
  - wordpress-pvc.yaml
  - wordpress-deployment.yaml
  - wordpress-service.yaml
  - wordpress-ingress.yaml
```

Este archivo YAML define el conjunto de recursos que se utilizarán para desplegar el clúster, incluidos secretos y servicios para la aplicación que incluye bases de datos MySQL y WordPress. Aquí está la descripción:

**secretGenerator:** Esta sección define la generación de secretos. En este caso, se define un secreto llamado mysql-pass que contiene una sola clave llamada password. Este secreto se utilizará para autenticar con la base de datos MySQL.

**resources:** Esta sección lista los recursos que se utilizarán para el despliegue del clúster. Cada recurso está definido en un archivo YAML separado y se incluye mediante su ruta relativa. Los recursos incluidos son:

- *mysql-pvc.yaml:* Define un volumen persistente para la base de datos MySQL.
- *mysql-deployment.yaml:* Define un deployment para la base de datos MySQL.
- *mysql-service.yaml:* Define un servicio para la base de datos MySQL.
- *wordpress-pvc.yaml:* Define un volumen persistente para la aplicación WordPress.
- *wordpress-deployment.yaml:* Define un deployment para la aplicación WordPress.
- *wordpress-service.yaml:* Define un servicio para la aplicación WordPress.
- *wordpress-ingress.yaml:* Define un ingress para la aplicación WordPress.

### MySQL 

#### mysql-pvc.yaml

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pv-claim
  labels:
    app: wordpress
spec:
  storageClassName: nfs-csi
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
```

Este archivo YAML define un PersistentVolumeClaim (PVC) en Kubernetes. El PVC se llama "mysql-pv-claim" y está etiquetado como parte de la aplicación "wordpress". Solicita un volumen de almacenamiento persistente de 20 gigabytes (20Gi) con acceso de lectura y escritura para un solo nodo, utilizando la clase de almacenamiento "nfs-csi".

#### mysql-deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wordpress-mysql
  labels:
    app: wordpress
spec:
  selector:
    matchLabels:
      app: wordpress
      tier: mysql
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: wordpress
        tier: mysql
    spec:
      containers:
        - image: mysql:8.0
          name: mysql
          env:
            - name: MYSQL_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mysql-pass
                  key: password
            - name: MYSQL_DATABASE
              value: wordpress
            - name: MYSQL_USER
              value: wordpress
            - name: MYSQL_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mysql-pass
                  key: password
          ports:
            - containerPort: 3306
              name: mysql
          volumeMounts:
            - name: mysql-persistent-storage
              mountPath: /var/lib/mysql
      volumes:
        - name: mysql-persistent-storage
          persistentVolumeClaim:
            claimName: mysql-pv-claim
```

Este archivo YAML define el Deployment en Kubernetes para la base de datos MySQL de WordPress. El Deployment se encarga de gestionar los pods que ejecutan MySQL. Los pods se crearán a partir de la plantilla proporcionada, utilizando la imagen "mysql:8.0". Se definen variables de entorno para la configuración de MySQL, y se monta un volumen persistente para almacenar los datos de la base de datos.

#### mysql-service.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: wordpress-mysql
  labels:
    app: wordpress
spec:
  ports:
    - port: 3306
  selector:
    app: wordpress
    tier: mysql
  clusterIP: None

```

Este archivo YAML describe un servicio en Kubernetes para la base de datos MySQL de WordPress. Este servicio permite la exposición de la base de datos MySQL dentro del clúster de Kubernetes para que otros servicios puedan comunicarse con ella. Está etiquetado como parte de la aplicación "wordpress" y selecciona los pods con las etiquetas "app: wordpress" y "tier: mysql" para exponerlos. El puerto 3306, que es el puerto por defecto de MySQL, está expuesto por este servicio. Sin embargo, no se le asigna una dirección IP interna en el clúster, lo que significa que solo será accesible desde otros servicios dentro del mismo.

### Wordpress

#### wordpress-pvc.yaml

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: wp-pv-claim
  labels:
    app: wordpress
spec:
  storageClassName: nfs-csi
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
```

Idéntico al pvc definido para el servicio de MySQL. Hace parte de la aplicación "wordpress", el PVC se llama "wp-pv-claim".

#### wordpress-deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wordpress
  labels:
    app: wordpress
spec:
  replicas: 5
  selector:
    matchLabels:
      app: wordpress
      tier: frontend
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: wordpress
        tier: frontend
    spec:
      containers:
        - image: wordpress:6.5.3
          name: wordpress
          env:
            - name: WORDPRESS_DB_HOST
              value: wordpress-mysql
            - name: WORDPRESS_DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mysql-pass
                  key: password
            - name: WORDPRESS_DB_USER
              value: wordpress
          ports:
            - containerPort: 80
              name: wordpress
          volumeMounts:
            - name: wordpress-persistent-storage
              mountPath: /var/www/html
      volumes:
        - name: wordpress-persistent-storage
          persistentVolumeClaim:
            claimName: wp-pv-claim

```


Este archivo YAML describe el deployment en Kubernetes para WordPress. Este deployment despliega los pods que ejecutan la aplicación WordPress. Está etiquetado como parte de la aplicación "wordpress" y selecciona los pods con las etiquetas "app: wordpress" y "tier: frontend". Utiliza una estrategia de tipo Recreate para manejar los cambios en los pods.

Los contenedores dentro de este deployment utilizan la imagen "wordpress:6.5.3", se especifica una cantidad inicial de cinco replicas. También establecen variables de entorno para configurar la base de datos de WordPress, como el host de la base de datos y las credenciales de acceso. El puerto 80 está expuesto para la aplicación WordPress.

Además, este deployment monta un volumen persistente llamado "wordpress-persistent-storage" en el directorio "/var/www/html" dentro de los contenedores. Este volumen persistente se asocia con el PersistentVolumeClaim llamado "wp-pv-claim", que proporciona almacenamiento persistente para los archivos de la aplicación WordPress.

#### wordpress-service.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: wordpress
  labels:
    app: wordpress
spec:
  ports:
    - port: 80
  selector:
    app: wordpress
    tier: frontend

```

Este archivo YAML describe el servicio en Kubernetes para la aplicación WordPress. El servicio se llama "wordpress" y está etiquetado como parte de la aplicación "wordpress". Establece un puerto de escucha en el puerto 80.

El selector del servicio indica que este servicio redirigirá el tráfico hacia los pods que tienen las etiquetas "app: wordpress" y "tier: frontend". Esto significa que cualquier solicitud dirigida a este servicio será dirigida a los pods que pertenecen a la parte frontal de la aplicación WordPress.

#### wordpress-ingress.yaml

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: wordpress-ingress
spec:
  rules:
    - http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: wordpress
                port:
                  number: 80

```

Este archivo YAML describe el recurso de Ingress en Kubernetes para enrutar el tráfico HTTP hacia el servicio de WordPress. El Ingress se denomina "wordpress-ingress".

Las reglas del Ingress especifican que cualquier solicitud HTTP enviada al prefijo "/" será dirigida al servicio llamado "wordpress" en el puerto 80. Esto significa que cuando se accede al dominio asociado al Ingress, se redirigirá al servicio de WordPress para manejar la solicitud.


## Evidencias

![App Screenshot](https://i.ibb.co/dLGk0dv/Image-15-05-24-at-1-59-PM.jpg)

Aplicación corriendo cuando se ubica la IP publica del master, la cual mapea el ingress de la aplicación (root) para que el cliente sea dirigido a los pods de la capa de servicio wordpress.

![App Screenshot](https://i.ibb.co/cFjGLsG/Image-15-05-24-at-2-00-PM.jpg)

Todos los servicios, despliegues y contenedores activos para dar soporte al administrador de contenidos.


![App Screenshot](https://i.ibb.co/mCNPxRL/Image-15-05-24-at-2-03-PM.jpg)

Como se puede ver en la imagen de la session en la máquina virtual que soporta el servicio de NFS, hay varios pvc creados, uno de ellos correspondiente al servicio de wordpress y el otro para MySQL. Ingresando al pvc de wordpress es posible ver que los assests almacenados.
## Authors

- [Santiago Ospina Idrobo](https://github.com/Santiagospinai7)
- [Isaac Tadina Giraldo](https://github.com/Isaac1502)

