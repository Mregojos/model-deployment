#----------Enable Artifact Registry, Cloud Build, and Cloud Run, Vertex AI----------#
# Directory
cd app-dev

# Directory
# cd app-deployment

#---------Application Name Environment Variables----------#
# In production, change these values.
VERSION="i"
APP_NAME="app-prod-$VERSION"
DB_PASSWORD="password"
ADMIN_PASSWORD="password"
SPECIAL_NAME="guest"

#---------Project Environment Variable---------#
PROJECT_NAME="$(gcloud config get project)"

#----------Database Instance Environment Variables----------#
VPC_NAME="$APP_NAME-vpc"
SUBNET_NAME="$APP_NAME-subnet"
RANGE_A='10.100.0.0/20'
RANGE_B='10.200.0.0/20'
DB_INSTANCE_NAME="$APP_NAME-db"
MACHINE_TYPE="e2-micro"
REGION="us-west1"
ZONE="us-west1-a"
BOOT_DISK_SIZE="30"
TAGS="db"
FIREWALL_RULES_NAME="$APP_NAME-ports"
STATIC_IP_ADDRESS_NAME="$APP_NAME-db-static-ip-address"
BUCKET_NAME="$APP_NAME-startup-script"
STARTUP_SCRIPT_BUCKET_SA="$APP_NAME-bucket-sa"
STARTUP_SCRIPT_BUCKET_CUSTOM_ROLE="appDeploymentBucketCustomRole.$VERSION"
# STARTUP_SCRIPT_NAME="$APP_NAME-startup-script.sh"

# For Notebook 
NOTEBOOK_REGION='us-central1'
RANGE_C='10.150.0.0/20'

#---------Database Credentials----------#
DB_CONTAINER_NAME="$APP_NAME-sql"
DB_NAME="$APP_NAME-admin"
DB_USER="$APP_NAME-admin" 
# DB_HOST=$(gcloud compute addresses describe $STATIC_IP_ADDRESS_NAME --region $REGION | grep "address: " | cut -d " " -f2)
DB_HOST=$(gcloud compute instances list --filter="name=$DB_INSTANCE_NAME" --format="value(networkInterfaces[0].accessConfigs[0].natIP)") 
DB_PORT=5000
DB_PASSWORD=$DB_PASSWORD
ADMIN_PASSWORD=$ADMIN_PASSWORD
APP_PORT=9000
APP_ADDRESS=""
DOMAIN_NAME="" 
SPECIAL_NAME=$SPECIAL_NAME

#----------Deployment Environment Variables----------#
CLOUD_BUILD_REGION="us-west2"
REGION="us-west1"
APP_ARTIFACT_NAME="$APP_NAME-artifact-registry"
APP_VERSION="latest"
APP_SERVICE_ACCOUNT_NAME="$APP_NAME-app-sa"
APP_CUSTOM_ROLE="appDeploymentCustomRole.$VERSION"
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
gcloud compute --project=$(gcloud config get project) firewall-rules create $FIREWALL_RULES_NAME-dev \
    --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:9000 --source-ranges=0.0.0.0/0 

# Remove docker container
# docker rm -f $APP_NAME

# Remove docker container all
# docker rm -f $(docker ps -aq)

# Remove the db data
# sudo rm -f data

# Docker exec
# docker exec -it $APP_NAME sh

echo "\n #----------DONE----------# \n"

