#!/usr/bin/env python3
"""
Retriever for macOS Tahoe RAG chatbot.
Searches ChromaDB for relevant document chunks.
Uses hybrid search: semantic similarity + keyword boosting.
"""

import re
from pathlib import Path
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_chroma import Chroma

# Paths
BASE_DIR = Path(__file__).parent.parent
CHROMA_DIR = BASE_DIR / "rag" / "chroma_db"

# Embedding model (must match indexer)
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# Retrieval parameters
TOP_K = 5  # Number of chunks to retrieve
INITIAL_K = 15  # Retrieve more initially for reranking
RELEVANCE_THRESHOLD = 0.35  # Chunks with score above this are considered irrelevant

# Important terms for keyword boosting
KEY_TERMS = {
    "liquid glass", "tahoe", "macos 26", "wwdc", "apple intelligence",
    "siri", "safari", "finder", "system settings", "battery", "wifi",
    "compatible", "upgrade", "features", "new", "release"
}


class MacOSTahoeRetriever:
    """Retriever for macOS Tahoe documentation."""

    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self._initialized = False

    def initialize(self):
        """Initialize the retriever (lazy loading)."""
        if self._initialized:
            return

        if not CHROMA_DIR.exists():
            raise RuntimeError(
                "Vector database not found. Run 'python -m rag.indexer' first."
            )

        print("Loading embedding model...")
        self.embeddings = FastEmbedEmbeddings(model_name=EMBEDDING_MODEL)

        print("Loading vector store...")
        self.vectorstore = Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=self.embeddings
        )

        self._initialized = True
        print(f"Retriever initialized with {self.vectorstore._collection.count()} vectors")

    def _keyword_boost(self, query: str, content: str) -> float:
        """Calculate keyword match boost score."""
        query_lower = query.lower()
        content_lower = content.lower()

        boost = 0.0
        # Check for key terms from query in content
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        for word in query_words:
            if len(word) > 3 and word in content_lower:
                boost += 0.05

        # Extra boost for important macOS terms
        for term in KEY_TERMS:
            if term in query_lower and term in content_lower:
                boost += 0.1

        return min(boost, 0.3)  # Cap boost at 0.3

    def retrieve(self, query: str, k: int = TOP_K) -> tuple[list[dict], bool]:
        """
        Retrieve relevant document chunks using hybrid search.
        Combines semantic similarity with keyword boosting.

        Args:
            query: The user's question
            k: Number of chunks to retrieve

        Returns:
            Tuple of (list of chunk dicts, is_relevant bool).
            is_relevant is False when the best chunk score exceeds RELEVANCE_THRESHOLD.
        """
        if not self._initialized:
            self.initialize()

        # Retrieve more candidates initially
        results = self.vectorstore.similarity_search_with_score(query, k=INITIAL_K)

        # Score and rerank with keyword boosting
        chunks = []
        for doc, semantic_score in results:
            content = doc.page_content
            keyword_boost = self._keyword_boost(query, content)

            # Lower score = better in ChromaDB (distance metric)
            # Subtract boost to improve ranking
            final_score = semantic_score - keyword_boost

            chunks.append({
                "content": content,
                "source": doc.metadata.get("source", "unknown"),
                "score": final_score,
                "semantic_score": semantic_score,
                "keyword_boost": keyword_boost
            })

        # Sort by final score (lower is better) and return top k
        chunks.sort(key=lambda x: x["score"])
        top_chunks = chunks[:k]

        # Check if best result is relevant enough
        is_relevant = bool(top_chunks and top_chunks[0]["score"] < RELEVANCE_THRESHOLD)

        return top_chunks, is_relevant

    def format_context(self, chunks: list[dict]) -> str:
        """Format retrieved chunks as context for the LLM."""
        if not chunks:
            return "No relevant documentation found."

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Source: {chunk['source']}]\n{chunk['content']}"
            )

        return "\n\n---\n\n".join(context_parts)


# Singleton instance
_retriever = None


def get_retriever() -> MacOSTahoeRetriever:
    """Get or create the singleton retriever instance."""
    global _retriever
    if _retriever is None:
        _retriever = MacOSTahoeRetriever()
    return _retriever


if __name__ == "__main__":
    # Test the retriever
    retriever = get_retriever()
    retriever.initialize()

    test_queries = [
        "What are the new features in macOS Tahoe?",
        "What Macs are compatible with macOS 26?",
        "What is Liquid Glass?",
    ]

    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print("=" * 50)

        chunks, is_relevant = retriever.retrieve(query, k=3)
        print(f"Relevant: {is_relevant}")
        for i, chunk in enumerate(chunks, 1):
            print(f"\n[{i}] Source: {chunk['source']} (score: {chunk['score']:.4f})")
            print(f"Content: {chunk['content'][:200]}...")
