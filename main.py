from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
from dotenv import load_dotenv

# Load .env
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

app = FastAPI(title="Gemini Proxy + Soft UI Frontend")

# Allow CORS for testing/development (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend files from ./static
app.mount("/static", StaticFiles(directory="static"), name="static")


class AskRequest(BaseModel):
    prompt: str
    model: str = "gemini-2.5-flash"


@app.get("/")
def index():
    # Serve the SPA
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/ask")
def ask_gemini(req: AskRequest):
    """
    Proxy the request to the Google Generative Language API (Gemini).
    Reads API key from environment variable GOOGLE_API_KEY.
    """
    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Missing GOOGLE_API_KEY on server. Put it into a .env file or environment variables.",
        )

    url = f"https://generativelanguage.googleapis.com/v1/models/{req.model}:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": API_KEY}
    data = {"contents": [{"parts": [{"text": req.prompt}]}]}

    try:
        resp = requests.post(url, headers=headers, params=params, json=data, timeout=60)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Upstream request failed: {str(e)}")

    if resp.status_code == 200:
        try:
            result = resp.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            return {"status": "ok", "response": text}
        except Exception:
            # return raw JSON for debugging if structure isn't as expected
            return {"status": "ok", "response": "⚠️ No text response found.", "raw": resp.json()}
    else:
        # forward error details
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
