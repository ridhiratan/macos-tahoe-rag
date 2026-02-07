# macOS Tahoe RAG

A Retrieval-Augmented Generation (RAG) chatbot for answering questions about macOS Tahoe (macOS 26). Combines web-scraped Apple documentation with Claude AI to provide accurate, sourced information about features, compatibility, troubleshooting, and more.

## Features


- **Hybrid Search**: Combines semantic vector search with keyword boosting for accurate retrieval
- **Source Attribution**: Every response includes references to the source documentation
- **25+ Documentation Sources**: Scraped from Apple Support, Newsroom, and Developer docs
- **Modern Chat UI**: Dark-themed responsive interface with collapsible source panels
- **Multiple Deployment Options**: Local, Vercel, Heroku, or Railway

## Tech Stack

- **Backend**: FastAPI + Uvicorn
- **LLM**: Anthropic Claude (claude-sonnet-4-20250514)
- **Vector Database**: ChromaDB with FastEmbed embeddings (BAAI/bge-small-en-v1.5)
- **RAG Framework**: LangChain
- **Web Scraping**: BeautifulSoup + Playwright
- **Frontend**: Vanilla HTML/CSS/JS

## Project Structure

```
macos-tahoe-rag/
├── api/
│   └── chat.py              # FastAPI endpoints
├── rag/
│   ├── indexer.py           # Document chunking & vector DB creation
│   ├── retriever.py         # Hybrid search implementation
│   └── chroma_db/           # Persisted vector database
├── scrapers/
│   ├── base.py              # HTTP scraper for static pages
│   ├── support.py           # Playwright scraper for support articles
│   └── playwright.py        # Playwright scraper for developer docs
├── static/
│   ├── index.html           # Chat UI
│   ├── script.js            # Client-side logic
│   └── style.css            # Styling
├── docs/                    # Scraped documentation files
├── main.py                  # Local dev entry point
├── requirements.txt         # Python dependencies
├── Procfile                 # Heroku/Railway config
└── vercel.json              # Vercel deployment config
```

## Installation

### Prerequisites

- Python 3.11+
- Anthropic API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd macos-tahoe-rag
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers** (only if you need to update scraped docs)
   ```bash
   playwright install chromium
   ```

## Configuration

Create a `.env` file in the project root:

```env
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```

## Running Locally

### Start the server

```bash
python main.py
```

The app will be available at `http://127.0.0.1:8000`

### API Documentation

FastAPI auto-generates interactive docs at `http://127.0.0.1:8000/docs`

## Indexing Documents

If you need to rebuild the vector database (after adding new docs):

```bash
python -m rag.indexer
```

This will:
- Load all `.txt` files from the `docs/` folder
- Chunk documents into 1000-character segments
- Generate embeddings and store in ChromaDB

## Updating Documentation

To scrape fresh documentation from Apple:

```bash
# Scrape Apple Newsroom and static support pages
python scrapers/base.py

# Scrape JS-rendered Apple Support articles
python scrapers/support.py

# Scrape Apple Developer documentation
python scrapers/playwright.py
```

After scraping, re-run the indexer to update the vector database.

## API Endpoints

### POST /api/chat

Send a chat message and receive an AI response with sources.

**Request:**
```json
{
  "message": "What Macs are compatible with macOS Tahoe?",
  "history": []
}
```

**Response:**
```json
{
  "response": "macOS Tahoe is compatible with...",
  "sources": ["macos-tahoe-compatible-macs.txt"]
}
```

### GET /api/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "rag_initialized": true
}
```

## Deployment

### Vercel

The project includes `vercel.json` for seamless Vercel deployment:

```bash
vercel deploy
```

### Heroku / Railway

Uses the included `Procfile`:

```bash
heroku create
heroku config:set ANTHROPIC_API_KEY=your-key
git push heroku main
```

## How It Works

1. **User sends a question** via the chat interface
2. **RAG Retriever** searches ChromaDB for relevant document chunks using hybrid search (semantic + keyword)
3. **Top 5 chunks** are selected and passed to Claude along with the conversation history
4. **Claude generates a response** using the retrieved context
5. **Response + sources** are returned to the frontend
6. **Sources are displayed** in a collapsible panel for transparency

## Documentation Coverage

The scraped docs cover:
- macOS Tahoe release notes and announcements
- Compatible Mac models
- Upgrade guides
- Enterprise features
- Troubleshooting (battery, Wi-Fi, startup, storage, performance)
- System Settings guides
- Security content
- Time Machine backup

## License

MIT