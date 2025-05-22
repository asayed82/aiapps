# Cloud Function Tools

This directory contains various tools that are deployed as Google Cloud Functions.

## Tools Overview

### Weather Tools
- **get-weather-tool**: Retrieves current weather data for a specified location
- **get-forecast-tool**: Provides 5-day weather forecast data for a specified location

### Calendar Tools
- **get-calendar-tool**: Retrieves next calendar appointments from a Google Calendar

## Prerequisites

1. **Google Cloud Project Setup**:
   ```bash
   # Set your project ID
   export PROJECT_ID=your-project-id
   gcloud config set project $PROJECT_ID
   ```

2. **Enable Required APIs**:
   ```bash
   gcloud services enable \
     cloudfunctions.googleapis.com \
     secretmanager.googleapis.com \
     calendar-json.googleapis.com
   ```

## Secret Management Setup

1. **Create Service Account for Functions**:
   ```bash
   # Create service account for weather functions
   gcloud iam service-accounts create weather-function-sa \
       --description="Service account for Weather Cloud Functions" \
       --display-name="Weather Function SA"

   # Create service account for calendar function
   gcloud iam service-accounts create calendar-function-sa \
       --description="Service account for Calendar Cloud Function" \
       --display-name="Calendar Function SA"
   ```

2. **Grant Secret Manager Access**:
   ```bash
   # Grant access to weather function service account
   gcloud projects add-iam-policy-binding $PROJECT_ID \
       --member="serviceAccount:weather-function-sa@$PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/secretmanager.secretAccessor"

   # Grant access to calendar function service account
   gcloud projects add-iam-policy-binding $PROJECT_ID \
       --member="serviceAccount:calendar-function-sa@$PROJECT_ID.iam.gserviceaccount.com" \
       --role="roles/secretmanager.secretAccessor"
   ```

3. **Store API Keys in Secret Manager**:
   ```bash
   # Store OpenWeather API key
   echo -n "your-openweather-api-key" | \
     gcloud secrets create OPENWEATHER_API_KEY \
     --data-file=- \
     --replication-policy="automatic"

   # Store Calendar service account key (after downloading from Google Cloud Console)
   gcloud secrets create CALENDAR_SERVICE_ACCOUNT \
     --data-file=path/to/service-account-key.json \
     --replication-policy="automatic"
   ```

## Weather Tools Setup

1. **Get OpenWeather API Key**:
   - Sign up at [OpenWeatherMap](https://openweathermap.org/api)
   - Get your API key
   - Store it in Secret Manager (see above)

2. **Deploy Weather Functions**:
   ```bash
   # Deploy get-weather function
   gcloud functions deploy get-weather-tool \
       --runtime python310 \
       --trigger-http \
       --entry-point=get_weather \
       --service-account="weather-function-sa@$PROJECT_ID.iam.gserviceaccount.com" \
       --source=cloud-functions/weather-tools/get-weather-tool \
       --region=us-central1

   # Deploy get-forecast function
   gcloud functions deploy get-forecast-tool \
       --runtime python310 \
       --trigger-http \
       --entry-point=get_forecast \
       --service-account="weather-function-sa@$PROJECT_ID.iam.gserviceaccount.com" \
       --source=cloud-functions/weather-tools/get-forecast-tool \
       --region=us-central1
   ```

## Calendar Tool Setup

1. **Create and Download Service Account Key**:
   - Go to Google Cloud Console > IAM & Admin > Service Accounts
   - Select calendar-function-sa
   - Keys > Add Key > Create New Key > JSON
   - Download the key file
   - Store it in Secret Manager (see above)

2. **Share Calendar with Service Account**:
   - Go to [calendar.google.com](https://calendar.google.com)
   - Find your calendar on the left
   - Settings and sharing > Share with specific people
   - Add the service account email (from the JSON key file)
   - Give "See all event details" permission

3. **Get Calendar ID**:
   - In the same settings page
   - Scroll to "Integrate calendar"
   - Copy your Calendar ID

4. **Deploy Calendar Function**:
   ```bash
   gcloud functions deploy get-calendar-tool \
       --runtime python310 \
       --trigger-http \
       --entry-point=get_calendar \
       --service-account="calendar-function-sa@$PROJECT_ID.iam.gserviceaccount.com" \
       --source=cloud-functions/calendar-tools/get-calendar-tool \
       --region=us-central1 \
       --set-env-vars CALENDAR_ID=your.calendar.id@gmail.com
   ```

## Testing the Functions

### Weather Functions
```bash
# Test get-weather with city
curl "https://YOUR_FUNCTION_URL/get-weather-tool?city=London"

# Test get-weather with coordinates
curl "https://YOUR_FUNCTION_URL/get-weather-tool?lat=51.5074&lon=-0.1278"

# Test get-forecast
curl "https://YOUR_FUNCTION_URL/get-forecast-tool?city=London"
```

### Calendar Function
```bash
# Test get-calendar (if CALENDAR_ID is set in environment)
curl "https://YOUR_FUNCTION_URL/get-calendar-tool"

# Test with specific calendar ID
curl "https://YOUR_FUNCTION_URL/get-calendar-tool?calendar_id=your.calendar@gmail.com"
```

## Project Structure
```
cloud-functions/
├── weather-tools/
│   ├── get-weather-tool/
│   │   ├── main.py
│   │   └── requirements.txt
│   └── get-forecast-tool/
│       ├── main.py
│       └── requirements.txt
└── calendar-tools/
    └── get-calendar-tool/
        ├── main.py
        └── requirements.txt
```

## Security Notes
- Never commit API keys or service account credentials to version control
- Use Secret Manager for all sensitive credentials
- Consider adding authentication to your Cloud Functions if needed
- Regularly rotate API keys and service account credentials
- Monitor function access logs for any suspicious activity 