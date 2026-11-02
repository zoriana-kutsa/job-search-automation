import json
import os
from datetime import date

import gspread
from dotenv import load_dotenv

from imap_reader import fetch_email_texts
from job_scorer import score_email

load_dotenv()

MIN_SCORE = 6


def detect_source(url):
    for name in ["linkedin", "pracuj", "justjoin"]:
        if name in url.lower():
            return name
    return "other"


def main():
        sa_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if sa_json:
        gc = gspread.service_account_from_dict(json.loads(sa_json))
    else:
        gc = gspread.service_account(filename="service_account.json")
    ws = gc.open_by_key(os.getenv("SPREADSHEET_ID")).sheet1
    existing = {u.split("?")[0] for u in ws.col_values(8)[1:]}

    new_rows = []
    for text in fetch_email_texts(days=4):
        for v in score_email(text):
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