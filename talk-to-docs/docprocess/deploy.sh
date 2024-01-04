export GCP_PROJECT_ID='my-demo-project-359019'
export GCP_LOCATION='us-central1'
export INPUT_BUCKET='my-demo-project-359019-docprocess-test'
export TEST='MYTEST'

AR_REPO='aidemos-repo' 
JOB_NAME='docprocess-job'
IMAGE_NAME="$GCP_LOCATION-docker.pkg.dev/$GCP_PROJECT_ID/$AR_REPO/$JOB_NAME"


echo "Configure gcloud to use $GCP_LOCATION for Cloud Run"
gcloud config set run/region $GCP_LOCATION

echo "Enabling required services"
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com

echo "Creating Artifact Repository"
gcloud artifacts repositories create "$AR_REPO" --location="$GCP_REGION" --repository-format=Docker

echo "Auth Configure Docker"
gcloud auth configure-docker "$GCP_LOCATION-docker.pkg.dev"


echo "Building image into a container"
gcloud builds submit --tag $IMAGE_NAME


echo "Deleting job if it already exists"
gcloud run jobs delete $JOB_NAME --quiet

echo "Creating $JOB_NAME using $IMAGE_NAME, bucket $INPUT_BUCKET"
gcloud run jobs create $JOB_NAME --execute-now \
    --image $IMAGE_NAME \
    --command python \
    --args process.py \
    --set-env-vars=INPUT_BUCKET=$INPUT_BUCKET,TEST=$TEST








