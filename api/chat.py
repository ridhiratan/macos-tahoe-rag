import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import anthropic

from rag.retriever import get_retriever

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

# Initialize retriever on startup
retriever = None


@app.on_event("startup")
async def startup_event():
    """Initialize the RAG retriever on startup."""
    global retriever
    try:
        retriever = get_retriever()
        retriever.initialize()
        print("RAG retriever initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize RAG retriever: {e}")
        print("Chat will work without RAG context")


SYSTEM_PROMPT = """You are an expert assistant for macOS Tahoe (also known as macOS 26).

Your role is to answer questions related to macOS Tahoe using the provided documentation context.

Context from Official Apple Documentation:
{context}

Rules:
- Use the provided context above to answer questions accurately.
- If a question is not about macOS Tahoe, politely say that you only answer Tahoe-related questions.
- If the context doesn't contain enough information, say you don't have enough information about that yet.
- Do NOT guess or invent features not mentioned in the documentation.
- Keep answers factual, concise, and user-friendly.

IMPORTANT FORMATTING RULES:
- Write in natural, conversational paragraphs only.
- Do NOT use any markdown formatting like headers (#), bullet points (-), bold (**), or emojis.
- Do NOT use lists or structured formatting.
- Write like you're having a friendly conversation, in flowing prose.
- Keep responses concise but informative.

Tone: Helpful, calm, and friendly - like a knowledgeable friend explaining things."""


class ChatRequest(BaseModel):
    message: str
    history: list = []


class ChatResponse(BaseModel):
    response: str
    sources: list = []


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")

    client = anthropic.Anthropic(api_key=api_key)

    # Retrieve relevant context using RAG
    context = "No documentation context available."
    sources = []

    if retriever and retriever._initialized:
        try:
            chunks = retriever.retrieve(request.message, k=5)
            context = retriever.format_context(chunks)
            sources = list(set(chunk["source"] for chunk in chunks))
        except Exception as e:
            print(f"RAG retrieval error: {e}")

    # Build system prompt with context
    system_prompt = SYSTEM_PROMPT.format(context=context)

    # Build messages with history
    messages = []
    for msg in request.history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": request.message})

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=system_prompt,
            messages=messages
        )
        return ChatResponse(
            response=response.content[0].text,
            sources=sources
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Health check endpoint
@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "rag_initialized": retriever._initialized if retriever else False
    }


# Serve static files
static_path = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.get("/")
async def root():
    return FileResponse(static_path / "index.html")
