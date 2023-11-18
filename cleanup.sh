#----------Environment Variables----------#
VERSION="ii"
APP_NAME="site-model-app-dev-$VERSION"
FIREWALL_RULES_NAME="ports"
INSTANCE_NAME="matt"

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

#----------Delete Resources----------#
gcloud compute instances delete $DB_NAME --zone=$ZONE --quiet