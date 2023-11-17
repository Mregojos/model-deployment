# Local Development
# app-dev

# Objective
# * To create a web app and use model apis

#----------Enable Artifact Registry, Cloud Build, and Cloud Run, Vertex AI
# !gcloud services list --available
gcloud services enable cloudbuild.googleapis.com artifactregistry.googleapis.com run.googleapis.com aiplatform.googleapis.com cloudresourcemanager.googleapis.com
echo "\n #----------Services have been successfully enabled.----------# \n"

#----------Environment Variables
VERSION="i"
APP_NAME="app-model-dev-$VERSION"
# APP_NAME="simple-app"
FIREWALL_RULES_NAME="ports"

#----------Database
# With volume/data connected
# cd app-model 
# cd app-model
docker run -d \
    --name postgres-sql \
    -e POSTGRES_USER=matt \
    -e POSTGRES_PASSWORD=password \
    -v $(pwd)/data/:/var/lib/postgresql/data/ \
    -p 5000:5432 \
    postgres
docker run -p 8000:80 \
    -e 'PGADMIN_DEFAULT_EMAIL=matt@example.com' \
    -e 'PGADMIN_DEFAULT_PASSWORD=password' \
    -d dpage/pgadmin4
    
#----------Local Development----------#
# Virtual Environment
virtualenv env
source env/bin/activate
# cd app-dev
pip install -U -r requirements.txt -q
streamlit run app-model.py --server.address=0.0.0.0 --server.port=9000

# Create a firewall (GCP)
gcloud compute --project=$(gcloud config get project) firewall-rules create $FIREWALL_RULES_NAME \
    --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:5000,tcp:8000,tcp:9000 --source-ranges=0.0.0.0/0 

# For Local Development
export DBNAME='matt'
export USER='matt' 
export HOST='' 
export DBPORT='5000'
export DBPASSWORD='password' 
export PROJECT_NAME='$(gcloud config get project)'

#----------Local Development using container----------#
# Environment Variables for the app
echo """DBNAME='matt'
USER='matt' 
HOST='34.135.111.54' 
DBPORT='5000'
DBPASSWORD='password' 
PROJECT_NAME='$(gcloud config get project)'
ADMIN_PASSWORD='password'
""" > env.sh

# For App Development
cd app-dev
# Build
docker build -t $APP_NAME Dockerfile

# Run
docker run -d -p 9000:9000 -v $(pwd):/app --env-file env.sh --name $APP_NAME $APP_NAME

# Create a firewall (GCP)
gcloud compute --project=$(gcloud config get project) firewall-rules create $FIREWALL_RULES_NAME \
    --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:5000,tcp:8000,tcp:9000 --source-ranges=0.0.0.0/0 
# Remove docker container
# docker rm -f $APP_NAME


# Remove docker container all
# docker rm -f $(docker ps -aq)
# Docker exec
# docker exec -it $APP_NAME sh



#----------Delete Resources----------#
gcloud compute instances delete $DB_NAME --zone=$ZONE --quiet