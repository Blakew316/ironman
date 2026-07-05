"""Read upcoming events from Google Calendar.

Credentials and token paths come from configuration. All Google API imports are
lazy and failures degrade gracefully to a spoken error message.
"""

import datetime
import os
import pickle
import re

from jarvis import config

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

_service = None


def authenticate_google():
    """Authenticate with the Google Calendar API and return a service handle."""
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    creds = None
    token_file = str(config.GOOGLE_TOKEN_FILE)
    if os.path.exists(token_file):
        with open(token_file, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(config.GOOGLE_CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(token_file, "wb") as token:
            pickle.dump(creds, token)

    return build("calendar", "v3", credentials=creds)


def get_events(n, service):
    """Return a spoken-style description of the next ``n`` calendar events."""
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    print(f"Getting the upcoming {n} events")
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=n,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
        e = "You have no events scheduled today."
        print(e)
        return e
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        match = re.findall(r"T([0-9][0-9]:[0-9][0-9]):[0-9][0-9]", start)
        when = match[0] if match else start
        e = "You have an event titled " + event["summary"] + " scheduled at " + when
        print(e)
        return e


def setupCalendar():
    """Authenticate once at startup, storing the service handle."""
    global _service
    try:
        _service = authenticate_google()
    except Exception as exc:
        print(f"[google_calendar] authentication failed: {exc}")
        _service = None


def startCalendar(n):
    """Return the next ``n`` events, or a friendly error message."""
    if _service is None:
        return "Calendar is not available."
    try:
        return get_events(n, _service)
    except Exception:
        return "Failed to get calendar data."


if __name__ == "__main__":
    setupCalendar()
    print(startCalendar(2))
