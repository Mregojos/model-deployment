#---------Application Name Environment Variables----------#
# TO DO: In prodcution, change these values.
VERSION="i" # Change this
APP_NAME="-$VERSION"

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
# DB_NAME="$APP_NAME-db"
DB_USER="$APP_NAME-admin" 
DB_HOST=$(gcloud compute instances list --filter="name=$DB_INSTANCE_NAME" --format="value(networkInterfaces[0].accessConfigs[0].natIP)") 
DB_PORT=5000
DB_PASSWORD='sitedbapp' # change the value in production 
PROJECT_NAME='$(gcloud config get project)'
# TO DO
ADMIN_PASSWORD= # change the value in production
APP_PORT=9000
APP_ADRESS= # change the value in production
DOMAIN_NAME= "site.mattcloudtech.com" # change the value in production
# TO DO
SPECIAL_NAME='' # change the value in production

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

echo "\n #----------Custom Roles have been Successfully deleted.----------# \n"