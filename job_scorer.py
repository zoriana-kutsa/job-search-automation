import json
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()

MODELS = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.5-flash"]
UNAVAILABLE = set()

PROMPT = """You evaluate job vacancies for a candidate. Candidate skills: SQL, Power BI,
Excel, Python/pandas, AI, proofreading. Languages: Polish and Ukrainian.
Rules: contract must be umowa o prace or umowa zlecenia (B2B is NOT suitable).
Internship (staz) is OK. Any work schedule is OK. Roles that check AI answers are OK.

Below is the text of a job alert email. Extract all vacancies and return ONLY a JSON list.
Each item has fields: title, company, location, url, score (0-10), fit, reason, b2b_only.
b2b_only is true ONLY if the email says the contract is B2B and does not mention umowa o prace or umowa zlecenia; otherwise false.
If there are no vacancies, return [].

EMAIL:
"""


def score_email(text):
    time.sleep(4)
    for attempt in range(6):
        models = [m for m in MODELS if m not in UNAVAILABLE]
        if not models:
            print("All Gemini models are unavailable (quota or model not found). Stopping.")
            raise SystemExit(1)
        model = models[attempt % len(models)]
        try:
            response = client.models.generate_content(
                model=model,
                contents=PROMPT + text[:15000],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    max_output_tokens=8192,
                    temperature=0.2,
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            msg = str(e)
            print(f"Attempt {attempt + 1} ({model}) failed: {type(e).__name__}: {msg[:120]}")
            if "RESOURCE_EXHAUSTED" in msg or "NOT_FOUND" in msg:
                UNAVAILABLE.add(model)
                continue
            time.sleep(15 * (attempt + 1))
    return []