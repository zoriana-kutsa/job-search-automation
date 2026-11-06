import time
import base64
import json
import re

from dotenv import load_dotenv
from google import genai
from google.genai import types

from gmail_reader import get_gmail_service

load_dotenv()
client = genai.Client()

PROMPT = """You evaluate job vacancies for a candidate. Candidate skills: SQL, Power BI,
Excel, Python/pandas, AI, proofreading. Languages: Polish and Ukrainian.
Rules: contract must be umowa o prace or umowa zlecenia (B2B is NOT suitable).
Internship (staz) is OK. Any work schedule is OK. Roles that check AI answers are OK.

Below is the text of a job alert email. Extract all vacancies and return ONLY a JSON list.
Each item has fields: title, company, location, url, score (0-10), fit, reason.
If there are no vacancies, return [].

EMAIL:
"""


def get_body(payload):
    if payload.get("body", {}).get("data"):
        raw = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", "ignore")
        if payload.get("mimeType") == "text/html":
            raw = re.sub(r"<[^>]+>", " ", raw)
        return raw
    text = ""
    for part in payload.get("parts", []):
        text += get_body(part)
    return text


def score_email(text):
    time.sleep(4)
    for attempt in range(4):
        try:
            response = client.models.generate_content(
                model="gemini-flash-lite-latest",
                contents=PROMPT + text[:15000],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    max_output_tokens=8192,
                    temperature=0.2,
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {type(e).__name__}: {str(e)[:300]}")
            time.sleep(15 * (attempt + 1))
    return []


if __name__ == "__main__":
    service = get_gmail_service()
    result = service.users().messages().list(
        userId="me", q="newer_than:3d", maxResults=3
    ).execute()
    for m in result.get("messages", []):
        msg = service.users().messages().get(userId="me", id=m["id"], format="full").execute()
        vacancies = score_email(get_body(msg["payload"]))
        for v in vacancies:
            print(v["score"], v["title"], "|", v["company"])