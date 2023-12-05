#----------Delete Resources----------#
gcloud compute instances delete $DB_INSTANCE_NAME --zone=$ZONE --quiet
gcloud compute addresses delete $STATIC_IP_ADDRESS_NAME --region $REGION --quiet
gcloud compute firewall-rules delete $FIREWALL_RULES_NAME --quiet
gcloud artifacts repositories delete $APP_ARTIFACT_NAME --location=$REGION --quiet
gcloud run services delete $APP_NAME --region=$REGION --quiet
gcloud storage rm -r gs://$BUCKET_NAME
gcloud storage rm -r gs://$(gcloud config get project)_cloudbuild


# Remove IAM Policy Binding to the Bucket Service Account
# gcloud projects remove-iam-policy-binding \
#    $(gcloud config get project) \
#    --member=serviceAccount:$STARTUP_SCRIPT_BUCKET_SA@$(gcloud config get project).iam.gserviceaccount.com \
#    --role=roles/storage.objectViewer

# Remove IAM Policy Binding to the App Service Account
gcloud projects remove-iam-policy-binding \
    $(gcloud config get project) \
    --member=serviceAccount:$STARTUP_SCRIPT_BUCKET_SA@$(gcloud config get project).iam.gserviceaccount.com \
    --role=projects/$(gcloud config get project)/roles/$STARTUP_SCRIPT_BUCKET_CUSTOM_ROLE

gcloud iam service-accounts delete $STARTUP_SCRIPT_BUCKET_SA@$(gcloud config get project).iam.gserviceaccount.com --quiet

# Add IAM Policy Binding to the App Service Account
# gcloud projects remove-iam-policy-binding \
#    $(gcloud config get project) \
#    --member=serviceAccount:$APP_SERVICE_ACCOUNT_NAME@$(gcloud config get project).iam.gserviceaccount.com \
#    --role=roles/aiplatform.user

# Remove IAM Policy Binding to the App Service Account
gcloud projects remove-iam-policy-binding \
    $(gcloud config get project) \
    --member=serviceAccount:$APP_SERVICE_ACCOUNT_NAME@$(gcloud config get project).iam.gserviceaccount.com \
    --role=projects/$(gcloud config get project)/roles/$APP_CUSTOM_ROLE

gcloud iam service-accounts delete $APP_SERVICE_ACCOUNT_NAME@$(gcloud config get project).iam.gserviceaccount.com --quiet

#----------Requires Project Owner Permission----------#
# Delete
gcloud iam roles delete $STARTUP_SCRIPT_BUCKET_CUSTOM_ROLE \
    --project=$(gcloud config get project)

# Undelete
# gcloud iam roles undelete $STARTUP_SCRIPT_BUCKET_CUSTOM_ROLE \
#    --project=$(gcloud config get project)

# Delete
gcloud iam roles delete $APP_CUSTOM_ROLE \
    --project=$(gcloud config get project)

# Undelete
# gcloud iam roles undelete $APP_CUSTOM_ROLE \
#    --project=$(gcloud config get project) 

# Delete Subnets
gcloud compute networks subnets delete $SUBNET_NAME-$REGION --region=$REGION --quiet
gcloud compute networks subnets delete $SUBNET_NAME-$CLOUD_BUILD_REGION --region=$CLOUD_BUILD_REGION --quiet
gcloud compute networks subnets delete $SUBNET_NAME-$NOTEBOOK_REGION --region=$NOTEBOOK_REGION --quiet

# Delete Custom VPC
gcloud compute networks delete $VPC_NAME --quiet

# For Dev Firewall Rule
if gcloud compute firewall-rules list --filter="name=$FIREWALL_RULES_NAME-dev" --format="table(name)" | grep -q $FIREWALL_RULES_NAME-dev; then
    gcloud compute firewall-rules delete $FIREWALL_RULES_NAME-dev --quiet
# else
    # echo "$FIREWALL_RULES_NAME-dev Firewall Rule doesn't exist." 
fi

echo "\n #----------Services and Resources have been Successfully deleted.----------# \n"

echo "\n #----------DONE----------# \n"