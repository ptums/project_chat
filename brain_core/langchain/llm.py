"""LangChain LLM setup."""
import logging
from langchain_openai import ChatOpenAI
from typing import Optional

from .config import get_langchain_config

logger = logging.getLogger(__name__)

def create_openai_llm(
    model: Optional[str] = None,
    temperature: Optional[float] = None
) -> ChatOpenAI:
    """
    Create LangChain OpenAI LLM instance.

    Args:
        model: Optional model name (overrides config default)
        temperature: Optional temperature (overrides config default)

    Returns:
        LangChain ChatOpenAI instance
    """
    config = get_langchain_config()

    llm_config = {
        "model": model or config["model"],
        "temperature": temperature if temperature is not None else config["temperature"],
        "openai_api_key": config["openai_api_key"],
    }

    # Add max_tokens if configured
    if "max_tokens" in config:
        llm_config["max_tokens"] = config["max_tokens"]

    logger.debug(f"Creating LangChain LLM: model={llm_config['model']}")
    return ChatOpenAI(**llm_config)
