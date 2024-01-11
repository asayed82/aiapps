# Backend - Data Processing
 
The objective now is to process your data and store their embedding in a Vector Database.

Before we start, ensure that you have cloned this repository and you are currently in the `talk-to-videos/process` folder. This should be your active working directory for the rest of the commands in this repo.

## Setup your config

Update the `utils/config.py` file with your configuration details

## Prepare Videos

Gemini Vision Pro, the model we'll be using to generate video descriptions process the [first 2 minutes of videos](https://cloud.google.com/vertex-ai/docs/generative-ai/multimodal/send-multimodal-prompts#video-requirements).

If you have videos with longer than 2 minutes, you'll need to split them into clips by running the below script:

```bash
        python video_prep.py 
```

This script will take an input bucket of videos and create clips into an output bucket.

Once clips are created correctly, you'll be using the clips bucket as an input for the processing job. 

You have the option to run the job from your local machine or on GCP.

## Option 1 - Run the Processing Job locally

To run the job your local machine, you need to follow the below steps:

1. Setup the Python virtual environment and install the dependencies:

    In Cloud Shell, execute the following commands:

```bash
      python3 -m venv venv
      source venv/bin/activate
      pip install -r requirements.txt
```

  2. Run the job locally by executing the following command:

```bash
        python process.py 
```

## Option 2 - Run the Processing Job remotely on Google Cloud Run

To run the job on GCP, you need to follow the below steps:

1. Edit the `deploy.sh` file to set your configuration, including the AR_REPO, JOB_NAME.  Other variables are optional as they can be set from the `utils/config.py` file.

2. Build and run the job on Cloud Run by executing the following command:

```bash
        sh deploy.sh
```
