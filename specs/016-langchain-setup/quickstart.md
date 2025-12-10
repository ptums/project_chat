# Quickstart: LangChain Environment Setup

## Overview

Set up LangChain infrastructure in project_chat to prepare for future agent migration. This guide covers installation, configuration, and verification.

## Prerequisites

- Python 3.10+ installed
- Existing project_chat setup working
- OpenAI API key configured (in `.env` or `.env.local`)
- PostgreSQL database set up (existing)

## Step 1: Install LangChain Dependencies

**Update `requirements.txt`:**

Add the following lines to `requirements.txt`:

```txt
langchain>=1.0.0
langchain-openai>=1.0.0
```

**Install dependencies:**

```bash
pip install -r requirements.txt
```

**Verify installation:**

```bash
python3 -c "import langchain; import langchain_openai; print('LangChain installed successfully')"
```

Expected output: `LangChain installed successfully`

## Step 2: Create LangChain Module Structure

**Create module directory:**

```bash
mkdir -p brain_core/langchain
touch brain_core/langchain/__init__.py
touch brain_core/langchain/config.py
touch brain_core/langchain/llm.py
touch brain_core/langchain/memory.py
```

## Step 3: Implement Configuration Module

**Create `brain_core/langchain/config.py`:**

```python
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
    if not api_key:
        # Fall back to existing config if available
        try:
            from brain_core.config import client
            if hasattr(client, 'api_key'):
                api_key = client.api_key
        except ImportError:
            pass

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
```

## Step 4: Implement LLM Module

**Create `brain_core/langchain/llm.py`:**

```python
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
```

## Step 5: Implement Memory Module

**Create `brain_core/langchain/memory.py`:**

```python
"""LangChain memory setup (preparation for future agents)."""
import logging
from langchain.memory import ConversationBufferMemory

logger = logging.getLogger(__name__)

def create_conversation_memory() -> ConversationBufferMemory:
    """
    Create LangChain conversation memory instance.

    This is preparation for future agent development.
    Memory will be integrated with existing conversation storage later.

    Returns:
        LangChain ConversationBufferMemory instance
    """
    logger.debug("Creating LangChain conversation memory")
    return ConversationBufferMemory(
        return_messages=True,  # Return message objects, not strings
        memory_key="chat_history"  # Key for storing messages
    )
```

## Step 6: Create Module Exports

**Create `brain_core/langchain/__init__.py`:**

```python
"""LangChain module for project_chat."""
from .config import get_langchain_config
from .llm import create_openai_llm
from .memory import create_conversation_memory

__all__ = [
    "get_langchain_config",
    "create_openai_llm",
    "create_conversation_memory",
]
```

## Step 7: Verify Installation

**Test configuration:**

```python
from brain_core.langchain.config import get_langchain_config

config = get_langchain_config()
print(f"Model: {config['model']}")
print(f"Temperature: {config['temperature']}")
```

**Test LLM creation:**

```python
from brain_core.langchain.llm import create_openai_llm

llm = create_openai_llm()
print(f"LLM created: {llm.model_name}")
```

**Test memory creation:**

```python
from brain_core.langchain.memory import create_conversation_memory

memory = create_conversation_memory()
print(f"Memory created: {type(memory).__name__}")
```

## Step 8: Optional Configuration

**Add LangChain-specific environment variables (optional):**

In `.env` or `.env.local`:

```bash
# LangChain Configuration (optional)
LANGCHAIN_MODEL=gpt-4  # Override default model
LANGCHAIN_TEMPERATURE=0.5  # Override default temperature
LANGCHAIN_MAX_TOKENS=2000  # Set max tokens
```

**Note**: If not set, LangChain will use defaults or fall back to existing OpenAI config.

## Verification Checklist

- [ ] LangChain packages installed (`langchain`, `langchain-openai`)
- [ ] Module structure created (`brain_core/langchain/`)
- [ ] Configuration module implemented and working
- [ ] LLM module implemented and can create LLM instances
- [ ] Memory module implemented and can create memory instances
- [ ] Module exports working (can import from `brain_core.langchain`)
- [ ] No breaking changes to existing functionality
- [ ] Existing chat functionality still works

## Next Steps (Future)

Once LangChain is set up:

1. **Create base agent class** (future feature)
2. **Migrate one project to agent** (pilot - DAAS, THN, FF, 700B, or General)
3. **Test agent patterns** and refine architecture
4. **Migrate remaining projects** to agents
5. **Full agent-based architecture**

## Troubleshooting

### Import Error: No module named 'langchain'

**Solution**: Install dependencies: `pip install -r requirements.txt`

### ValueError: OPENAI_API_KEY not found

**Solution**: Set `OPENAI_API_KEY` in `.env` or `.env.local` file

### Module Import Error

**Solution**: Verify module structure exists: `ls -la brain_core/langchain/`

### Configuration Not Loading

**Solution**: Check `.env` file location and format (key=value, no quotes)
