#----------Local Development Environment Variables----------#
VERSION="ii"
APP_NAME="site-model-app-dev-$VERSION"
FIREWALL_RULES_NAME="ports"
INSTANCE_NAME="matt"

#----------Database Instance Environment Variables----------#
DB_INSTANCE_NAME="db"
MACHINE_TYPE="e2-micro"
REGION="us-west1"
ZONE="us-west1-a"
BOOT_DISK_SIZE="30"
TAGS="db"
FIREWALL_RULES_NAME="ports"
STATIC_IP_ADDRESS_NAME="db-static-ip-address"

#---------Database Credentials----------#
DB_CONTAINER_NAME='postgres-sql'
DB_NAME='matt'
DB_USER='matt' 
DB_HOST=$(gcloud compute instances list --filter="name=$INSTANCE_NAME" --format="value(networkInterfaces[0].accessConfigs[0].natIP)") 
DB_PORT=5000
DB_PASSWORD='password'
PROJECT_NAME='$(gcloud config get project)'
ADMIN_PASSWORD=password
APP_PORT=9000
APP_ADRESS=
DOMAIN_NAME=
SPECIAL_NAME='Matt'

#----------Deployment Environment Variables----------#
VERSION="ii"
APP_NAME="site-model-app-deployment-$VERSION"
CLOUD_BUILD_REGION="us-west2"
APP_ARTIFACT_NAME="app"
APP_VERSION="latest"
APP_SERVICE_ACCOUNT_NAME='app-service-account'
BUCKET_NAME='matt-startup-script'
STARTUP_SCRIPT_BUCKET_SA='startup-script-bucket-sa'
STARTUP_SCRIPT_NAME='startup-script.sh'
echo "\n #----------Exporting Environment Variables is done.----------# \n"

#----------Delete Resources----------#
gcloud compute instances delete $DB_INSTANCE_NAME --zone=$ZONE --quiet