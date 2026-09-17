# Customer Feedback Analyzer

A full-stack project that uses an LLM (Google Gemini) to perform sentiment analysis on customer reviews. Paste in a batch of reviews (e.g. Google reviews for a restaurant or any other business), and the app analyzes each one, shows aggregate insights, and lets you save the results for later.

## What it does

1. You paste in a list of customer reviews (one review per line).
2. Clicking **Analyze** sends each review to the FastAPI backend.
3. The backend calls the Gemini API to classify the review and returns:
   - **label** — `positive`, `negative`, or `neutral`
   - **score** — 1 (very bad) to 5 (very good)
   - **theme** — a one-word topic the review is mainly about (e.g. `delivery`, `price`, `service`, `quality`)
4. The app displays the per-review results in a table along with an aggregate summary (total reviews, average score, percentage positive, etc.).
5. Clicking **Save to database** stores the results in a local SQLite database so you can build up a history of past reports.

This mirrors a real business use case: a business owner can export their Google reviews to a text file, run them through this tool, and get quick, structured analytics instead of reading through reviews one by one.

## Architecture

- **Backend — `api.py`**: A FastAPI app exposing an `/analyze` endpoint. It takes a review's text, sends a prompt to the Gemini API, and uses a Pydantic schema (`Analysis`) to force the model's JSON response into a fixed shape (`label`, `score`, `theme`).
- **Frontend — `app.py`**: A Streamlit UI where users paste reviews, trigger analysis (looping over each review and calling the backend via `requests.post`), view results, and save them.
- **Database — `database.py`**: SQLite persistence (`feedback.db`) for saved analysis results, so past reports can be loaded again later. Also holds the developer-only `audit_log` table described below.

## Tech stack

- [FastAPI](https://fastapi.tiangolo.com/) — backend API
- [Google Gemini API](https://ai.google.dev/) (`google-genai`) — LLM-powered sentiment analysis
- [Pydantic](https://docs.pydantic.dev/) — request/response schema validation
- [Streamlit](https://streamlit.io/) — frontend UI
- [SQLite](https://www.sqlite.org/) — local storage for saved reports
- [uv](https://docs.astral.sh/uv/) — Python project & virtual environment management

## Setup

1. Install dependencies with `uv`:
   ```
   uv sync
   ```
2. Copy `.env.example` to `.env` and add your Gemini API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

`uv run` (used below) automatically uses the project's virtual environment, so there's no separate activation step.

## Running the project

Run everything through `python -m` rather than the `fastapi`/`streamlit` executables directly — on Windows, tools like Application Control / Smart App Control can block the standalone `.exe` wrappers that `uv` generates in `.venv\Scripts`, since they're freshly built and unsigned. Going through `python -m` avoids that.

**1. Start the backend** (in this directory):
```
uv run python -m uvicorn api:app --reload
```
This serves the API at `http://127.0.0.1:8000`. Leave it running.

**2. Start the frontend** (in a second terminal, same directory):
```
uv run python -m streamlit run app.py
```
This opens the app at `http://localhost:8501` in your browser.

> If a terminal reports the port is already in use, a previous `uvicorn` (or `streamlit`) process is still running in the background — stop it before starting a new one.

## Testing it out

1. In the Streamlit app, paste a few sample reviews into the text area, one per line, e.g.:
   ```
   The food was cold and delivery took forever.
   Great service, will come back again!
   Prices are a bit high for the portion size.
   ```
2. Click **Analyze**. You should see:
   - A results table with `label`, `score`, and `theme` for each review.
   - A summary with total reviews, average score, and percentage positive.
3. Click **Save to database** to persist the results to `feedback.db`.
4. Click **Load history** to see everything saved so far, including past runs.

You can also test the backend on its own via the interactive docs at `http://127.0.0.1:8000/docs`, using the `/analyze` endpoint's "Try it out" button.

## Audit log (developer-only)

`feedback.db` includes a second table, `audit_log`, that records any failure that happens while analyzing a review (e.g. the Gemini API returning an error, rate limits, malformed responses, network issues). This is **not** shown anywhere in the Streamlit UI — end users only ever see a generic "Failed to analyze review" message. The audit log exists purely so a developer can diagnose what actually went wrong.

Columns:
- **id** — auto-incrementing primary key
- **review** — the exact review text that failed to analyze
- **error** — the exact exception message raised, for debugging
- **timestamp** — when the error occurred (ISO 8601)

Every failure in `api.py`'s `/analyze` endpoint is caught and logged via `database.log_error(review, error)` before returning a generic 500 response to the caller.

To inspect it, either open `feedback.db` with a SQLite viewer (e.g. the "SQLite Viewer" VS Code extension) and look at the `audit_log` table, or query it directly:
```python
from database import load_audit_log
load_audit_log()
```
