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

app = FastAPI(title="Fatima AI Chatbot API")

# CORS (Next.js frontend ke liye)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"message": "Fatima AI Chatbot API running"}

@app.post("/chat")
async def chat_endpoint(payload: ChatRequest):
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message is empty")
    try:
        headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
        json_payload = {
            "model": "gemini-2.0-flash",
            "messages": [{"role": "user", "content": payload.message}]
        }
        response = httpx.post(GEMINI_URL, headers=headers, json=json_payload)
        data = response.json()
        return {"reply": data.get("choices", [{"message": {"content": "Error"}}])[0]["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))