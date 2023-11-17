# Environment
export USER="matt" # DB_NAME
export DBPASSWORD="password"

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
    --name postgres-sql \
    -e POSTGRES_USER=$USER \
    -e POSTGRES_PASSWORD=$DBPASSWORD \
    -v $(pwd)/data/:/var/lib/postgresql/data/ \
    -p 5000:5432 \
    postgres
docker run -p 8000:80 \
    -e 'PGADMIN_DEFAULT_EMAIL=matt@example.com' \
    -e 'PGADMIN_DEFAULT_PASSWORD=password' \
    -d dpage/pgadmin4
