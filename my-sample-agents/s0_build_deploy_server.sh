#!/bin/bash
chmod +x *.sh

export PROJECT_ID='my-project-id'
export PROJECT_NUMBER='my-project-number'
export LOCATION='us-central1'
export AGENTS_BUCKET='my-bucket'
export DB_INSTANCE_NAME='live-agents-db-instance'
export DEMO_TYPE='hr'

echo "============BUILDING ${DEMO_TYPE} AGENT SERVER==========="

echo "******** (1) STARTED Server Setup"
./s0.1_server_setup.sh

echo "******** (2) STARTED MCP Server Deploy"
./s0.2_mcp_setup.sh
export MCP_TOOLBOX_URL=$(gcloud run services describe toolbox  --platform managed --region us-central1 --format 'value(status.url)')

echo "******* (3) STARTED Server Build..."
gcloud builds submit --config server/cloudbuild.yaml

echo "******* (4) STARTED Server Deploy...."
gcloud builds submit --config server/clouddeploy.yaml --substitutions=_DEMO_TYPE=$DEMO_TYPE,_MCP_TOOLBOX_URL=$MCP_TOOLBOX_URL
export BACKEND_URL=$(gcloud run services describe live-agent-backend-${DEMO_TYPE}  --platform managed --region us-central1 --format 'value(status.url)')
echo $BACKEND_URL

