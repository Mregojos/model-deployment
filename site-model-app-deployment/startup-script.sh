# Environment
# TO DO: In production, change the values to be more secure. 
export VERSION="viiii" # Change this
export APP_NAME="site-model-app-deployment-$VERSION"
export DB_CONTAINER_NAME="$APP_NAME-postgres-sql"
export DB_NAME="$APP_NAME-db"
export DB_USER="$APP_NAME-admin" 
export DB_PASSWORD='password' # change the value in production 

# docs.docker.com
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker

# Remove all running docker 
docker rm -f $(docker ps -aq)

# Create a database 
docker run -d \
    --name $DB_CONTAINER_NAME \
    -e POSTGRES_USER=$DB_USER \
    -e POSTGRES_PASSWORD=$DB_PASSWORD \
    -v $(pwd)/data/:/var/lib/postgresql/data/ \
    -p 5000:5432 \
    postgres
docker run -p 8000:80 \
    -e 'PGADMIN_DEFAULT_EMAIL=matt@example.com' \
    -e 'PGADMIN_DEFAULT_PASSWORD=password' \
    -d dpage/pgadmin4
