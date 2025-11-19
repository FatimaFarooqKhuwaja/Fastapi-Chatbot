# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import httpx
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"

if not GEMINI_API_KEY:
    # If you want to rely ONLY on canned responses, you could remove this check.
    # But it's good to fail loudly if you expect model fallback to work.
    print("Warning: GEMINI_API_KEY not set. Model fallback will fail if reached.")

app = FastAPI(title="Fatima AI Chatbot API")

# CORS (dev: allow all; production: restrict to your frontend domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

# --- About-me tool (canned responses) ---
def about_me_tool(query: str) -> str:
    q = (query or "").lower()
    # check specific keyphrases - add more variants as you like
    if "who made you" in q or "who is your creator" in q or "who created you" in q or "who are you" in q:
        return (
            "Mujhe Fatima Farooq Khuwaja ne banaya hai. "
            "Woh ek talented Full Stack Developer, Python Expert aur Agentic AI Engineer hain. 😊"
        )
    if "who is fatima" in q or "tell me about fatima" in q or "tell me about fatima farooq" in q:
        return (
            "Fatima Farooq Khuwaja ek passionate Full Stack Engineer hain jo Next.js aur Python me kaam karte hain. "
            "Unhon ne 100+ websites develop ki hain — eCommerce, portfolios, blogs, aur zyada. "
            "Woh GIAIC ki student bhi hain."
        )
    # can add more canned responses
    if "about me" in q and "fatima" in q:
        return (
            "Fatima Farooq Khuwaja ek Full Stack Developer aur AI enthusiast hain. "
            "Unka kaam Next.js, Python aur agentic AI projects pe focused hai."
        )
    # default: no canned answer
    return ""

# --- Helper: call Gemini/OpenAI HTTP API (fallback) ---
async def call_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not configured for model fallback.")
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json",
    }

    # Adjust request format if your provider expects slightly different body.
    # This structure matches many chat completions endpoints.
    body = {
        "model": "gemini-2.0-flash",
        "messages": [{"role": "user", "content": prompt}],
        # add other params like temperature, max_tokens if supported
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(GEMINI_URL, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()

    # Try common response shapes gracefully
    # Many OpenAI-like responses have .choices[0].message.content
    try:
        # Guard for multiple shapes
        if isinstance(data, dict):
            # try OpenAI-like shape
            choices = data.get("choices")
            if choices and isinstance(choices, list):
                first = choices[0]
                # nested message content
                msg = first.get("message", {}).get("content")
                if msg:
                    return msg
                # or plain text
                txt = first.get("text")
                if txt:
                    return txt
            # some APIs return 'response' or other key
            if "response" in data:
                return data["response"]
        # fallback to stringified body
        return str(data)
    except Exception:
        return str(data)

@app.get("/")
async def root():
    return {"message": "Fatima AI Chatbot API running"}

@app.post("/chat")
async def chat_endpoint(payload: ChatRequest):
    msg = (payload.message or "").strip()
    if not msg:
        raise HTTPException(status_code=400, detail="Message is empty")

    # 1) Try rule-based canned answers first:
    canned = about_me_tool(msg)
    if canned:
        return {"reply": canned}

    # 2) Otherwise call the model (Gemini/OpenAI) as fallback
    try:
        ai_reply = await call_gemini(msg)
        return {"reply": ai_reply}
    except httpx.HTTPStatusError as e:
        # bubble HTTP errors with status
        raise HTTPException(status_code=502, detail=f"Model error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")



