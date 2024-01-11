export PROJECT_ID='' 
export LOCATION='us-central1'
export CLIPS_BUCKET=''
export VIDEO_COLLECTION=''

AR_REPO='aidemos-repo' 
SERVICE_NAME='video-search-app'
MEMORY='4Gi'
CPU=8


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
  --cpu $CPU \
  --memory $MEMORY \
  --set-env-vars=PROJECT_ID=$PROJECT_ID,LOCATION=$LOCATION,CLIPS_BUCKET=$CLIPS_BUCKET,VIDEO_COLLECTION=$VIDEO_COLLECTION