#!/bin/bash

gcloud config set project $PROJECT_ID

gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    iam.googleapis.com \
    sql-component.googleapis.com \
    aiplatform.googleapis.com \
    storage.googleapis.com


gcloud sql instances create ${DB_INSTANCE_NAME} --database-version=POSTGRES_15 \
    --region=${LOCATION} --cpu=4 --memory=4GB --root-password=postgres

gcloud sql databases create DATABASE_NAME \
    --instance=${DB_INSTANCE_NAME}

gcloud storage buckets create gs://${AGENTS_BUCKET}

gcloud iam service-accounts create live-agent-backend --display-name="Live Agent Backend Service Account"


gcloud projects add-iam-policy-binding $PROJECT_ID \
       --member="serviceAccount:live-agent-backend@${PROJECT_ID}.iam.gserviceaccount.com" \
       --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
       --member="serviceAccount:live-agent-backend@${PROJECT_ID}.iam.gserviceaccount.com" \
       --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
       --member="serviceAccount:live-agent-backend@${PROJECT_ID}.iam.gserviceaccount.com" \
       --role="roles/aiplatform.onlinePredictionServiceAgent"


gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
   --role="roles/run.developer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
   --member serviceAccount:toolbox-identity@$PROJECT_ID.iam.gserviceaccount.com \
   --role roles/cloudsql.client

gcloud secrets create GOOGLE_API_KEY --replication-policy="automatic"
echo -n "your-api-key" | gcloud secrets versions add GOOGLE_API_KEY --data-file=-

 #If using more APIs:
 #gcloud secrets create FINNHUB_API_KEY --replication-policy="automatic"
 #echo -n "your-api-key" | gcloud secrets versions add FINNHUB_API_KEY --data-file=-
