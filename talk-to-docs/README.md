# Use Case: Talk to your Documents

This repo includes an example for building chat & search apps using Vertex AI PaLM-2 model with Langchain and Vertex AI Search. The chat app will be deployed on Google Cloud Run using [Streamlit](https://streamlit.io/), while the search app will be deployed on Gogle Cloud Run using Flask (Coming soon). 

To build and run the app, you'll need to follow the below 2 steps:

1.  Backend: Build and run the document processing job in `talk-to-docs/docprocess`
2.  Frontend : Build and run the chat app in `talk-to-docs/chat`

These are 2 different apps that need to be executed separately. Both apps can be executed either locally or on GCP.

# Backend - Document Processing
 
 First step is to process documents and store their embedding in a Vector Database.

 Additionally, ensure that you have cloned this repository and you are currently in the `talk-to-docs/docprocess` folder. This should be your active working directory for the rest of the commands for this Backend section (Document Processing).

## Run the Job locally

To run the job your local machine, you need to follow the below steps:

1. Setup the Python virtual environment and install the dependencies:

    In Cloud Shell, execute the following commands:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
  ```

  2.  Update the `utils/config.py` file with your configuration details

  3. Run the job locally by executing the following command:

    ```bash
    python process.py 
    ```

## Run the Job on GCP

To run the job on GCP, you need to run the `deploy.sh` file. Edit the file first to change included parameters.
It's mandatory to set your AR_REPO, JOB_NAME parameters. The other parameters are optional as they will be set from the `utils/config.py` file.

  1.  Update the `utils/config.py` file with your configuration details

  2. Build and run the job on GCP by executing the following command:

    ```bash
    sh deploy.sh
    ```

# Frontend - Chat App
## Run the Application locally

Before you start, ensure that you have cloned this repository and you are currently in the `talk-to-docs/chat` folder. This should be now your active working directory for the rest of the commands for this Frontend section (Chat App).

To run the Streamlit Application locally (on cloud shell), we need to perform the following steps:

1. Setup the Python virtual environment and install the dependencies:

    In Cloud Shell, execute the following commands:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2. Update the `utils/config.py` file with your configuration details


3. To run the application locally, execute the following command:

    In Cloud Shell, execute the following command:

    ```bash
    streamlit run app.py \
      --browser.serverAddress=localhost \
      --server.enableCORS=false \
      --server.enableXsrfProtection=false \
      --server.port 8080
    ```

The application will startup and you will be provided a URL to the application. Use Cloud Shell's [web preview](https://cloud.google.com/shell/docs/using-web-preview) function to launch the preview page. You may also visit that in the browser to view the application. Choose the functionality that you would like to check out and the application will prompt the Vertex AI PaLM-2 API with your Vector Database and display the responses.

## Build and Deploy the Application to Cloud Run


To deploy the Streamlit Application in [Cloud Run](https://cloud.google.com/run/docs/quickstarts/deploy-container), you need to following the below steps:


  1.  Update the `utils/config.py` file with your configuration details

  2. Edit `deploy.sh` file first to change included parameters.It's mandatory to set your AR_REPO, JOB_NAME parameters. The other parameters are optional as they can be set by default from the `utils/config.py` file.

  3. Build and Run the job on GCP Cloud Run by executing the following command:

    ```bash
    sh deploy.sh
    ```

On successful deployment, you will be provided a URL to the Cloud Run service. You can visit that in the browser to view the Cloud Run application that you just deployed. 

Congratulations!