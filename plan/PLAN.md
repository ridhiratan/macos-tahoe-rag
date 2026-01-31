# macOS Tahoe RAG Chatbot - Project Plan

## Overview
A RAG-powered chatbot that answers questions about macOS Tahoe (macOS 26) using official Apple documentation.

## Tech Stack
- **Backend:** FastAPI (Python)
- **Frontend:** HTML/CSS/JavaScript
- **AI:** Anthropic Claude API
- **RAG Components:**
  - Embeddings: `sentence-transformers` (free, local)
  - Vector Store: ChromaDB (free, local)
- **Deployment:** Vercel

---

## Scraped Documents

| File | Size | Content |
|------|------|---------|
| `announcement.txt` | 38KB | WWDC 2025 announcement - detailed features |
| `release_announcement.txt` | 40KB | September 2025 release announcement |
| `whats_new_updates.txt` | 8KB | Update history and changes |
| `macos_main.txt` | 6KB | Main macOS page overview |
| `enterprise_features.txt` | 5KB | Enterprise/MDM features |
| `how_to_upgrade.txt` | 2KB | Upgrade instructions |
| `compatible_computers.txt` | 2KB | Supported Mac models |
| `release_notes.txt` | ~300B | Minimal (JS-rendered page) |
| `release_notes_26_2.txt` | ~300B | Minimal (JS-rendered page) |

**Total: ~100KB of macOS Tahoe documentation**

### Notes on Scraped Content
- Apple's developer docs use JavaScript rendering, so the scraper got minimal content
- Newsroom announcements have the richest content
- Additional URLs can be added to `scraper.py` if needed

---

## RAG Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           INDEXING (One-time)                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   docs/*.txt  ──▶  Chunking  ──▶  Embeddings  ──▶  ChromaDB            │
│   (Apple docs)    (split text)   (vectors)        (vector store)        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         QUERY (Runtime)                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   User Question                                                         │
│        │                                                                │
│        ▼                                                                │
│   Embed Query  ──▶  Search ChromaDB  ──▶  Top K Chunks                 │
│        │                                      │                         │
│        ▼                                      ▼                         │
│   ┌─────────────────────────────────────────────────┐                  │
│   │  Claude API                                      │                  │
│   │  - System Prompt (macOS Tahoe expert)           │                  │
│   │  - Retrieved Context (relevant chunks)          │                  │
│   │  - User Question                                 │                  │
│   └─────────────────────────────────────────────────┘                  │
│        │                                                                │
│        ▼                                                                │
│   Answer (grounded in Apple docs)                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
macos-tahoe-rag/
├── venv/                    # Python virtual environment
├── api/
│   └── chat.py              # FastAPI backend with RAG
├── static/
│   ├── index.html           # Chat UI
│   ├── style.css
│   └── script.js
├── docs/                    # Scraped Apple documentation
│   ├── announcement.txt
│   ├── release_announcement.txt
│   ├── whats_new_updates.txt
│   └── ...
├── plan/
│   └── PLAN.md              # This file
├── rag/                     # RAG components (to be created)
│   ├── indexer.py           # Document chunking & indexing
│   ├── retriever.py         # Query & retrieve relevant chunks
│   └── chroma_db/           # Vector database storage
├── scraper.py               # Apple docs scraper
├── main.py                  # Local dev runner
├── .env                     # API keys (gitignored)
├── .gitignore
├── requirements.txt
└── vercel.json
```

---

## Implementation Steps

### Phase 1: Scraping ✅
- [x] Create scraper for Apple pages
- [x] Scrape macOS Tahoe documentation
- [x] Save to `docs/` folder

### Phase 2: RAG Pipeline
- [ ] Install RAG dependencies (chromadb, sentence-transformers)
- [ ] Create `indexer.py` - chunk documents and create embeddings
- [ ] Create `retriever.py` - search for relevant chunks
- [ ] Index all documents into ChromaDB

### Phase 3: Integration
- [ ] Update `api/chat.py` to use RAG retrieval
- [ ] Modify prompt to include retrieved context
- [ ] Test with sample questions

### Phase 4: Testing & Refinement
- [ ] Test accuracy of responses
- [ ] Tune chunk size and retrieval parameters
- [ ] Add source citations to responses

### Phase 5: Deployment
- [ ] Push to GitHub
- [ ] Deploy to Vercel
- [ ] Configure environment variables

---

## Key Parameters (to tune)

| Parameter | Initial Value | Description |
|-----------|---------------|-------------|
| Chunk size | 500 tokens | Size of text chunks |
| Chunk overlap | 50 tokens | Overlap between chunks |
| Top K | 5 | Number of chunks to retrieve |
| Embedding model | `all-MiniLM-L6-v2` | Sentence transformer model |

---

## Dependencies to Add

```
chromadb
sentence-transformers
```

---

## Next Steps
1. Build the RAG pipeline (indexer + retriever)
2. Integrate with chatbot API
3. Test and refine
