
# Despliegue en producción de un Modelo TF2 de clasificación de imágenes.

![Portada](docs/images/08_Deployment_images.png)

## Configuración del entorno de trabajo


Una vez ...
```cmd
####  CentOS Configuration ####

#Install tools on CentOS 7:
sudo yum –y update
sudo yum install -y zip unzip nano git tree wget

#Install an environment manager (Miniconda):
curl -LO https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
sh ./Miniconda3-latest-Linux-x86_64.sh

#Loading environment variables:
source ~/.bashrc

#Deactivate current environment (base):
conda deactivate
```

A continuación se crea el entrono de trabajo de producción ....

```cmd
#### Create PROD Environment ####

#Create an environment called "PROD" and install Python
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
python -c "import platform; print('\nPython: ',platform.python_version())"
python -c "import tensorflow as tf; print('TensorFlow: ',tf.__version__)"
python -c "import fastapi; print('FastAPI: ', fastapi.__version__)"

#Deactiavate current environment:
conda deactivate

```


```cmd
#### Deployment PROD ####

#Start docker service
sudo systemctl start docker

#Remove all Containers (optional)
docker rm $(docker ps -aq)

#Folder with PB model
cd ~
export MODEL_PB=$(pwd)/Pebrassos-detection/model/tf2x/tensorflow

#Start Docker Swarm
docker swarm init

#Start TensorFlow serving with docker-compose:
cd $(pwd)/Pebrassos-detection/Deployment/docker

docker stack deploy -c compose-config-PROD.yml PROD-STACK

```

## Chequear servivios activos

```cmd
docker stack ls
docker service ls
docker container ls

#Visualize servicew on web browser (don't forget open port 9001)
http://<public IP>:9001/

#Activate PROD environment
conda activate PROD

#Locate on test folder
cd $(pwd)/Pebrassos-detection/Deployment/test

#TFserving on gGPR 9500 --> 8500
python test-tfserving-gRPC-PROD.py \
    --images $(pwd)/images/img01.jpg,$(pwd)/images/img02.jpg,$(pwd)/images/img03.jpg \
    --model flowers \
    --version 1 \
    --port 9500

# Remove stack
docker stack rm PROD-STACK

#Leave docker swarm
docker swarm leave --force

# Stop docker
sudo systemctl stop docker
```

## Servicio FastAPI 

```cmd
#### Start FastAPI service  ####

# starting the service
cd $(pwd)/Pebrassos-detection/Deployment/service

# Activando environment PROD
conda activate PROD

# starting web-service
uvicorn fastapi_service_PROD:app --port 9000 --host 0.0.0.0

#Stop Web Service: Ctrl + C

#Deactivate PROD env
conda deactivate
```

## Monitorización

```cmd
#### Monitoring ####

#Prometheus: IP:9002

#Grafana: IP:9003
#>> admin/admin
#Grafana Datasource:
#>> public-ip:9002
#>> server

#Grafana dashboards to import
https://grafana.com/grafana/dashboards?dataSource=prometheus

```