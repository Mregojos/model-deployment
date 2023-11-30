#----------Enable Artifact Registry, Cloud Build, and Cloud Run, Vertex AI
# gcloud services list --available
gcloud services enable compute.googleapis.com iam.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com run.googleapis.com aiplatform.googleapis.com cloudresourcemanager.googleapis.com
echo "\n #----------Services have been successfully enabled.----------# \n"

# Directory
cd app-deployment

# Create a Custom VPC
if gcloud compute networks list | grep -q $VPC_NAME; then
    echo "VPC already exists"
else
    gcloud compute networks create $VPC_NAME --subnet-mode=custom
fi

# Create subnets
if gcloud compute networks subnets list | grep -q $SUBNET_NAME-$REGION; then
    echo "Subnet already exists"
else
    gcloud compute networks subnets create $SUBNET_NAME-$REGION --network=$VPC_NAME --range=$RANGE_A --region=$REGION
fi

# Create subnets
if gcloud compute networks subnets list | grep -q $SUBNET_NAME-$CLOUD_BUILD_REGION; then
    echo "Subnet already exists"
else
    gcloud compute networks subnets create $SUBNET_NAME-$CLOUD_BUILD_REGION --network=$VPC_NAME --range=$RANGE_B --region=$CLOUD_BUILD_REGION
fi

# Create subnets
if gcloud compute networks subnets list | grep -q $SUBNET_NAME-$NOTEBOOK_REGION; then
    echo "Subnet already exists"
else
    gcloud compute networks subnets create $SUBNET_NAME-$NOTEBOOK_REGION --network=$VPC_NAME --range=$RANGE_C --region=$NOTEBOOK_REGION
fi


# Create a static external ip address
if gcloud compute addresses list | grep -q $STATIC_IP_ADDRESS_NAME; then
    echo "Address already exists"
else
    gcloud compute addresses create $STATIC_IP_ADDRESS_NAME --region $REGION
    echo "\n #----------Static IP Address has been successfully created.----------# \n"
fi


# Make a bucket
if gcloud storage buckets list | grep -q $BUCKET_NAME; then
    echo "Bucket already exists"
else
    gcloud storage buckets create gs://$BUCKET_NAME
    echo "\n #----------The bucket has been successfully created.---------- # \n"
fi

# Startup-script.sh
# touch startup-script.sh
# Change the version
# using sed: sed -i 's/<TEXT>/<NEW TEXT/g' <FILE>
sed -i s/VERSION=".*"/VERSION=\""$VERSION"\"/g startup-script.sh
sed -i s/APP_NAME=".*"/APP_NAME=\""$APP_NAME"\"/g startup-script.sh
sed -i s/DB_PASSWORD=".*"/DB_PASSWORD=\""$DB_PASSWORD"\"/g startup-script.sh

# Copy the file to Cloud Storage
# gcloud storage cp startup-script.sh gs://$BUCKET_NAME
# echo "\n #----------Startup script has been successfully copied.----------# \n"


#----------Use this service account only for deployment development ans use the custom service account for production----------#
# Create a service account
if gcloud iam service-accounts list | grep -q $STARTUP_SCRIPT_BUCKET_SA; then
    echo "Bucket Service Account already exists"
else
    gcloud iam service-accounts create $STARTUP_SCRIPT_BUCKET_SA
    echo "\n #----------Bucket Service Account has been successfully created.----------# \n"
fi
