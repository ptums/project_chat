"""
Embedding generation service using OpenAI API.

Provides functions to generate vector embeddings for text using OpenAI's
text-embedding-3-small model (1536 dimensions).
"""
import logging
from typing import List

from openai import OpenAI

from .config import client, MOCK_MODE

logger = logging.getLogger(__name__)

# Use the same OpenAI client from config
# In mock mode, we can't generate embeddings (would need mock implementation)
if MOCK_MODE:
    _embedding_client = None
    logger.warning("Embedding service unavailable in mock mode")
else:
    _embedding_client = OpenAI()


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using OpenAI text-embedding-3-small model.
    
    Args:
        text: Text to embed (will be truncated if too long)
        
    Returns:
        List of 1536 float values representing the embedding vector
        
    Raises:
        Exception: If embedding generation fails (API error, network issue, etc.)
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    if _embedding_client is None:
        raise Exception("Embedding service unavailable (mock mode or client not initialized)")
    
    # OpenAI embeddings API has token limits, but text-embedding-3-small
    # supports up to 8191 input tokens, which is quite large
    # We'll let OpenAI handle truncation if needed
    
    try:
        logger.debug(f"Generating embedding for text (length: {len(text)} chars)")
        response = _embedding_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        
        if not response.data or len(response.data) == 0:
            raise ValueError("OpenAI API returned empty embedding data")
        
        embedding = response.data[0].embedding
        
        if len(embedding) != 1536:
            raise ValueError(
                f"Expected embedding dimension 1536, got {len(embedding)}"
            )
        
        logger.debug(f"Generated embedding successfully (dimension: {len(embedding)})")
        return embedding
        
    except Exception as e:
        # Handle specific error types
        error_msg = str(e)
        if "rate limit" in error_msg.lower() or "429" in error_msg:
            logger.error("OpenAI API rate limit exceeded. Please wait before retrying.")
            raise Exception("Embedding generation rate limited. Please wait and retry.")
        elif "network" in error_msg.lower() or "connection" in error_msg.lower():
            logger.error("Network error during embedding generation")
            raise Exception("Network error: Unable to connect to OpenAI API.")
        elif "api key" in error_msg.lower() or "401" in error_msg or "403" in error_msg:
            logger.error("OpenAI API authentication failed")
            raise Exception("OpenAI API key invalid or missing. Check OPENAI_API_KEY environment variable.")
        else:
            logger.error(f"Failed to generate embedding: {e}")
            raise

