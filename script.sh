# using sed: sed -i 's/<TEXT>/<NEW TEXT/g' <FILE>
sed -i s/VERSION=".*"/VERSION=\""$VERSION"\"/g startup-script.sh
sed -i s/APP_NAME=".*"/APP_NAME=\""$APP_NAME"\"/g startup-script.sh
sed -i s/DB_PASSWORD=".*"/DB_PASSWORD=\""$DB_PASSWORD"\"/g startup-script.sh
sed -i s/ADMIN_PASSWORD=".*"/ADMIN_PASSWORDD=\""$ADMIN_PASSWORD"\"/g startup-script.sh