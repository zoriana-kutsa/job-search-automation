import email
import imaplib
import os
import re
from datetime import date, timedelta

from dotenv import load_dotenv

load_dotenv()

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def get_text(msg):
    texts = []
    for part in msg.walk():
        ctype = part.get_content_type()
        if ctype not in ("text/plain", "text/html"):
            continue
        payload = part.get_payload(decode=True)
        if not payload:
            continue
        text = payload.decode(part.get_content_charset() or "utf-8", "ignore")
        if ctype == "text/html":
            text = re.sub(r"<[^>]+>", " ", text)
        texts.append(text)
    return "\n".join(texts)


def fetch_email_texts(days=4, limit=20):
    d = date.today() - timedelta(days=days)
    since = f"{d.day:02d}-{MONTHS[d.month - 1]}-{d.year}"
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(os.getenv("GMAIL_ADDRESS"), os.getenv("GMAIL_APP_PASSWORD"))
    mail.select("INBOX", readonly=True)
    _, data = mail.search(None, f'(SINCE "{since}")')
    texts = []
    for num in data[0].split()[-limit:]:
        _, msg_data = mail.fetch(num, "(BODY.PEEK[])")
        msg = email.message_from_bytes(msg_data[0][1])
        texts.append(get_text(msg))
    mail.logout()
    return texts