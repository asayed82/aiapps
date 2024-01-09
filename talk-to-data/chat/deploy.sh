export PROJECT_ID='' 
export LOCATION=''
export DOCS_BUCKET=''
export DATA_STORE_ID=''
export DATA_STORE_REGION=''
export DOC_COLLECTION=''

AR_REPO='aidemos-repo' 
SERVICE_NAME='chat-wdocs-custom-app'


gcloud artifacts repositories create "$AR_REPO" --location="$LOCATION" --repository-format=Docker
gcloud auth configure-docker "$LOCATION-docker.pkg.dev"
gcloud builds submit --tag "$LOCATION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/$SERVICE_NAME"

gcloud run deploy "$SERVICE_NAME" \
  --port=8080 \
  --image="$LOCATION-docker.pkg.dev/$PROJECT_ID/$AR_REPO/$SERVICE_NAME" \
  --allow-unauthenticated \
  --region=$LOCATION \
  --platform=managed  \
  --project=$PROJECT_ID \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,LOCATION=$LOCATION,DOCS_BUCKET=$DOCS_BUCKET,DOC_COLLECTION=$DOC_COLLECTION