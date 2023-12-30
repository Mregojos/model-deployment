#----------Enable Artifact Registry, Cloud Build, and Cloud Run, Vertex AI----------#
# Directory
cd app-dev

# Directory
# cd app-deployment

# DB_HOST Static IP Address
DB_HOST=$(gcloud compute instances list --filter="name=$DB_INSTANCE_NAME" --format="value(networkInterfaces[0].accessConfigs[0].natIP)") 

# Environment Variables for the app
echo """DB_NAME=$DB_USER
DB_USER=$DB_USER 
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_PASSWORD=$DB_PASSWORD
PROJECT_NAME=$PROJECT_NAME
ADMIN_PASSWORD=$ADMIN_PASSWORD
APP_PORT=$APP_PORT
APP_ADRESS=$APP_ADDRESS
DOMAIN_NAME=$DOMAIN_NAME
SPECIAL_NAME=$SPECIAL_NAME
""" > .env.sh

# Remove docker container
# docker rm -f $APP_NAME

# Build
docker build -t $APP_NAME .

# Run
docker run -d -p 9000:9000 -v $(pwd):/app --env-file .env.sh --name $APP_NAME $APP_NAME

# Create a firewall (GCP)
if gcloud compute firewall-rules list --filter="name=$FIREWALL_RULES_NAME-dev" --format="table(name)" | grep -q $FIREWALL_RULES_NAME-dev; then
    echo ""
else
    gcloud compute --project=$(gcloud config get project) firewall-rules create $FIREWALL_RULES_NAME-dev \
        --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:9000 --source-ranges=0.0.0.0/0 
fi

# Remove docker container
# docker rm -f $APP_NAME

# Remove docker container all
# docker rm -f $(docker ps -aq)

# Remove the db data
# sudo rm -f data

# Docker exec
# docker exec -it $APP_NAME sh

echo "\n #----------DONE----------# \n"

