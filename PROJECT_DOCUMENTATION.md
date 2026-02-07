# macOS Tahoe RAG - Project Documentation

## Overview

**macOS Tahoe RAG** is a Retrieval-Augmented Generation (RAG) chatbot that provides accurate, sourced answers about macOS Tahoe (macOS 26). It combines web-scraped Apple documentation with AI-powered responses using Claude.

---

## Purpose

This project solves the problem of accessing fragmented information about macOS Tahoe by:

- Aggregating 25+ official Apple documentation sources
- Using vector-based semantic search with keyword boosting
- Leveraging Claude AI for intelligent response generation
- Providing source attribution for transparency and verification

**Use Cases:**
- Feature inquiries about macOS 26
- Compatibility questions
- Upgrade guides
- Troubleshooting assistance
- System settings and security information

---

## Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Core language |
| FastAPI | 0.115.0 | Web framework |
| Uvicorn | 0.30.6 | ASGI server |
| Anthropic | 0.77.0 | Claude API client |

### Vector Database & Search
| Technology | Purpose |
|------------|---------|
| ChromaDB | Vector storage and retrieval |
| FastEmbed | Lightweight embeddings (BAAI/bge-small-en-v1.5) |
| LangChain | RAG orchestration |
| LangChain-Chroma | ChromaDB integration |

### Data Ingestion
| Technology | Purpose |
|------------|---------|
| BeautifulSoup | Static page scraping |
| Playwright | Dynamic/JS-rendered page scraping |
| RecursiveCharacterTextSplitter | Document chunking |

### Frontend
| Technology | Purpose |
|------------|---------|
| HTML/CSS/JavaScript | Vanilla frontend (no frameworks) |
| Custom CSS | Dark theme with gradient UI |

### Deployment
| Platform | Method |
|----------|--------|
| Vercel | Python serverless |
| Heroku/Railway | Docker via Procfile |
| Local | Direct Python execution |

---

## Project Structure

```
macos-tahoe-rag/
├── api/
│   └── chat.py                 # FastAPI app with /api/chat endpoint
├── rag/
│   ├── __init__.py
│   ├── indexer.py              # Document loading, chunking, embedding
│   ├── retriever.py            # Hybrid search (semantic + keyword boosting)
│   └── chroma_db/              # Persisted vector database
├── scrapers/
│   ├── base.py                 # HTTP scraper for static pages
│   ├── support.py              # Playwright scraper for Apple Support
│   └── playwright.py           # Playwright scraper for Developer docs
├── static/
│   ├── index.html              # Chat UI
│   ├── script.js               # Client-side logic
│   └── style.css               # Styling
├── docs/                       # 25 text files (scraped documentation)
├── main.py                     # Local dev entry point
├── requirements.txt            # Python dependencies
├── Procfile                    # Heroku/Railway deployment config
├── vercel.json                 # Vercel deployment config
├── runtime.txt                 # Python version specification
└── .env                        # API key configuration (not committed)
```

---

## Application Flow

### Phase 1: Data Pipeline (Setup - One-time)

```
┌─────────────────────────────────────────────────────────────────┐
│                        WEB SCRAPING                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  scrapers/base.py          scrapers/support.py                  │
│  (Static pages)            (Apple Support - Playwright)         │
│       │                           │                             │
│       │    scrapers/playwright.py │                             │
│       │    (Developer docs)       │                             │
│       │           │               │                             │
│       └───────────┴───────────────┘                             │
│                   │                                             │
│                   ▼                                             │
│           docs/ folder                                          │
│         (25 .txt files)                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DOCUMENT INDEXING                            │
│                (python -m rag.indexer)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. LOAD         Read all .txt files from docs/                 │
│       │                                                         │
│       ▼                                                         │
│  2. CHUNK        Split into 1000-char chunks                    │
│       │          (200-char overlap)                             │
│       ▼                                                         │
│  3. EMBED        Generate vectors using FastEmbed               │
│       │          (BAAI/bge-small-en-v1.5)                       │
│       ▼                                                         │
│  4. STORE        Persist to ChromaDB                            │
│                  (rag/chroma_db/)                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 2: Runtime Flow (Chat)

```
┌──────────────────┐
│   User Query     │
│  "What are the   │
│   new features?" │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│                    FRONTEND (static/)                            │
│                                                                  │
│  index.html + script.js                                          │
│  - Captures user input                                           │
│  - Maintains conversation history                                │
│  - Shows typing indicator                                        │
│                                                                  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
                    POST /api/chat
                    {
                      "message": "What are new features?",
                      "history": [previous messages]
                    }
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                    BACKEND (api/chat.py)                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. RETRIEVE CONTEXT                                             │
│     └─► retriever.retrieve(query, k=5)                           │
│         ├─► Semantic similarity search (ChromaDB)                │
│         ├─► Keyword boosting for important terms                 │
│         └─► Return top 5 ranked chunks + sources                 │
│                                                                  │
│  2. BUILD PROMPT                                                 │
│     └─► Format context from retrieved chunks                     │
│     └─► Create system prompt with RAG context                    │
│                                                                  │
│  3. CALL CLAUDE API                                              │
│     └─► Send: system prompt + history + user message             │
│     └─► Model: claude-sonnet-4-20250514                           │
│                                                                  │
│  4. RETURN RESPONSE                                              │
│     └─► AI response + source list                                │
│                                                                  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                    FRONTEND DISPLAY                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  AI Response                                               │  │
│  │  "macOS Tahoe introduces Liquid Glass design..."           │  │
│  │                                                            │  │
│  │  ▼ Sources (click to expand)                               │  │
│  │    • announcement.txt                                      │  │
│  │    • whats_new_macos26.txt                                 │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Key Components

### 1. Hybrid Search (rag/retriever.py)

The retriever uses a hybrid approach combining:

- **Semantic Similarity**: ChromaDB vector search for contextual understanding
- **Keyword Boosting**: Extra weight for important macOS terms

```
Query: "liquid glass design"
    │
    ├─► Semantic Search (ChromaDB)
    │   Returns chunks by vector similarity
    │
    └─► Keyword Boost
        - +0.05 per query word match
        - +0.10 per important term ("liquid glass", "tahoe", "siri", etc.)
        - Max boost cap: 0.30
```

### 2. Document Chunking (rag/indexer.py)

```
Original Document (5000 chars)
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Chunk 1 │ Chunk 2 │ Chunk 3 │ Chunk 4 │ Chunk 5     │
│ 1000ch  │ 1000ch  │ 1000ch  │ 1000ch  │ 1000ch      │
└─────────────────────────────────────────────────────┘
     └──────┘
     200 char overlap (maintains context)
```

### 3. Conversation Management

- Maintains history of last 10 exchanges (20 messages max)
- Prevents context window overflow
- Enables multi-turn coherent conversations

---

## Documentation Coverage

The system includes 25 scraped documentation sources:

| Category | Files |
|----------|-------|
| **Release & Features** | announcement.txt, release_notes_26.txt, release_notes_26_1.txt, release_notes_26_2.txt, whats_new_updates.txt, whats_new_tahoe_guide.txt, whats_new_macos26.txt, macos_main.txt |
| **Compatibility** | compatible_computers.txt, how_to_upgrade.txt, enterprise_features.txt |
| **Troubleshooting** | battery_drain_fix.txt, battery_settings.txt, battery_condition.txt, battery_not_charging.txt, startup_issues.txt, diagnose_problems.txt, storage_mac.txt, slow_mac.txt, wifi_issues.txt |
| **System & Security** | system_settings.txt, security_content.txt, software_update.txt, time_machine.txt |

---

## Environment Setup

### Prerequisites
- Python 3.11+
- Anthropic API key

### Installation

```bash
# Clone repository
git clone <repo-url>
cd macos-tahoe-rag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Index documents (if not already done)
python -m rag.indexer

# Run locally
python main.py
```

### Deployment

**Vercel:**
```bash
vercel deploy
```

**Heroku/Railway:**
```bash
# Uses Procfile automatically
git push heroku main
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Main chat endpoint |
| `/api/health` | GET | Health check (returns RAG status) |
| `/` | GET | Serves static frontend |

### Chat Request Format
```json
{
  "message": "What are the new features in macOS Tahoe?",
  "history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"}
  ]
}
```

### Chat Response Format
```json
{
  "response": "macOS Tahoe introduces several new features...",
  "sources": ["announcement.txt", "whats_new_macos26.txt"]
}
```

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| **FastEmbed over PyTorch-based models** | Lightweight, enables serverless deployment |
| **Hybrid search** | Balances semantic understanding with keyword precision |
| **1000-char chunks with 200 overlap** | Preserves context while maintaining granularity |
| **Source attribution** | Builds user trust and enables verification |
| **Vanilla frontend** | No build step, simple deployment |

---

## Security Considerations

- System prompt includes guards against prompt injection
- Distinguishes documentation facts from general AI knowledge
- Avoids inventing features not in documentation
- API key stored in environment variables (never committed)

---

## License

MIT License - See LICENSE file for details.
