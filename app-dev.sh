#----------Enable Artifact Registry, Cloud Build, and Cloud Run, Vertex AI----------#
# Directory
cd app-dev

#---------Application Name Environment Variables----------#
# TO DO: In prodcution, change these values.
VERSION="iii"
APP_NAME="app-prod-$VERSION"

#---------Project Environment Variables---------#
PROJECT_NAME=$(gcloud config get project)

#----------Database Instance Environment Variables----------#
DB_INSTANCE_NAME="$APP_NAME-db"
MACHINE_TYPE="e2-micro"
REGION="us-west1"
ZONE="us-west1-a"
BOOT_DISK_SIZE="30"
TAGS="db"
FIREWALL_RULES_NAME="$APP_NAME-ports"
STATIC_IP_ADDRESS_NAME="db-static-ip-address"
BUCKET_NAME="$APP_NAME-startup-script"
STARTUP_SCRIPT_BUCKET_SA="startup-script-bucket-sa"
STARTUP_SCRIPT_BUCKET_CUSTOM_ROLE="bucketCustomRole.$VERSION"
# STARTUP_SCRIPT_NAME="$APP_NAME-startup-script.sh"

#---------Database Credentials----------#
DB_CONTAINER_NAME="$APP_NAME-postgres-sql"
DB_NAME="$APP_NAME-admin"
DB_USER="$APP_NAME-admin" 
DB_HOST=$(gcloud compute instances list --filter="name=$DB_INSTANCE_NAME" --format="value(networkInterfaces[0].accessConfigs[0].natIP)") 
DB_PORT=5000
# TO DO
DB_PASSWORD=$APP_NAME # change the value in production 
PROJECT_NAME='$(gcloud config get project)'
# TO DO
ADMIN_PASSWORD=$APP_NAME # change the value in production
APP_PORT=9000
# APP_ADDRESS= # change the value in production
# TO DO
DOMAIN_NAME="" # change the value in production
# TO DO
SPECIAL_NAME=$APP_NAME # change the value in production

#----------Deployment Environment Variables----------#
CLOUD_BUILD_REGION="us-west2"
REGION="us-west1"
APP_ARTIFACT_NAME="$APP_NAME-artifact-registry"
APP_VERSION="latest"
APP_SERVICE_ACCOUNT_NAME="app-service-account"
APP_CUSTOM_ROLE="appCustomRole.$VERSION"
APP_PORT=9000
APP_ENV_FILE=".env.yaml"
MIN_INSTANCES=1
MAX_INSTANCES=1

echo "\n #----------Exporting Environment Variables is done.----------# \n"

# Environment Variables for the app
echo """DB_NAME=$DB_USER
DB_USER=$DB_USER 
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_PASSWORD=$DB_PASSWORD
PROJECT_NAME=$PROJECT_NAME
ADMIN_PASSWORD=$ADMIN_PASSWORD
APP_PORT=$APP_PORT
APP_ADRESS=$APP_ADDRESS
DOMAIN_NAME=$DOMAIN_NAME
SPECIAL_NAME=$SPECIAL_NAME
""" > .env.sh

# Remove docker container
# docker rm -f $APP_NAME

# Build
docker build -t $APP_NAME .

# Run
docker run -d -p 9000:9000 -v $(pwd):/app --env-file .env.sh --name $APP_NAME $APP_NAME

# Create a firewall (GCP)
# gcloud compute --project=$(gcloud config get project) firewall-rules create $FIREWALL_RULES_NAME \
#    --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:5000,tcp:8000,tcp:9000 --source-ranges=0.0.0.0/0 

# Remove docker container
# docker rm -f $APP_NAME

# Remove docker container all
# docker rm -f $(docker ps -aq)

# Remove the db data
# sudo rm -f data

# Docker exec
# docker exec -it $APP_NAME sh



