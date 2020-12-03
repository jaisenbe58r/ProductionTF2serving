# Commands for deployment in PROD Environment (Centos 7 - Linux)

############################ Deployment PROD ############################
#Start docker service
sudo systemctl start docker

#Remove all Containers (optional)
docker rm $(docker ps -aq)

#Folder with PB model
cd ~
export MODEL_PB=$(pwd)/models/tf2x/tensorflow

#Start Docker Swarm
docker swarm init

#Start TensorFlow serving with docker-compose:
cd ~/DEEP-LEARNING_deployment/Deployment-PROD4/docker

docker stack deploy -c compose-config-PROD.yml PROD-STACK

# Check services/containers
docker stack ls
docker service ls
docker container ls

#Visualize servicew on web browser (don't forget open port 9001)
http://<public IP>:9001/

#Activate PROD environment
conda activate PROD

#Locate on test folder
cd ~/DEEP-LEARNING_deployment/Deployment-PROD4/test

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
#########################################################################

######################### Start FastAPI service  ########################
# starting the service
cd ~/DEEP-LEARNING_deployment/Deployment-PROD4/service/

# Activando environment PROD
conda activate PROD

# starting web-service
uvicorn fastapi_service_PROD:app --port 9000 --host 0.0.0.0
#########################################################################

#Stop Web Service: Ctrl + C

#Deactivate PROD env
conda deactivate


############################### Monitoring ##############################
#Prometheus: IP:9002

#Grafana: IP:9003
#>> admin/admin
#Grafana Datasource:
#>> public-ip:9002
#>> server

#Grafana dashboards to import
https://grafana.com/grafana/dashboards?dataSource=prometheus
