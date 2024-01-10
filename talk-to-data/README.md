# Talk to your Data

This repo includes a demonstration example for building chat & search apps using Google Cloud Vertex AI & Langchain. 

You'll have the option to build one of the below apps:

- Chatbot app on your documents using [Streamlit](https://streamlit.io/). Components include Vertex AI (Embeddings, Search, PaLM), Google Cloud SQL and Langchain.

- Video search app using [Flask](https://flask.palletsprojects.com/en/3.0.x/). Components include Vertex AI (Embeddings, Gemini, Video Intelligence), Google Cloud SQL and Langchain.

To build and run an app, you'll need to follow the below 3 steps:

1.  Backend: Create a vector database to store documents content and embeddings

2.  Backend: Build and run the document processing or video processing job in `talk-to-data/process`

3.  Frontend : Build and run the UI as described in `talk-to-data/chat` or `talk-to-data/search`


All jobs and apps can be deployed locally or on Google Cloud Run. 

We're assuming that you have already an access to a GCP Project and environment.


# Step 1 - Backend - Vector Database

Create a Cloud SQL database instance in Google Cloud. In this example, we will use PostgreSQL.

```bash
gcloud sql instances create {instance_name} --database-version=POSTGRES_15 \
    --region={region} --cpu=4 --memory=4GB --root-password={database_password}
```

# Step 2 - Backend - Data Processing

Please refer to `talk-to-data/process` section to complete this step. 
 

# Step 3 - Frontend UI

Please refer to `talk-to-data/chat` 
or `talk-to-data/search` 
sections to complete this step. 


