from datetime import datetime, timezone
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.cloud import secretmanager
import json
import os

def get_secret(secret_id):
    """Get secret from Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.environ.get('PROJECT_ID', 'next-2025-ces')  # Fallback to your project
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

def get_calendar(request):
    """Cloud Function to get next calendar appointments.
    Requires:
    - Service account credentials in Secret Manager
    - Calendar to be shared with the service account email
    - Calendar ID to be provided (or stored in environment)
    """
    try:
        # Get calendar ID from request or environment
        calendar_id = request.args.get('calendar_id') or os.environ.get('CALENDAR_ID')
        if not calendar_id:
            return json.dumps({'error': 'Calendar ID is required. Either provide it as a parameter or set CALENDAR_ID environment variable.'}), 400, {'Content-Type': 'application/json'}

        # Get service account credentials from Secret Manager
        service_account_key = json.loads(get_secret('CALENDAR_SERVICE_ACCOUNT'))
        
        # Create credentials from service account
        credentials = service_account.Credentials.from_service_account_info(
            service_account_key,
            scopes=['https://www.googleapis.com/auth/calendar.readonly']
        )

        # Build the service
        service = build('calendar', 'v3', credentials=credentials)

        # Get the next event
        now = datetime.now(timezone.utc)
        now_str = now.isoformat()
        
        # Look for the first valid event (has specific time and title)
        next_event = None
        page_token = None
        
        while True:
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=now_str,
                maxResults=10,
                singleEvents=True,
                orderBy='startTime',
                pageToken=page_token
            ).execute()
            
            for event in events_result.get('items', []):
                if ('dateTime' in event['start'] and  # This is a timed event, not an all-day event
                    event.get('summary')):  # Event has a title
                    # Parse event time and ensure it's timezone-aware
                    event_time = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                    if event_time > now:
                        next_event = event
                        break
            
            if next_event or not events_result.get('nextPageToken'):
                break
            page_token = events_result.get('nextPageToken')

        if not next_event:
            return json.dumps({'message': 'No upcoming events with time and title found.'}), 200, {'Content-Type': 'application/json'}
        
        start_time = next_event['start']['dateTime']
        # Format the date and time more nicely
        date_part = start_time.split('T')[0]
        time_part = start_time.split('T')[1].split('+')[0]
        formatted_start = f"{date_part} at {time_part}"

        response_data = {
            'summary': next_event.get('summary', 'No title'),
            'start': formatted_start,
            'location': next_event.get('location', 'No location specified'),
            'description': next_event.get('description', 'No description available')
        }

        return json.dumps(response_data), 200, {'Content-Type': 'application/json'}

    except Exception as e:
        error_message = f"Failed to get calendar events: {str(e)}"
        return json.dumps({'error': error_message}), 500, {'Content-Type': 'application/json'}


if __name__ == '__main__':
    # Example of local testing
    class MockRequest:
        def __init__(self, args):
            self.args = args

    # Test with calendar ID
    mock_request = MockRequest({'calendar_id': 'heiko.hotz@gmail.com'})  # Replace with your calendar ID
    print("\nTesting calendar access:")
    response, status_code, headers = get_calendar(mock_request)
    print(f"Status Code: {status_code}")
    print("Response:")
    print(response)

    # Test without calendar ID (should return error if not set in environment)
    mock_request_no_id = MockRequest({})
    print("\nTesting without calendar ID:")
    response, status_code, headers = get_calendar(mock_request_no_id)
    print(f"Status Code: {status_code}")
    print("Response:") 