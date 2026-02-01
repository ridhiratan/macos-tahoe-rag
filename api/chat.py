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

You have access to official Apple documentation about macOS Tahoe, plus your general knowledge about Apple and macOS.

Reference Documentation:
{context}

How to answer:
- First, use the documentation above if it contains relevant information.
- If the documentation doesn't fully cover the question, supplement with your general knowledge about macOS and Apple.
- For comparisons with older macOS versions, use your knowledge to provide helpful context.
- Be confident and helpful. Give direct, useful answers.
- If you truly don't know something specific, briefly acknowledge it but still try to be helpful.

If a question is completely unrelated to macOS or Apple, politely redirect to Tahoe-related topics.

FORMATTING:
- Break your response into short, digestible paragraphs (2-3 sentences each).
- Use blank lines between paragraphs for readability.
- For lists of features, steps, or items, use bullet points with "•" character.
- Keep bullet points concise (one line each when possible).
- No markdown symbols like #, **, or ```.
- No emojis.

Example format:
macOS Tahoe introduces the new Liquid Glass design language. This gives the interface a translucent, modern look across all system apps.

Key features include:
• Redesigned Control Center
• New Safari sidebar
• Improved Siri integration

The update is available for Macs from 2018 and later.

Tone: Confident, knowledgeable, and friendly."""


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
