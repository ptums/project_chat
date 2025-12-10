"""LangChain configuration management."""
import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env files (same as existing config)
if os.path.exists(".env.local"):
    load_dotenv(".env.local")
load_dotenv()

def get_langchain_config() -> Dict[str, Any]:
    """
    Get LangChain configuration from environment variables.

    Returns:
        Dictionary with LangChain configuration:
        - openai_api_key: OpenAI API key
        - model: Model name (defaults to gpt-3.5-turbo)
        - temperature: Temperature setting (defaults to 0.7)
        - max_tokens: Max tokens (optional)
    """
    # Get API key (shared with existing OpenAI SDK)
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Note: OpenAI SDK client doesn't expose api_key directly, so we rely on environment variable
    # The client is initialized with the API key from environment automatically
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment")

    # Get model (LangChain-specific or fall back to existing)
    model = os.getenv("LANGCHAIN_MODEL") or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    # Get temperature (optional, defaults to 0.7)
    temperature = float(os.getenv("LANGCHAIN_TEMPERATURE", "0.7"))

    # Get max tokens (optional)
    max_tokens = os.getenv("LANGCHAIN_MAX_TOKENS")
    if max_tokens:
        max_tokens = int(max_tokens)

    config = {
        "openai_api_key": api_key,
        "model": model,
        "temperature": temperature,
    }

    if max_tokens:
        config["max_tokens"] = max_tokens

    logger.debug(f"LangChain config loaded: model={model}, temperature={temperature}")
    return config
