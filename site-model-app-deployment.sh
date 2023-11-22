# site-model-app-deployment
# sh site-model-app-deployment.sh

# Objective
# * To deploy a pre-trained model on GCP

#----------Enable Artifact Registry, Cloud Build, and Cloud Run, Vertex AI
# !gcloud services list --available
gcloud services enable iam.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com run.googleapis.com aiplatform.googleapis.com cloudresourcemanager.googleapis.com
echo "\n #----------Services have been successfully enabled.----------# \n"

# Directory
cd site-model-app-deployment

# TO DO: In prodcution, change these values.
#---------Application Name Environment Variables----------#
VERSION="x" # Change this
APP_NAME="site-model-app-deployment-$VERSION"

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
DB_PASSWORD='password' # change the value in production 
PROJECT_NAME='$(gcloud config get project)'
ADMIN_PASSWORD=password # change the value in production
APP_PORT=9000
APP_ADRESS= # change the value in production
DOMAIN_NAME= # change the value in production
SPECIAL_NAME='Matt' # change the value in production

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

#----------Database Instance Section----------#
# Create a static external ip address
gcloud compute addresses create $STATIC_IP_ADDRESS_NAME --region $REGION
echo "\n #----------Static IP Address has been successfully created.----------# \n"

# Make a bucket
gcloud storage buckets create gs://$BUCKET_NAME
echo "\n #----------THe bucket has been successfully created.---------- # \n"

# Startup-script.sh
# touch startup-script.sh
# Change the version

# Copy the file to Cloud Storage
gcloud storage cp startup-script.sh gs://$BUCKET_NAME
echo "\n #----------Startup script has been successfully copied.----------# \n"

#----------Use this service account only for deployment development ans use the custom service account for production----------#
# Create a service account
gcloud iam service-accounts create $STARTUP_SCRIPT_BUCKET_SA
echo "\n #----------Bucket Service Account has been successfully created.----------# \n"

# Add IAM Policy Binding to the Bucket Service Account
# gcloud projects add-iam-policy-binding \
#    $(gcloud config get project) \
#    --member=serviceAccount:$STARTUP_SCRIPT_BUCKET_SA@$(gcloud config get project).iam.gserviceaccount.com \
#    --role=roles/storage.objectViewer

#----------To create a custom role. Use this in Production.----------#
# It needs Project Owner Role.

# To describe and list IAM Roles 
# gcloud iam roles describe roles/storage.objectUser
gcloud iam roles create $STARTUP_SCRIPT_BUCKET_CUSTOM_ROLE \
    --project=$(gcloud config get project) \
    --title=$STARTUP_SCRIPT_BUCKET_CUSTOM_ROLE \
    --description="Get the object only" \
    --permissions=storage.objects.get \
    --stage=GA

# Add IAM Policy Binding to the App Service Account
gcloud projects add-iam-policy-binding \
    $(gcloud config get project) \
    --member=serviceAccount:$STARTUP_SCRIPT_BUCKET_SA@$(gcloud config get project).iam.gserviceaccount.com \
    --role=projects/$(gcloud config get project)/roles/$STARTUP_SCRIPT_BUCKET_CUSTOM_ROLE
echo "\n #----------Bucket Service Account IAM has been successfully binded.----------# \n"

# Print the Static IP Address
# gcloud compute addresses describe $STATIC_IP_ADDRESS_NAME --region $REGION | grep "address: " | cut -d " " -f2

# Create an instance with these specifications
gcloud compute instances create $DB_INSTANCE_NAME \
    --machine-type=$MACHINE_TYPE --zone=$ZONE --tags=$TAGS \
    --boot-disk-size=$BOOT_DISK_SIZE \
    --service-account=$STARTUP_SCRIPT_BUCKET_SA@$(gcloud config get project).iam.gserviceaccount.com  \
    --metadata=startup-script-url=gs://$BUCKET_NAME/startup-script.sh \
    --network-interface=address=$(gcloud compute addresses describe $STATIC_IP_ADDRESS_NAME --region $REGION | grep "address: " | cut -d " " -f2)
echo "\n #----------Compute Instance has been successfully created.----------# \n"

# Create a firewall rule (GCP)
# TO DO: In production, only open the DB port and add tags
gcloud compute --project=$(gcloud config get project) firewall-rules create $FIREWALL_RULES_NAME \
    --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:5000,tcp:8000,tcp:9000 --source-ranges=0.0.0.0/0 # \
    # --target-tags=$TAGS
echo "\n #----------Firewall Rules has been successfully created.----------# \n"

#----------Deployment Section----------#

# Create a Docker repository in Artifact Registry
gcloud artifacts repositories create $APP_ARTIFACT_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker repository"
echo "\n #----------Artifact Repository has been successfully created.----------# \n"

# build and submnit an image to Artifact Registry
gcloud builds submit \
    --region=$CLOUD_BUILD_REGION \
    --tag $REGION-docker.pkg.dev/$(gcloud config get-value project)/$APP_ARTIFACT_NAME/$APP_NAME:$APP_VERSION
echo "\n #----------Docker image has been successfully built.----------# \n"

# For Cloud Run Deploy, use a Service Account with Cloud Run Admin
# For Cloud Run Deployed App Service, use a Service Account with Vertex AI User or with (prefered in production) custom IAM Role 
# Create IAM Service Account for the app
gcloud iam service-accounts create $APP_SERVICE_ACCOUNT_NAME
echo "\n #----------Service Account has been successfully created.----------# \n"

# Add IAM Policy Binding to the App Service Account
# gcloud projects add-iam-policy-binding \
#    $(gcloud config get project) \
#    --member=serviceAccount:$APP_SERVICE_ACCOUNT_NAME@$(gcloud config get project).iam.gserviceaccount.com \
#    --role=roles/aiplatform.user

# To create a custom role it needs Project Owner Role
# App Custom Role
gcloud iam roles create $APP_CUSTOM_ROLE \
    --project=$(gcloud config get project) \
    --title=$APP_CUSTOM_ROLE \
    --description="Predict Only" \
    --permissions=aiplatform.endpoints.predict \
    --stage=GA

# Add IAM Policy Binding to the App Service Account
gcloud projects add-iam-policy-binding \
    $(gcloud config get project) \
    --member=serviceAccount:$APP_SERVICE_ACCOUNT_NAME@$(gcloud config get project).iam.gserviceaccount.com \
    --role=projects/$(gcloud config get project)/roles/$APP_CUSTOM_ROLE
echo "\n #----------App Service Account has been successfully binded.----------# \n"

# Change the directory
# cd site-model-app-deployment
# touch env.yaml

# Environment Variables for the app
# TO DO: In prodcution, change these values.
echo """
DB_NAME:
    '$APP_NAME-admin'
DB_USER:
    '$APP_NAME-admin'
DB_HOST:
    '$(gcloud compute instances list --filter="name=$DB_INSTANCE_NAME" --format="value(networkInterfaces[0].accessConfigs[0].natIP)")'
DB_PORT:
    '$DB_PORT'
DB_PASSWORD:
    '$DB_PASSWORD'
PROJECT_NAME:
    '$(gcloud config get project)'
ADMIN_PASSWORD:
    '$ADMIN_PASSWORD'
APP_PORT:
    '$APP_PORT'
APP_ADDRESS:
    '$APP_ADDRESS'
DOMAIN_NAME:
    '$DOMAIN_NAME'
SPECIAL_NAME:
    '$SPECIAL_NAME'
""" > .env.yaml


# Deploy the app using Cloud Run
gcloud run deploy $APP_NAME \
    --max-instances=$MAX_INSTANCES --min-instances=$MIN_INSTANCES --port=$APP_PORT \
    --env-vars-file=$APP_ENV_FILE \
    --image=$REGION-docker.pkg.dev/$(gcloud config get project)/$APP_ARTIFACT_NAME/$APP_NAME:$APP_VERSION \
    --allow-unauthenticated \
    --region=$REGION \
    --service-account=$APP_SERVICE_ACCOUNT_NAME@$(gcloud config get project).iam.gserviceaccount.com 
echo "\n #----------The application has been successfully deployed.----------# \n"



