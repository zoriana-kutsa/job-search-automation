import os
from datetime import date

import gspread
from dotenv import load_dotenv

from gmail_reader import get_gmail_service
from job_scorer import get_body, score_email

load_dotenv()

MIN_SCORE = 6


def detect_source(url):
    for name in ["linkedin", "pracuj", "justjoin"]:
        if name in url.lower():
            return name
    return "other"


def main():
    gc = gspread.service_account(filename="service_account.json")
    ws = gc.open_by_key(os.getenv("SPREADSHEET_ID")).sheet1
    existing = {u.split("?")[0] for u in ws.col_values(8)[1:]}

    service = get_gmail_service()
    messages = service.users().messages().list(
        userId="me", q="newer_than:4d", maxResults=20
    ).execute().get("messages", [])

    new_rows = []
    for m in messages:
        msg = service.users().messages().get(userId="me", id=m["id"], format="full").execute()
        for v in score_email(get_body(msg["payload"])):
            url = v.get("url", "")
            key = url.split("?")[0]
            try:
                score = float(v.get("score", 0))
            except (TypeError, ValueError):
                score = 0
            if score < MIN_SCORE or not url or key in existing:
                continue
            existing.add(key)
            new_rows.append([
                str(date.today()), v.get("title", ""), v.get("company", ""),
                v.get("location", ""), score, v.get("fit", ""), v.get("reason", ""),
                url, detect_source(url), "Нова",
            ])

    if new_rows:
        ws.append_rows(new_rows, value_input_option="USER_ENTERED")
    print(f"Added {len(new_rows)} new vacancies")


if __name__ == "__main__":
    main()