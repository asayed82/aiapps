# Backend - Data Processing
 
The objective now is to process your data and store their embedding in a Vector Database.

Before we start, ensure that you have cloned this repository and you are currently in the `talk-to-docs/process` folder. This should be your active working directory for the rest of the commands in this repo.

## Setup your config

Update the `utils/config.py` file with your configuration details

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
