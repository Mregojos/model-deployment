VPC_TRY="vpc-try"
gcloud compute networks list | grep -a $VPC_TRY
if [ $? -eq 0 ]; then
    echo "VPC already exists"
else
    gcloud compute networks create $VPC_TRY --subnet-mode=custom
    echo "VPC created"
fi

BUCKET_TRY="matt-bucket-try-"
gcloud storage buckets list | grep -a $BUCKET_TRY
if [ $? -eq 0 ]; then
    echo "Bucket already exists"
else
    gcloud storage buckets create gs://$BUCKET_TRY
    echo "Bucket created"
fi
