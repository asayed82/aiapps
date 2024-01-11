# Talk to your Documents

This repo includes a demonstration example for building a `Chatbot app` on your documents using Google Cloud Vertex AI & Langchain. Components include Vertex AI (Embeddings, Search, PaLM), Google Cloud SQL, Langchain and [Streamlit](https://streamlit.io/).


To build and run an app, you'll need to follow the below 3 steps:

1.  `Backend`: Create a vector database to store documents content and embeddings

2.  `Backend`: Build and run the document processing job in `talk-to-docs/process`

3.  `Frontend` : Build and run the UI as described in `talk-to-docs/chat`


All jobs and apps can be deployed locally or on Google Cloud Run. 

We're assuming that you have already setup an access to a GCP Project and environment.

## Step 1 - Backend - Vector Database

Create a Cloud SQL database instance in Google Cloud. In this example, we will use PostgreSQL.

```bash
gcloud sql instances create {instance_name} --database-version=POSTGRES_15 \
    --region={region} --cpu=4 --memory=4GB --root-password={database_password}
```

## Step 2 - Backend - Data Processing

Please refer to `talk-to-docs/process` section to complete this step. 
 

## Step 3 - Frontend UI

Please refer to `talk-to-docs/chat` section to complete this step. 


