import requests
import json
import os
from datetime import datetime
from google.cloud import secretmanager

def get_secret(secret_id):
    """Get secret from Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.environ.get('PROJECT_ID', 'sokratis-genai-bb')
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

def get_forecast(request):
    """Responds to an HTTP request with 5-day weather forecast data."""

    # Get location from request parameters (e.g., city, lat/lon)
    city = request.args.get('city')
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if not city and not (lat and lon):
        return "Please provide either 'city' or 'lat' and 'lon' parameters.", 400

    try:
        api_key = get_secret('OPENWEATHER_API_KEY')
    except Exception as e:
        return f"Error fetching API key from Secret Manager: {e}", 500

    if not api_key:
        return "API key not configured.", 500

    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        'appid': api_key,
        'units': 'metric'  # Or 'imperial' for Fahrenheit
    }

    if city:
        params['q'] = city
    elif lat and lon:
        params['lat'] = lat
        params['lon'] = lon

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        forecast_data = response.json()

        # Process and format the forecast data
        processed_forecast = []
        for item in forecast_data['list']:
            # Convert timestamp to readable date
            dt = datetime.fromtimestamp(item['dt'])
            
            # Only include forecasts for 12:00 (noon)
            if dt.hour == 12:
                date_str = dt.strftime('%Y-%m-%d %H:%M:%S')

                forecast_item = {
                    "datetime": date_str,
                    "temperature": int((item['main']['temp'])),
                    "description": item['weather'][0]['description'],
                    "humidity": item['main']['humidity'],
                    # "wind_speed": item['wind']['speed'],
                    # "clouds": item['clouds']['all']
                }
                processed_forecast.append(forecast_item)

        # Construct the final response
        custom_forecast_response = {
            "city": forecast_data['city']['name'],
            "country": forecast_data['city']['country'],
            "forecasts": processed_forecast
        }

        return json.dumps(custom_forecast_response), 200, {'Content-Type': 'application/json'}

    except requests.exceptions.HTTPError as e:
        return f"Error from OpenWeatherMap API: {e}", e.response.status_code
    except requests.exceptions.RequestException as e:
        return f"Error connecting to OpenWeatherMap API: {e}", 500
    except Exception as e:
        return f"An unexpected error occurred: {e}", 500


if __name__ == '__main__':
    # Example of local testing
    class MockRequest:
        def __init__(self, args):
            self.args = args

    mock_request_city = MockRequest({'city': 'London'})
    mock_request_latlon = MockRequest({'lat': '51.5', 'lon': '-0.12'})

    city_forecast, status_city, headers_city = get_forecast(mock_request_city)
    print("Forecast for London:")
    print(city_forecast)

    latlon_forecast, status_latlon, headers_latlon = get_forecast(mock_request_latlon)
    print("\nForecast for Lat/Lon (London):")
    print(latlon_forecast) 