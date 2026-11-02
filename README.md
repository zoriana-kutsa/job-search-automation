# Job Search Automation

Python project that automatically finds suitable job vacancies from email alerts, scores them with AI, and saves the best ones to Google Sheets. It runs 3 times a week on GitHub Actions, without paid tools.

## How it works

1. Reads job alert emails (LinkedIn, pracuj.pl, justjoin.it) from a separate Gmail inbox (IMAP).
2. Sends each email to the Gemini API with my criteria: skills, languages, contract type.
3. Gemini returns a JSON list of vacancies with `title`, `company`, `location`, `url`, `score` (0-10), `fit`, `reason`.
4. Keeps only vacancies with `score >= 6`.
5. Checks duplicates by URL, so the same vacancy is never added twice.
6. Writes new rows to Google Sheets with the status "Нова".

## Tech stack

Python, Gemini API, Gmail (IMAP), Google Sheets API (gspread), GitHub Actions.

## Project structure

- `main.py` - main script
- `imap_reader.py` - reads emails
- `job_scorer.py` - AI scoring with Gemini
- `.github/workflows/job-search.yml` - schedule (Mon, Wed, Fri)

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Create a `.env` file with `GEMINI_API_KEY`, `GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD`, `SPREADSHEET_ID`.
3. Add `service_account.json` for Google Sheets access.
4. Run: `python main.py`

For GitHub Actions, add the same values as repository secrets, plus `GOOGLE_SERVICE_ACCOUNT_JSON`.

## Notes

All keys are stored in `.env` and GitHub Secrets and are never uploaded to the repository.

I moved this project from Make to Python to remove credit limits and add duplicate check in code.