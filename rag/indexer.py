#!/usr/bin/env python3
"""
Indexer for macOS Tahoe RAG chatbot.
Loads documents, chunks them, creates embeddings, and stores in ChromaDB.
"""

from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Paths
BASE_DIR = Path(__file__).parent.parent
DOCS_DIR = BASE_DIR / "docs"
CHROMA_DIR = BASE_DIR / "rag" / "chroma_db"

# Embedding model (free, runs locally)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Chunking parameters
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def load_documents():
    """Load all text documents from the docs folder."""
    print(f"Loading documents from {DOCS_DIR}...")

    loader = DirectoryLoader(
        str(DOCS_DIR),
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )

    docs = loader.load()
    print(f"Loaded {len(docs)} documents")

    for doc in docs:
        # Add source filename to metadata
        doc.metadata["source"] = Path(doc.metadata["source"]).name

    return docs


def chunk_documents(docs):
    """Split documents into smaller chunks."""
    print(f"Chunking documents (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )

    splits = text_splitter.split_documents(docs)
    print(f"Created {len(splits)} chunks")

    return splits


def create_vectorstore(chunks):
    """Create ChromaDB vectorstore with embeddings."""
    print(f"Creating embeddings with {EMBEDDING_MODEL}...")
    print("(This may take a moment on first run as the model downloads)")

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    # Remove old database if exists
    if CHROMA_DIR.exists():
        import shutil
        shutil.rmtree(CHROMA_DIR)
        print("Removed old vector database")

    print("Creating vector store...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR)
    )

    print(f"Vector store created with {vectorstore._collection.count()} vectors")
    print(f"Saved to {CHROMA_DIR}")

    return vectorstore


def index_documents():
    """Main indexing pipeline."""
    print("=" * 50)
    print("macOS Tahoe RAG - Document Indexer")
    print("=" * 50)

    # Load
    docs = load_documents()

    # Chunk
    chunks = chunk_documents(docs)

    # Create vectorstore
    vectorstore = create_vectorstore(chunks)

    print("=" * 50)
    print("Indexing complete!")
    print("=" * 50)

    return vectorstore


if __name__ == "__main__":
    index_documents()
