"""
Shared RAG Utilities
Common resources like ChromaDB client singleton
"""

import logging
from typing import Optional
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings

logger = logging.getLogger(__name__)

# Distance metric for all ChromaDB collections.
# ChromaDB passes this via metadata={"hnsw:space": ...} at collection creation time
# (a ChromaDB API quirk — hnsw:* keys in metadata are index config, not document metadata).
# Valid values: "cosine" | "l2" | "ip"
# IMPORTANT: retrieval.py distance→relevance conversion formula assumes "cosine".
# Changing this requires recreating all collections (force_reingest=True).
HNSW_SPACE = "cosine"

# Global ChromaDB client (singleton pattern to avoid conflicts)
_chroma_client: Optional[chromadb.ClientAPI] = None


def get_chroma_client() -> chromadb.ClientAPI:
    """
    Get or create ChromaDB client singleton
    
    Returns:
        ChromaDB PersistentClient instance
    """
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        logger.info(f"ChromaDB client initialized: {settings.chroma_persist_directory}")
    return _chroma_client
