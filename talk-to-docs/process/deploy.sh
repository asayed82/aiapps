export GCP_PROJECT_ID='noondev-chatbot'
export GCP_LOCATION='us-east1'
export DOCS_BUCKET='noongpt_training_data'

AR_REPO='aiapps-raghav'
JOB_NAME='process-job'
JOB_MEMORY='4Gi'
JOB_CPU=8
JOB_MAX_RETRIES=0
PROCESS_NUM_TASKS=20
TASK_TIMEOUT='300m'
SERVICE_ACCOUNT='rmundhada@noondev-chatbot.iam.gserviceaccount.com'
TASK_PARALLELISM=3

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

echo "Creating $JOB_NAME using $IMAGE_NAME"
gcloud run jobs create $JOB_NAME --execute-now \
    --image $IMAGE_NAME \
    --command python \
    --args process.py \
    --service-account=$SERVICE_ACCOUNT \
    --tasks $PROCESS_NUM_TASKS \
    --max-retries $JOB_MAX_RETRIES \
    --task-timeout $TASK_TIMEOUT \
    --parallelism $TASK_PARALLELISM \
    --cpu $JOB_CPU \
    --memory $JOB_MEMORY \
    --set-env-vars=DOCS_BUCKET=$DOCS_BUCKET








