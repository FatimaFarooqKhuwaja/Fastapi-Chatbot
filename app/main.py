import os
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"

app = FastAPI(title="Fatima AI Chatbot API")

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return {"message": "Fatima AI Chatbot API running"}

@app.post("/chat")
def chat(request: ChatRequest):
    # Yahan HTTP request send karna Gemini API ko
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
    payload = {
        "model": "gemini-2.0-flash",
        "messages": [{"role": "user", "content": request.message}]
    }
    response = httpx.post(GEMINI_URL, headers=headers, json=payload)
    data = response.json()
    # Gemini response ko return karo
    return {"response": data.get("choices", [{"message": {"content": "Error"}}])[0]["message"]["content"]}