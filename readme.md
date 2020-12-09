
# Despliegue en producción de un Modelo TF2 de clasificación de imágenes.

![Portada](docs\images\08_Deployment_images_v2.png)

## Crear servidor de despliegue

En primer lugar, se va a crear el servidor de despliegue en producción que vams a utiloizar en este proyecto. Para ello necesitamos crear una cuenta en Google Cloud Plataform, donde nos dan la posibilidad de crearnos una cuenta gratuita de 90 días con 300 USD en crédito para poder utilizar servicios como Compute Engine, Cloud Storage y BigQuery.

Para acceder visite el siguiente enlace: https://console.cloud.google.com/


Una vez registrados, nos debe aparecer la página principal con el Dashboard general de la aplicación:

![1](docs/images/1_gc.PNG)

Seguidamente rocedemos a crear un nuevo proyecto de trabajo, pulsamos sobre el desplegable de proyectos, ```Despliegue TF2x``` en mi caso, y nos aparece la siguiente ventana emergente:

![2](docs/images/2_gc_crear_proyecto.PNG)

Pinchamos sobre ```NUEVO PROYECTO``` y nos aparece la ventana creación de un nuevo proyecto. Aquí asignamos el nombre que queramos para nuestro proyecto, en mi caso ```Despliegue TF2x```:

![3](docs/images/3_gc_crear_proyecto.PNG)

A continuación, vamos a crear la maquina virtual para el despliegue. En este caso vamos a utilizar una máquina con el so de Centos7. Para poder crear y configurar dicha máquina, primero hacemos una búsqueda ```Centos```y seleccionamos la ```CentOS 7```que vamos a dar de alta:

![5](docs/images/5_gc_crear_mv.PNG)

Una vez seleccionada nos aparece la siguiente ventana donde debemos iniciar la maquina pulsando sobre el botón ```iniciar```:

![6](docs/images/6_gc_iniciar_mv.PNG)

Una vez dentro, procedemos a configurar la máquina. en nuestro caso vamos a configurar el Tipo de máquina y su cortafuegos para permitir peticiones HTTP:

**Tipo de máquina**: e2-standard-4 (4 vCPU, 16 GB de memoria)

![8](docs/images/8_gc_conf_mv_1.PNG)

**Cortafuegos**: Permitir el tráfico HTTP.

![9](docs/images/9_gc_conf_mv_2.PNG)

Una vez configurada nos aparecera la siguiente ventana con nuestra máquina:

![10](docs/images/10_gc_end.PNG)

Como podeis observar también nos indica la IP externa de la máquina. Para acceder la la consola necesitaremos pulsar en el botón de ```PLAY``` y en el desplegable de ```SSH`` seleccionar la opción de abrir en una nueva pestaña del navegador:

![12](docs/images/12_gc_cmd.PNG)

Con ello, ya tenemos acceso a la consola de nuestro servidor, pero antes de seguir nos haria falta configurar las reglas del cortafuegos para permitir el acceso a través de los puertos de cada servicio.

La forma de acceder a esta configuración es pulsando en el desplegable de ```SSH``` en la opción de ```ver detalles de red```:

![20](docs/images/20_gc_red.PNG)

Una vez dentro, pinchamos sobre ```default-allow-http```:

![21](docs/images/21_gc_red_1.PNG)

Seguidamente damos click a la opción de ```EDITAR```:

![22](docs/images/22_gc_red_2.PNG)

Una vez dentro damos de alta todos los puertos utilizados en los servicios del proyecto:

- **9000**: API del servidor.
- **9001**: Visualizador de microservicios.
- **9002**: Prometheus.
- **9003**: Grafana.

![23](docs/images/23_gc_red_3.PNG)


Con todos estos pasos ya tendriamos acceso a la maquina virtual del servidor y podriamos proceder a configurar el entorno de trabajo y a dar de alta los servicios de nuestro proyecto.


## Configuración del entorno de trabajo

Una vez creado la maquina virtual del servidor procedemos a configurar el entorno de trabajo. Para ello abrimos la consola tal y como hemos comentado en el apartado anterior.

### Configuración Centos 7

En primer lugar instalamos el entorno virtual de ```miniconda``` para configurar el entorno virtual de trabajo en producción. Procedemos pues a introducir las siguientes lineas de comandos en la consola:

```cmd
####  CentOS Configuration ####

#Install tools on CentOS 7:
sudo yum –y update
sudo yum install -y zip unzip nano git tree wget

#Install an environment manager (Miniconda):
curl -LO https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
sh ./Miniconda3-latest-Linux-x86_64.sh

# Loading environment variables:
source ~/.bashrc

# Deactivate current environment (base):
conda deactivate
```

### Entorno Virtual de trabajo

A continuación se crea y se configura el entorno de trabajo de producción sobre el cual desplegaremos la API del servidor:

```cmd
#### Create PROD Environment ####

# Create an environment called "PROD" and install Python
conda create -n PROD pip python=3.7.0

#Activate PROD Environment
conda activate PROD

#Install python
pip install python=3.7.5

#Install TensorFlow in PROD:
pip install --no-cache-dir tensorflow==2.3.0
pip install tensorflow-serving-api

#Install FastAPI, uvicorn and other tools in PROD:
pip install fastapi
pip install uvicorn # ASGI server for production: https://github.com/tiangolo/fastapi
pip install python-multipart
pip install pillow #Pil image needed for tf.keras image

#Testing tools installation version:
python -c "import platform; print('/nPython: ',platform.python_version())"
python -c "import tensorflow as tf; print('TensorFlow: ',tf.__version__)"
python -c "import fastapi; print('FastAPI: ', fastapi.__version__)"

# Deactivate current environment:
conda deactivate
```

### Instalación y configuración de Docker

A continuación procedemos a instalar y configurar Docker que nos permitirá desplegar nuestros servicios como microservicios en Docker:

```cmd
#### Docker installation ####
# Reference: https://docs.docker.com/install/linux/docker-ce/centos/

# Install pre-requirements:
sudo yum install -y yum-utils device-mapper-persistent-data lvm2

# Add docker repo:
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install docker
sudo yum install -y docker-ce docker-ce-cli containerd.io

# Start Docker service
sudo systemctl start docker

# Validate Docker version
docker --version

# Post installation configuration
# sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker

# Download 'hello-world' docker image
docker pull hello-world

# Create a docker container from 'hello-world' image'
docker run hello-world

# List Docker objects
docker images #Images
docker ps -a  #Containers

#Stop Docker service
sudo systemctl stop docker
```

## Clonar Repositorio del proyecto

Clonamos el repositorio de código del proyecto: [GitHub | ProductionTF2serving](https://github.com/jaisenbe58r/ProductionTF2serving)

```cmd
#Clone main deployment project:
cd ~
git clone https://github.com/jaisenbe58r/ProductionTF2serving.git
```


## Despliegue de servicios con Docker swarm

Docker Swarm es una herramienta integrada en el ecosistema de Docker que permite la gestión de un cluster de servidores. Pone a nuestra disposición una API con la que podemos administrar las  tareas y asignación de recursos de cada contenedor dentro de cada una de las máquinas. Dicha API nos permite gestionar el cluster como si se tratase de una sola máquina Docker.

Para nuestro proyecto, se genera un clúster con docker swarm con 4 replicas del microservicio de ```tensorflow/serving``` para servir las predicciones, 1 visualizador de contenedores docker en el clúster (visualizer), 1 microservicio de monitoreo de servicios (prometheus) y 1 microservicio de consulta y visualización (grafana):

```yml
version: '3'

services:
  pets:
    image: tensorflow/serving
    ports:
      - 9500:8500
      - 9501:8501
    volumes:
      - ${MODEL_PB}:/models/pets
    environment:
      - MODEL_NAME=pets
    deploy:
      replicas: 4
    command:
      - --enable_batching=true

  visualizer:
    image: dockersamples/visualizer
    ports:
      - 9001:8080
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    deploy:
      placement:
        constraints: [node.role == manager]

  prometheus:
    image: prom/prometheus
    ports:
      - 9002:9090

  grafana:
    image: grafana/grafana:latest
    ports:
      - 9003:3000
    links:
      - prometheus:prometheus
    environment:
      - GF_USERS_ALLOW_SIGN_UP=false
```

Para poder desplegar el clúster de docker swarm vamos a ejecutar las siguientes lineas de comandos:


```cmd
#### Deployment PROD ####

#Start docker service
sudo systemctl start docker

#Remove all Containers (optional)
docker rm $(docker ps -aq)

#Folder with PB model
cd ~
export MODEL_PB=$(pwd)/ProductionTF2serving/model/tf2x/tensorflow

#Start Docker Swarm
docker swarm init

#Start TensorFlow serving with docker-compose:
cd $(pwd)/ProductionTF2serving/Deployment/docker

docker stack deploy -c compose-config-PROD.yml PROD-STACK

```


## Chequear servivios activos

Una vez desplejado el clúster con todos los microservicios vamos a chequear que dichos servicios estén activos. Para ello vamos a ejecutar lo siguiente:

```cmd
docker stack ls
docker service ls
docker container ls
```

Para acceder al visualizador del clúster, basta con introducir en su navegador predeterminado la siguiente ruta:

http://```<public IP>```:9001/


Para eliminar el clúster de docker swarm ejecuta lo siguiente:

```cmd
# Remove stack
docker stack rm PROD-STACK

# Leave docker swarm
docker swarm leave --force

# Stop docker
sudo systemctl stop docker
```

## Servicio FastAPI 

El servicio FastAPI se despliega externamente al clúster de docker swarm dentro del entorno virtual de Producción. Este servicio es la API que recibe las peticiones ```HTTP``` de los clientes y se encarga de comunicarse directamente con los microservicios servidores del modelo para realizar las predicciones y posteriormente devolver el resultado al cliente.

Para desplegar este el servicio Fast API procedemos de la siguiente manera:

```cmd
#### Start FastAPI service  ####

# starting the service
cd $(pwd)/ProductionTF2serving/Deployment/service

# Activando environment PROD
conda activate PROD

# starting web-service
uvicorn fastapi_service_PROD:app --port 9000 --host 0.0.0.0
```

En caso de querer detener este servicio se ejecutará:

```cmd
# Stop Web Service: Ctrl + C

# Deactivate PROD env
conda deactivate
```

## Monitorización

Como hemos comentado anteriormente, hemos desplegado el microservicio de grafana y prometheus que nos permiten almacenar y visualizar las metricas del cluster en funcionamiento que previamente configuremos.

Para acceder 

```
#### Monitoring ####

# Prometheus: IP:9002

# Grafana: IP:9003
# >> admin/admin

# Grafana Datasource:
# >> public-ip:9002
# >> server

# Grafana dashboards to import
https://grafana.com/grafana/dashboards?dataSource=prometheus

```

## 

curl -i -X POST -F "file=@0f8c1af582.jpg" http://34.69.28.27:9000/model/predict/