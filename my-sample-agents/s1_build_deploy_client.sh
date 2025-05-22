#!/bin/bash
chmod +x *.sh


echo "============BUILDING ${DEMO_TYPE} AGENT CLIENT==========="

echo "********(5) STARTED Client Build..."
gcloud builds submit --config client/cloudbuild.yaml

echo "******** (6) STARTED Client Deploy..."
gcloud builds submit --config client/clouddeploy.yaml --substitutions=_DEMO_TYPE=$DEMO_TYPE,_BACKEND_URL=$BACKEND_URL
FRONTEND_URL=$(gcloud run services describe live-agent-ui-${DEMO_TYPE} --platform managed --region us-central1 --format 'value(status.url)')
echo $FRONTEND_URL

