# Environment Variables
export DB_NAME="db"
export MACHINE_TYPE="e2-micro"
export REGION="us-west1"
export ZONE="us-west1-a"
export BOOT_DISK_SIZE="30"
export TAGS="db"
export FIREWALL_RULES_NAME="ports"
export STATIC_IP_ADDRESS_NAME="db-static-ip-address"
export CLOUD_BUILD_REGION="us-west2"
export APP_ARTIFACT_NAME="app"
export APP_NAME="app"
export APP_VERSION="latest"
export APP_SERVICE_ACCOUNT_NAME='app-service-account'
export BUCKET_NAME='matt-startup-script'
export STARTUP_SCRIPT_BUCKET_SA='startup-script-bucket-sa'
export STARTUP_SCRIPT_NAME='startup-script.sh'
echo "\n #----------Exporting Environment Variables is done.----------# \n"

gcloud compute instances delete $DB_NAME --zone=$ZONE --quiet
gcloud compute addresses delete $STATIC_IP_ADDRESS_NAME --region $REGION --quiet
gcloud compute firewall-rules delete $FIREWALL_RULES_NAME --quiet
gcloud artifacts repositories delete $APP_ARTIFACT_NAME --location=$REGION --quiet
gcloud run services delete $APP_NAME --region=$REGION --quiet
gcloud iam service-accounts delete $STARTUP_SCRIPT_BUCKET_SA@$(gcloud config get project).iam.gserviceaccount.com --quiet
gcloud iam service-accounts delete $APP_SERVICE_ACCOUNT_NAME@$(gcloud config get project).iam.gserviceaccount.com --quiet
gcloud storage rm -r gs://$BUCKET_NAME
gcloud storage rm -r gs://$(gcloud config get project)_cloudbuild
echo "\n #----------Services and Resources have been Successfully deleted.----------# \n"