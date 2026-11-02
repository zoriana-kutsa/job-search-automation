import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


if __name__ == "__main__":
    service = get_gmail_service()
    result = service.users().messages().list(userId="me", maxResults=5).execute()
    for m in result.get("messages", []):
        msg = service.users().messages().get(
            userId="me", id=m["id"], format="metadata", metadataHeaders=["Subject"]
        ).execute()
        for h in msg["payload"]["headers"]:
            if h["name"] == "Subject":
                print(h["value"])