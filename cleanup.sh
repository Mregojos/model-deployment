#---------Application Name Environment Variables----------#
# TO DO: In prodcution, change these values.
VERSION="iii"
APP_NAME="app-prod-$VERSION"

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
STATIC_IP_ADDRESS_NAME="db-static-ip-address"
BUCKET_NAME="$APP_NAME-startup-script"
STARTUP_SCRIPT_BUCKET_SA="startup-script-bucket-sa"
STARTUP_SCRIPT_BUCKET_CUSTOM_ROLE="bucketCustomRole.$VERSION"
# STARTUP_SCRIPT_NAME="$APP_NAME-startup-script.sh"

# For Notebook 
NOTEBOOK_REGION='us-central1'
RANGE_C='10.150.0.0/20'

#---------Database Credentials----------#
DB_CONTAINER_NAME="$APP_NAME-postgres-sql"
DB_NAME="$APP_NAME-admin"
DB_USER="$APP_NAME-admin" 
# DB_HOST=$(gcloud compute addresses describe $STATIC_IP_ADDRESS_NAME --region $REGION | grep "address: " | cut -d " " -f2)
DB_HOST=$(gcloud compute instances list --filter="name=$DB_INSTANCE_NAME" --format="value(networkInterfaces[0].accessConfigs[0].natIP)") 
DB_PORT=5000
# TO DO
DB_PASSWORD=$APP_NAME # change the value in production 
PROJECT_NAME="$(gcloud config get project)"
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

#----------Delete Resources----------#
gcloud compute instances delete $DB_INSTANCE_NAME --zone=$ZONE --quiet
gcloud compute addresses delete $STATIC_IP_ADDRESS_NAME --region $REGION --quiet
gcloud compute firewall-rules delete $FIREWALL_RULES_NAME --quiet
gcloud artifacts repositories delete $APP_ARTIFACT_NAME --location=$REGION --quiet
gcloud run services delete $APP_NAME --region=$REGION --quiet
gcloud storage rm -r gs://$BUCKET_NAME
gcloud storage rm -r gs://$(gcloud config get project)_cloudbuild


# Remove IAM Policy Binding to the Bucket Service Account
# gcloud projects remove-iam-policy-binding \
#    $(gcloud config get project) \
#    --member=serviceAccount:$STARTUP_SCRIPT_BUCKET_SA@$(gcloud config get project).iam.gserviceaccount.com \
#    --role=roles/storage.objectViewer

# Remove IAM Policy Binding to the App Service Account
gcloud projects remove-iam-policy-binding \
    $(gcloud config get project) \
    --member=serviceAccount:$STARTUP_SCRIPT_BUCKET_SA@$(gcloud config get project).iam.gserviceaccount.com \
    --role=projects/$(gcloud config get project)/roles/$STARTUP_SCRIPT_BUCKET_CUSTOM_ROLE

gcloud iam service-accounts delete $STARTUP_SCRIPT_BUCKET_SA@$(gcloud config get project).iam.gserviceaccount.com --quiet

# Add IAM Policy Binding to the App Service Account
# gcloud projects remove-iam-policy-binding \
#    $(gcloud config get project) \
#    --member=serviceAccount:$APP_SERVICE_ACCOUNT_NAME@$(gcloud config get project).iam.gserviceaccount.com \
#    --role=roles/aiplatform.user

# Remove IAM Policy Binding to the App Service Account
gcloud projects remove-iam-policy-binding \
    $(gcloud config get project) \
    --member=serviceAccount:$APP_SERVICE_ACCOUNT_NAME@$(gcloud config get project).iam.gserviceaccount.com \
    --role=projects/$(gcloud config get project)/roles/$APP_CUSTOM_ROLE

gcloud iam service-accounts delete $APP_SERVICE_ACCOUNT_NAME@$(gcloud config get project).iam.gserviceaccount.com --quiet



echo "\n #----------Services and Resources have been Successfully deleted.----------# \n"



#----------Requires Project Owner Permission----------#
# Delete
gcloud iam roles delete $STARTUP_SCRIPT_BUCKET_CUSTOM_ROLE \
    --project=$(gcloud config get project)

# Undelete
# gcloud iam roles undelete $STARTUP_SCRIPT_BUCKET_CUSTOM_ROLE \
#    --project=$(gcloud config get project)

# Delete
gcloud iam roles delete $APP_CUSTOM_ROLE \
    --project=$(gcloud config get project)

# Undelete
# gcloud iam roles undelete $APP_CUSTOM_ROLE \
#    --project=$(gcloud config get project) 

# Delete Subnets
gcloud compute networks subnets delete $SUBNET_NAME-$REGION --region=$REGION --quiet
gcloud compute networks subnets delete $SUBNET_NAME-$CLOUD_BUILD_REGION --region=$CLOUD_BUILD_REGION --quiet
gcloud compute networks subnets delete $SUBNET_NAME-$NOTEBOOK_REGION --region=$NOTEBOOK_REGION --quiet

# Delete Custom VPC
gcloud compute networks delete $VPC_NAME --quiet

echo "\n #----------Custom Roles have been Successfully deleted.----------# \n"