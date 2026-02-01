#!/usr/bin/env python3
"""
Retriever for macOS Tahoe RAG chatbot.
Searches ChromaDB for relevant document chunks.
"""

from pathlib import Path
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Paths
BASE_DIR = Path(__file__).parent.parent
CHROMA_DIR = BASE_DIR / "rag" / "chroma_db"

# Embedding model (must match indexer)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Retrieval parameters
TOP_K = 5  # Number of chunks to retrieve


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
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )

        print("Loading vector store...")
        self.vectorstore = Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=self.embeddings
        )

        self._initialized = True
        print(f"Retriever initialized with {self.vectorstore._collection.count()} vectors")

    def retrieve(self, query: str, k: int = TOP_K) -> list[dict]:
        """
        Retrieve relevant document chunks for a query.

        Args:
            query: The user's question
            k: Number of chunks to retrieve

        Returns:
            List of dicts with 'content' and 'source' keys
        """
        if not self._initialized:
            self.initialize()

        # Search for similar documents
        results = self.vectorstore.similarity_search_with_score(query, k=k)

        # Format results
        chunks = []
        for doc, score in results:
            chunks.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "score": score
            })

        return chunks

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

        chunks = retriever.retrieve(query, k=3)
        for i, chunk in enumerate(chunks, 1):
            print(f"\n[{i}] Source: {chunk['source']} (score: {chunk['score']:.4f})")
            print(f"Content: {chunk['content'][:200]}...")
