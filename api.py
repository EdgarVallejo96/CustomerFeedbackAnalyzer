from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

from database import init_db, log_error

load_dotenv()
client = genai.Client()

app = FastAPI()
init_db()

# What the caller must SEND us
class Review(BaseModel):
    text: str

# What Gemini gives back, and what we SEND to the caller.
# We keep it small on purpose -> fewer tockens used.
class Analysis(BaseModel):
    label: str  # "positive", "negative", or "neutral"
    score: int  # 1 (very bad) to 5 (very good)
    theme: str  # one word: what the review is mainly about (e.g. "delivery")


@app.post("/analyze")
def analyze(review: Review):
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=(
                "Analyze this customer review.\n"
                "label must be 'positive', 'negative', or 'neutral'.\n"
                "score must be a number from 1 (very bad) to 5 (very good).\n"
                "theme must be ONE lowercase word for the main topic "
                "(for example: delivery, taste, price, service, quality).\n"
                f"Review: {review.text}"
            ),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=Analysis,
            ),
        )
        return response.parsed
    except Exception as e:
        log_error(review.text, str(e))
        raise HTTPException(status_code=500, detail="Failed to analyze review")