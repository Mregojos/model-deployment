# Cloud Deployment

# Objective
# * To deploy a pre-trained model on GCP

#----------Enable Artifact Registry, Cloud Build, and Cloud Run, Vertex AI
# !gcloud services list --available
gcloud services enable iam.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com run.googleapis.com aiplatform.googleapis.com cloudresourcemanager.googleapis.com
echo "\n #----------Services have been successfully enabled.----------# \n"

# Environment Variables
DB_NAME="db"
MACHINE_TYPE="e2-micro"
REGION="us-west1"
ZONE="us-west1-a"
BOOT_DISK_SIZE="30"
TAGS="db"
FIREWALL_RULES_NAME="ports"
STATIC_IP_ADDRESS_NAME="db-static-ip-address"
INSTANCE_NAME="matt"

# Change the APP_NAME
VERSION="i"
APP_NAME="site-model-app-deployment-$VERSION"
CLOUD_BUILD_REGION="us-west2"
APP_ARTIFACT_NAME="app"
APP_VERSION="latest"
APP_SERVICE_ACCOUNT_NAME='app-service-account'
BUCKET_NAME='matt-startup-script'
STARTUP_SCRIPT_BUCKET_SA='startup-script-bucket-sa'
STARTUP_SCRIPT_NAME='startup-script.sh'
echo "\n #----------Exporting Environment Variables is done.----------# \n"

# Create a Docker repository in Artifact Registry
gcloud artifacts repositories create $APP_ARTIFACT_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker repository"
echo "\n #----------Artifact Repository has been successfully created.----------# \n"

# Change the directory
cd site-model-app-deployment

# build and submnit an image to Artifact Registry
gcloud builds submit \
    --region=$CLOUD_BUILD_REGION \
    --tag $REGION-docker.pkg.dev/$(gcloud config get-value project)/$APP_ARTIFACT_NAME/$APP_NAME:$APP_VERSION
echo "\n #----------Docker image has been successfully built.----------# \n"

# For Cloud Run Deploy, use a Service Account with Cloud Run Admin
# For Clou Run Deployed Add (Service), use a Service Account with Vertex AI User or with custom IAM Role 
# Create IAM Service Account for the app
gcloud iam service-accounts create $APP_SERVICE_ACCOUNT_NAME
echo "\n #----------Service Account has been successfully created.----------# \n"

# Add IAM Policy Binding to the App Service Account
gcloud projects add-iam-policy-binding \
    $(gcloud config get project) \
    --member=serviceAccount:$APP_SERVICE_ACCOUNT_NAME@$(gcloud config get project).iam.gserviceaccount.com \
    --role=roles/aiplatform.user
echo "\n #----------App Service Account has been successfully binded.----------# \n"

# Change the directory
cd site-model-app-deployment
# touch env.yaml

# Environment Variables for the app
echo """
DBNAME:
    'matt'
USER:
    'matt'
HOST:
    '$(gcloud compute instances list --filter="name=$INSTANCE_NAME" --format="value(networkInterfaces[0].accessConfigs[0].natIP)")'
DBPORT:
    '5000'
DBPASSWORD:
    'password'
PROJECT_NAME:
    '$(gcloud config get project)'
ADMIN_PASSWORD:
    'password'
APP_PORT:
    '9000'
""" > env.yaml


# Deploy the app using Cloud Run
gcloud run deploy $APP_NAME \
    --max-instances=1 --min-instances=1 --port=9000 \
    --env-vars-file=env.yaml \
    --image=$REGION-docker.pkg.dev/$(gcloud config get project)/$APP_ARTIFACT_NAME/$APP_NAME:$APP_VERSION \
    --allow-unauthenticated \
    --region=$REGION \
    --service-account=$APP_SERVICE_ACCOUNT_NAME@$(gcloud config get project).iam.gserviceaccount.com 
echo "\n #----------The application has been successfully deployed.----------# \n"



#----------Build and Run only----------#
# build and submnit an image to Artifact Registry
gcloud builds submit \
    --region=$CLOUD_BUILD_REGION \
    --tag $REGION-docker.pkg.dev/$(gcloud config get-value project)/$APP_ARTIFACT_NAME/$APP_NAME:$APP_VERSION
echo "\n #----------Docker image has been successfully built.----------# \n"

# Deploy the app using Cloud Run
gcloud run deploy $APP_NAME \
    --max-instances=1 --min-instances=1 --port=9000 \
    --env-vars-file=env.yaml \
    --image=$REGION-docker.pkg.dev/$(gcloud config get project)/$APP_ARTIFACT_NAME/$APP_NAME:$APP_VERSION \
    --allow-unauthenticated \
    --region=$REGION \
    --service-account=$APP_SERVICE_ACCOUNT_NAME@$(gcloud config get project).iam.gserviceaccount.com 
echo "\n #----------The application has been successfully deployed.----------# \n"