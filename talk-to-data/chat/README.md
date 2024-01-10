# Frontend - Chatbot App

Before building the chat app, a pre-requesite is to process your documents as described in `talk-to-data/process`.

The objective now is to build a chatbot app on top of your vector database The app will be using [Streamlit](https://streamlit.io/). 

Before you start, ensure that you have cloned this repository and you are currently in the `talk-to-data/chat` folder. This should be now your active working directory for the rest of the commands in this repo.

## Setup your config

Update the `utils/config.py` file with your configuration details

You have the option to run the app from your local machine or on GCP.

## Option 1 - Run the Application locally

To run the Streamlit Application locally (on cloud shell), we need to perform the following steps:

1. Setup the Python virtual environment and install the dependencies:

    In Cloud Shell, execute the following commands:

```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
```

2. To run the application locally, execute the following command:

    In Cloud Shell, execute the following command:

```bash
    streamlit run app.py \
      --browser.serverAddress=localhost \
      --server.enableCORS=false \
      --server.enableXsrfProtection=false \
      --server.port 8080
```

The application will startup and you will be provided a URL to the application. Use Cloud Shell's [web preview](https://cloud.google.com/shell/docs/using-web-preview) function to launch the preview page. You may also visit that in the browser to view the application. 

## Option 2 - Run the App remotely on Google Cloud Run

To deploy the Streamlit Application in [Cloud Run](https://cloud.google.com/run/docs/quickstarts/deploy-container), you need to following the below steps:


  1. Edit the `deploy.sh` file to set your configuration, including the AR_REPO, JOB_NAME.  Other variables are optional as they can be set from the `utils/config.py` file.

  3. Build and deploy the service on Cloud Run by executing the following command:

```bash
    sh deploy.sh
```

On successful deployment, you will be provided a URL to the Cloud Run service. You can visit that in the browser to view the Cloud Run application that you just deployed. 

Congratulations! You've completed the chat app building.