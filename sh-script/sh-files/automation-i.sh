# Infrastructure Automation using Shell Scripting and gcloud CLI

# Environment Variables
DB_NAME="db"
MACHINE_TYPE="e2-micro"
REGION="us-west1"
ZONE="us-west1-a"
BOOT_DISK_SIZE="30"
TAGS="db"
FIREWALL_RULES_NAME="ports"
STATIC_IP_ADDRESS_NAME="db-static-ip-address"
CLOUD_BUILD_REGION="us-west2"
APP_ARTIFACT_NAME="app"
APP_NAME="app"
APP_VERSION="latest"
APP_SERVICE_ACCOUNT_NAME='app-service-account'
echo "#----------Exporting Environment Variables is done.----------#"

# Create a static external ip address
gcloud compute addresses create $STATIC_IP_ADDRESS_NAME --region $REGION
echo "#----------Static IP Address has been successfully created.----------#"

# Print the Static IP Address
# gcloud compute addresses describe $STATIC_IP_ADDRESS_NAME --region $REGION | grep "address: " | cut -d " " -f2

# Create an instance with these specifications
gcloud compute instances create $DB_NAME \
    --machine-type=$MACHINE_TYPE --zone=$ZONE --tags=$TAGS \
    --boot-disk-size=$BOOT_DISK_SIZE \
    --no-scopes --no-service-account \
    --metadata-from-file=startup-script=startup-script.sh \
    --network-interface=address=$(gcloud compute addresses describe $STATIC_IP_ADDRESS_NAME --region $REGION | grep "address: " | cut -d " " -f2)
echo "#----------Compute Instance has been successfully created.----------#"

# Create a firewall (GCP)
gcloud compute --project=$(gcloud config get project) firewall-rules create $FIREWALL_RULES_NAME \
    --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:5000 --source-ranges=0.0.0.0/0 \
    --target-tags=$TAGS
echo "#----------Firewall Rules has been successfully created.----------#"

# Enable Artifact Registry, Cloud Build, and Cloud Run, Vertex AI
# !gcloud services list --available
gcloud services enable cloudbuild.googleapis.com artifactregistry.googleapis.com run.googleapis.com aiplatform.googleapis.com
echo "#----------Services has been successfully enabled.----------#"

# Create a Docker repository in Artifact Registry
gcloud artifacts repositories create $APP_ARTIFACT_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker repository"
echo "#----------Artifact Repository has been successfully created.----------#"

# Check if the path is correct
cd ..
cd app

# build and submnit an image to Artifact Registry
gcloud builds submit \
    --region=$CLOUD_BUILD_REGION \
    --tag $REGION-docker.pkg.dev/$(gcloud config get-value project)/$APP_NAME/$APP_NAME:$APP_VERSION
echo "#----------Docker image has been successfully built.----------#"

# For Cloud Run Deploy, use a Service Account with Cloud Run Admin
# For Clou Run Deployed Add (Service), use a Service Account with Vertex AI User or with custom IAM Role 
# Create IAM Service Account for the app
gcloud iam service-accounts create $APP_SERVICE_ACCOUNT_NAME
echo "#----------Service Account has been successfully created.----------#"

# Change the directory
cd ..
cd sh-files

# Deploy the app using Cloud Run
gcloud run deploy $APP_NAME \
    --max-instances=1 --min-instances=1 --port=9000 \
    --env-vars-file=env.yaml \
    --image=$REGION-docker.pkg.dev/$(gcloud config get project)/$APP_NAME/$APP_NAME:$APP_VERSION \
    --allow-unauthenticated \
    --region=$REGION \
    --service-account=$APP_SERVICE_ACCOUNT_NAME@$(gcloud config get project).iam.gserviceaccount.com 
echo "#----------The application has been successfully deployed.----------#"