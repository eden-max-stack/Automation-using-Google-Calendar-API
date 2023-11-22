import datetime as dt
import os.path
import app

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]

template_id = ""
events = []

def get_event(event_list):
    for i in range(len(event_list)):
        events.append(event_list[i])

def add(events):
    creds = None
    
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        event = {}
        
        app.added(template_id)

        #for event in events:
         #   print(event)

        for event in events:
            event = service.events().insert(calendarId="primary", body=event).execute()

        print(f"event created {event.get('htmlLink')}")
    except HttpError as error:
        print("error", error)
        event = {}

        app.added(template_id)

        for event in events:
            print(event)


if __name__ == "__main__":
    add(events)