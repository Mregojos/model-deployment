# site-model-app-dev
# sh site-model-app-dev.sh

# Objective
# * To create a web app and use model apis

#----------Enable Artifact Registry, Cloud Build, and Cloud Run, Vertex AI----------#
# !gcloud services list --available
gcloud services enable iam.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com run.googleapis.com aiplatform.googleapis.com cloudresourcemanager.googleapis.com
echo "\n #----------Services have been successfully enabled.----------# \n"

#----------Environment Variables----------#
VERSION="vi"
APP_NAME="site-model-app-dev-$VERSION"
FIREWALL_RULES_NAME="ports"
INSTANCE_NAME="matt"

#----------Database Instance Environment Variables----------#
DB_INSTANCE_NAME="$APP_NAME-db"

#---------Database Credentials----------#
DB_CONTAINER_NAME="$APP_NAME-postgres-sql"
# DB_NAME="$APP_NAME-db"
DB_USER="$APP_NAME-admin" 
DB_HOST=$(gcloud compute instances list --filter="name=$DB_INSTANCE_NAME" --format="value(networkInterfaces[0].accessConfigs[0].natIP)") 
DB_PORT=5000
DB_PASSWORD='password' # change the value in production 
PROJECT_NAME='$(gcloud config get project)'
ADMIN_PASSWORD=password # change the value in production
APP_PORT=9000
APP_ADRESS= # change the value in production
DOMAIN_NAME= # change the value in production
SPECIAL_NAME='Matt' # change the value in production

#----------Database for local development----------#
# With volume/data connected
# cd app-model 
# cd app-model
docker run -d \
    --name $DB_CONTAINER_NAME \
    -e POSTGRES_USER=$DB_USER \
    -e POSTGRES_PASSWORD=$DB_PASSWORD \
    -v $(pwd)/data/:/var/lib/postgresql/data/ \
    -p $DB_PORT:5432 \
    postgres
docker run -p 8000:80 \
    -e 'PGADMIN_DEFAULT_EMAIL=matt@example.com' \
    -e 'PGADMIN_DEFAULT_PASSWORD=password' \
    -d dpage/pgadmin4
    
#----------Local Development----------#
# ***** Use with container instead of this 
# Virtual Environment
# virtualenv env
# source env/bin/activate
# cd app-dev
# pip install -U -r requirements.txt -q
# streamlit run app-model.py --server.address=0.0.0.0 --server.port=9000

# Create a firewall (GCP)
# gcloud compute --project=$(gcloud config get project) firewall-rules create $FIREWALL_RULES_NAME \
#     --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:5000,tcp:8000,tcp:9000 --source-ranges=0.0.0.0/0 

# For Local Development
# export DBNAME='matt'
# export USER='matt' 
# export HOST='$(gcloud compute instances list --filter="name=$INSTANCE_NAME" --format="value(networkInterfaces[0].accessConfigs[0].natIP)")' 
# export DBPORT='5000'
# export DBPASSWORD='password' 
# export PROJECT_NAME='$(gcloud config get project)'

#----------Local Development using container with deployment environment variables----------#
# For App Development
cd site-model-app-dev

# Environment Variables for the app
echo """DB_NAME=$DB_USER
DB_USER=$DB_USER 
# DB_HOST=$(gcloud compute instances list --filter="name=$INSTANCE_NAME" --format="value(networkInterfaces[0].accessConfigs[0].natIP)") 
DB_HOST=$DB_HOST
DB_PORT=5000
DB_PASSWORD=$DB_PASSWORD
PROJECT_NAME='$(gcloud config get project)'
ADMIN_PASSWORD=$ADMIN_PASSWORD
APP_PORT=9000
APP_ADRESS=
DOMAIN_NAME=
SPECIAL_NAME=$SPECIAL_NAME
""" > .env.sh

# Remove docker container
# docker rm -f $APP_NAME

# Build
docker build -t $APP_NAME .

# Run
docker run -d -p 9000:9000 -v $(pwd):/app --env-file .env.sh --name $APP_NAME $APP_NAME

# Create a firewall (GCP)
gcloud compute --project=$(gcloud config get project) firewall-rules create $FIREWALL_RULES_NAME \
    --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:5000,tcp:8000,tcp:9000 --source-ranges=0.0.0.0/0 
# Remove docker container
# docker rm -f $APP_NAME

# Remove docker container all
# docker rm -f $(docker ps -aq)
# sudo rm -f data
# Docker exec
# docker exec -it $APP_NAME sh



