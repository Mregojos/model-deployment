#----------Enable Artifact Registry, Cloud Build, and Cloud Run, Vertex AI
# gcloud services list --available
gcloud services enable compute.googleapis.com iam.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com run.googleapis.com aiplatform.googleapis.com cloudresourcemanager.googleapis.com
echo "\n #----------Services have been successfully enabled.----------# \n"

# Directory
cd app-deployment

#----------Database Instance Section----------#
# Create a Custom VPC
gcloud compute networks create $VPC_NAME --subnet-mode=custom

# Create subnets
gcloud compute networks subnets create $SUBNET_NAME-$REGION --network=$VPC_NAME --range=$RANGE_A --region=$REGION
gcloud compute networks subnets create $SUBNET_NAME-$CLOUD_BUILD_REGION --network=$VPC_NAME --range=$RANGE_B --region=$CLOUD_BUILD_REGION
gcloud compute networks subnets create $SUBNET_NAME-$NOTEBOOK_REGION --network=$VPC_NAME --range=$RANGE_C --region=$NOTEBOOK_REGION

# Create a static external ip address
gcloud compute addresses create $STATIC_IP_ADDRESS_NAME --region $REGION
echo "\n #----------Static IP Address has been successfully created.----------# \n"

# Make a bucket
gcloud storage buckets create gs://$BUCKET_NAME
echo "\n #----------The bucket has been successfully created.---------- # \n"

# Startup-script.sh
# touch startup-script.sh
# Change the version
# using sed: sed -i 's/<TEXT>/<NEW TEXT/g' <FILE>
sed -i s/VERSION=".*"/VERSION=\""$VERSION"\"/g startup-script.sh
sed -i s/APP_NAME=".*"/APP_NAME=\""$APP_NAME"\"/g startup-script.sh
sed -i s/DB_PASSWORD=".*"/DB_PASSWORD=\""$DB_PASSWORD"\"/g startup-script.sh

# Copy the file to Cloud Storage
gcloud storage cp startup-script.sh gs://$BUCKET_NAME
echo "\n #----------Startup script has been successfully copied.----------# \n"

#----------Use this service account only for deployment development ans use the custom service account for production----------#
# Create a service account
gcloud iam service-accounts create $STARTUP_SCRIPT_BUCKET_SA
echo "\n #----------Bucket Service Account has been successfully created.----------# \n"

#----------To create a custom role. Use this in Production.----------#\
# To describe and list IAM Roles 
# gcloud iam roles describe roles/storage.objectUser

# Custom role needs Project Owner Role.
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

# Create an instance with these specifications
gcloud compute instances create $DB_INSTANCE_NAME \
    --machine-type=$MACHINE_TYPE --zone=$ZONE --tags=$TAGS \
    --boot-disk-size=$BOOT_DISK_SIZE \
    --service-account=$STARTUP_SCRIPT_BUCKET_SA@$(gcloud config get project).iam.gserviceaccount.com  \
    --metadata=startup-script-url=gs://$BUCKET_NAME/startup-script.sh \
    --network-interface=address=$(gcloud compute addresses describe $STATIC_IP_ADDRESS_NAME --region $REGION | grep "address: " | cut -d " " -f2),subnet=$SUBNET_NAME-$REGION
echo "\n #----------Compute Instance has been successfully created.----------# \n"

# Create a firewall rule (GCP)
gcloud compute --project=$(gcloud config get project) firewall-rules create $FIREWALL_RULES_NAME \
    --direction=INGRESS --priority=1000 --network=$VPC_NAME --action=ALLOW --rules=tcp:5000,tcp:8000 --source-ranges=0.0.0.0/0  # \
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

# DB_HOST Static IP Address
DB_HOST=$(gcloud compute instances list --filter="name=$DB_INSTANCE_NAME" --format="value(networkInterfaces[0].accessConfigs[0].natIP)") 

# Environment Variables for the app
echo """
DB_NAME:
    '$DB_NAME'
DB_USER:
    '$DB_USER'
DB_HOST:
    '$DB_HOST'
DB_PORT:
    '$DB_PORT'
DB_PASSWORD:
    '$DB_PASSWORD'
PROJECT_NAME:
    '$PROJECT_NAME'
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

echo "\n #----------DONE----------# \n"



