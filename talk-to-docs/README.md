# Talk to your Documents

This repo includes a demonstration example for building a `Chatbot app` on your documents using Google Cloud Vertex AI & Langchain. Components include Vertex AI (Embeddings, Search, PaLM), Google Cloud SQL, Langchain and [Streamlit](https://streamlit.io/).


To build and run an app, you'll need to follow the below steps:

All jobs and apps can be deployed locally or on Google Cloud Run. 

We're assuming that you have already setup an access to a GCP Project and environment.

## Step 1 - Backend - Vector Database

Create a Cloud SQL database instance in Google Cloud. In this example, we will use PostgreSQL.

```bash
gcloud sql instances create {instance_name} --database-version=POSTGRES_15 \
    --region={region} --cpu=4 --memory=4GB --root-password={database_password}
```

## Step 2 - Create GCS Bucket

Create 2 buckets: {docs_bucket} for your source document files The bucket names must have a unique URI. Check [documentation here](https://cloud.google.com/sdk/gcloud/reference/storage/buckets/create).

```bash
gcloud storage buckets create gs://{docs_bucket}
```

Copy your document files into the {docs_bucket}. Check [documentation here](https://cloud.google.com/sdk/gcloud/reference/storage/cp).

```bash
gcloud storage cp *.html gs://{docs_bucket}
```

## Step 3 - Backend - Data Processing

Please refer to `talk-to-docs/process` section to complete this step. 
 

## Step 4 - Frontend UI

Please refer to `talk-to-docs/chat` section to complete this step. 


