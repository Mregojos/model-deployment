#---------Application Name Environment Variables----------#
# In production, change these values.
export VERSION="i"
export APP_NAME="app-prod-$VERSION"
export DB_PASSWORD="password"
export ADMIN_PASSWORD="password"
export SPECIAL_NAME="guest"

#---------Project Environment Variable---------#
export PROJECT_NAME="$(gcloud config get project)"

#----------Database Instance Environment Variables----------#
export VPC_NAME="$APP_NAME-vpc"
export SUBNET_NAME="$APP_NAME-subnet"
export RANGE_A='10.100.0.0/20'
export RANGE_B='10.200.0.0/20'
export DB_INSTANCE_NAME="$APP_NAME-db"
export MACHINE_TYPE="e2-micro"
export REGION="us-west1"
export ZONE="us-west1-a"
export BOOT_DISK_SIZE="30"
export TAGS="db"
export FIREWALL_RULES_NAME="$APP_NAME-ports"
export STATIC_IP_ADDRESS_NAME="$APP_NAME-db-static-ip-address"
export BUCKET_NAME="$APP_NAME-startup-script"
export STARTUP_SCRIPT_BUCKET_SA="$APP_NAME-bucket-sa"
export STARTUP_SCRIPT_BUCKET_CUSTOM_ROLE="appDeploymentBucketCustomRole.$VERSION"
# export STARTUP_SCRIPT_NAME="$APP_NAME-startup-script.sh"

# For Notebook 
export NOTEBOOK_REGION='us-central1'
export RANGE_C='10.150.0.0/20'

#---------Database Credentials----------#
export DB_CONTAINER_NAME="$APP_NAME-sql"
export DB_NAME="$APP_NAME-admin"
export DB_USER="$APP_NAME-admin" 
# export DB_HOST=$(gcloud compute addresses describe $STATIC_IP_ADDRESS_NAME --region $REGION | grep "address: " | cut -d " " -f2)
export DB_HOST=$(gcloud compute instances list --filter="name=$DB_INSTANCE_NAME" --format="value(networkInterfaces[0].accessConfigs[0].natIP)") 
export DB_PORT=5000
export DB_PASSWORD=$DB_PASSWORD
export ADMIN_PASSWORD=$ADMIN_PASSWORD
export APP_PORT=9000
export APP_ADDRESS=""
export DOMAIN_NAME="" 
export SPECIAL_NAME=$SPECIAL_NAME

#----------Deployment Environment Variables----------#
export CLOUD_BUILD_REGION="us-west2"
export REGION="us-west1"
export APP_ARTIFACT_NAME="$APP_NAME-artifact-registry"
export APP_VERSION="latest"
export APP_SERVICE_ACCOUNT_NAME="$APP_NAME-app-sa"
export APP_CUSTOM_ROLE="appDeploymentCustomRole.$VERSION"
export APP_PORT=9000
export APP_ENV_FILE=".env.yaml"
export MIN_INSTANCES=1
export MAX_INSTANCES=1

echo "\n #----------Exporting Environment Variables is done.----------# \n"