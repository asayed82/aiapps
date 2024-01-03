export GCP_PROJECT='my-demo-project-359019' 
export GCP_REGION='us-central1'
export AR_REPO='aidemos-repo' 
export SERVICE_NAME='chat-wdocs-vais-app'
export DATA_STORE_ID='noon-all-clean-ds_1704263161829'
export PG_DRIVER='psycopg2'


gcloud artifacts repositories create "$AR_REPO" --location="$GCP_REGION" --repository-format=Docker
gcloud auth configure-docker "$GCP_REGION-docker.pkg.dev"
gcloud builds submit --tag "$GCP_REGION-docker.pkg.dev/$GCP_PROJECT/$AR_REPO/$SERVICE_NAME"

gcloud run deploy "$SERVICE_NAME" \
  --port=8080 \
  --image="$GCP_REGION-docker.pkg.dev/$GCP_PROJECT/$AR_REPO/$SERVICE_NAME" \
  --allow-unauthenticated \
  --region=$GCP_REGION \
  --platform=managed  \
  --project=$GCP_PROJECT \
  --set-env-vars=GCP_PROJECT=$GCP_PROJECT,GCP_REGION=$GCP_REGION,PG_DRIVER=$PG_DRIVER,DATA_STORE_ID=$DATA_STORE_ID