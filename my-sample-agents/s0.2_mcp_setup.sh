#!/bin/bash

gcloud iam service-accounts create toolbox-identity
gcloud secrets create tools --data-file=server/mcp_toolbox/tools.yaml
export IMAGE=us-central1-docker.pkg.dev/database-toolbox/toolbox/toolbox:latest

gcloud run deploy toolbox \
--image $IMAGE \
--service-account toolbox-identity \
--region us-central1 \
--set-secrets "/app/tools.yaml=tools:latest" \
--args="--tools_file=/app/tools.yaml","--address=0.0.0.0","--port=8080" \
--allow-unauthenticated