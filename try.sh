# Environment
# TO DO: In production, change the values to be more secure. 
export VERSION="vii" # Change this
export APP_NAME="app-prod-$VERSION" # change the value in production 
export DB_PASSWORD="password" # change the value in production 

export DB_CONTAINER_NAME="$APP_NAME-sql"
# export DB_NAME="$APP_NAME-admin"
export DB_USER="$APP_NAME-admin" 