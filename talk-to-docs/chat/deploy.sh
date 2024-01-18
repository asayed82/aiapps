export GCP_PROJECT_ID='noondev-chatbot'
export GCP_LOCATION='us-east1'
export DOCS_BUCKET='noongpt_training_data'
export DATA_STORE_ID=''
export DATA_STORE_REGION=''
export DOC_COLLECTION='openai_collection'

AR_REPO='aiapps-raghav'
SERVICE_NAME='noongpt-openai-raghav'


gcloud artifacts repositories create "$AR_REPO" --location="$LOCATION" --repository-format=Docker
gcloud auth configure-docker "$LOCATION-docker.pkg.dev"
gcloud builds submit --tag "$LOCATION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/$SERVICE_NAME"

gcloud run deploy "$SERVICE_NAME" \
  --port=8080 \
  --image="$LOCATION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/$SERVICE_NAME" \
  --service-account=$SERVICE_ACCOUNT \
  --allow-unauthenticated \
  --region=$LOCATION \
  --platform=managed  \
  --project=$PROJECT_ID \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,LOCATION=$LOCATION,DOCS_BUCKET=$DOCS_BUCKET,DOC_COLLECTION=$DOC_COLLECTION