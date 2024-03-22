# Frontend - Video Search

Before building the video search app, a pre-requesite is to process your videos as described in `talk-to-videos/process`.

The objective now is to build a search app on top of your vector database The app will be using [Flask](https://flask.palletsprojects.com/en/3.0.x/). 

Before you start, ensure that you have cloned this repository and you are currently in the `talk-to-videos/search` folder. This should be now your active working directory for the rest of the commands in this repo.

## Setup your config

Update the `utils/config.py` file with your configuration details

You have the option to run the app from your local machine or on GCP.

## Option 1 - Run the Application locally

To run the app locally (on cloud shell), we need to perform the following steps:

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
    python main.py
```

The application will startup and you will be provided a locahost URL to the application.

## Option 2 - Run the App remotely on Google Cloud Run

To deploy the app in [Cloud Run](https://cloud.google.com/run/docs/quickstarts/deploy-container), you need to following the below steps:


  1. Edit the `deploy.sh` file to set your configuration, including the AR_REPO, JOB_NAME.  Other variables are optional as they can be set from the `utils/config.py` file.

  3. Build and deploy the service on Cloud Run by executing the following command:

```bash
    sh deploy.sh
```

On successful deployment, you will be provided a URL to the Cloud Run service. You can visit that in the browser to view the Cloud Run application that you just deployed. 

Congratulations! You've completed the video search app demo.