import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import anthropic

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

app = FastAPI()

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = """You are an expert assistant for macOS Tahoe (also known as macOS 26).

Your role is to answer ONLY questions related to macOS Tahoe, its features, system behavior, UI changes, apps, settings, performance, compatibility, and release information.

Rules:
- If a question is not about macOS Tahoe, politely say that you only answer Tahoe-related questions.
- If you are unsure about something or lack reliable information, clearly say: "I don't have enough information about that yet."
- Do NOT guess or invent features.
- Do NOT mix information from older macOS versions unless explicitly asked to compare, and clearly label comparisons.
- Keep answers factual, concise, and user-friendly.
- When helpful, explain things step-by-step.
- If the user asks about future or rumored features, state that they are not confirmed.

Tone:
Helpful, calm, and technical when needed, but friendly for everyday users."""


class ChatRequest(BaseModel):
    message: str
    history: list = []


class ChatResponse(BaseModel):
    response: str


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")

    client = anthropic.Anthropic(api_key=api_key)

    # Build messages with history
    messages = []
    for msg in request.history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": request.message})

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages
        )
        return ChatResponse(response=response.content[0].text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Serve static files
static_path = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.get("/")
async def root():
    return FileResponse(static_path / "index.html")
