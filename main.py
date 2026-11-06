import json
import os
import time
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


def append_with_retry(ws, rows):
    for attempt in range(3):
        try:
             ws.append_rows(
                rows,
                value_input_option="USER_ENTERED",
                insert_data_option="INSERT_ROWS",
            )
            return True
        except Exception as e:
            print(f"Sheets write attempt {attempt + 1} failed: {type(e).__name__}")
            time.sleep(10)
    return False


def main():
    sa_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if sa_json:
        gc = gspread.service_account_from_dict(json.loads(sa_json))
    else:
        gc = gspread.service_account(filename="service_account.json")
    gc.set_timeout(60)
    ws = gc.open_by_key(os.getenv("SPREADSHEET_ID")).sheet1
    existing = {u.split("?")[0] for u in ws.col_values(8)[1:]}

    added = 0
    for text in fetch_email_texts(days=4):
        rows = []
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
            rows.append([
                str(date.today()), v.get("title", ""), v.get("company", ""),
                v.get("location", ""), score, v.get("fit", ""), v.get("reason", ""),
                url, detect_source(url), "Нова",
            ])
        if rows and append_with_retry(ws, rows):
            added += len(rows)
    print(f"Added {added} new vacancies")


if __name__ == "__main__":
    main()