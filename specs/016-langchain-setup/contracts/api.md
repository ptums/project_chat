# API Contracts: LangChain Environment Setup

## Module: `brain_core.langchain.config`

### `get_langchain_config() -> Dict[str, Any]`

**Location**: `brain_core/langchain/config.py`

**Purpose**: Load LangChain configuration from environment variables

**Parameters**: None

**Returns**: Dictionary with configuration:

- `openai_api_key`: OpenAI API key (from `OPENAI_API_KEY` env var)
- `model`: Model name (from `LANGCHAIN_MODEL` or `OPENAI_MODEL`, defaults to "gpt-3.5-turbo")
- `temperature`: Temperature setting (from `LANGCHAIN_TEMPERATURE`, defaults to 0.7)
- `max_tokens`: Max tokens (from `LANGCHAIN_MAX_TOKENS`, optional)

**Behavior**:

- Reads from existing `.env` or `.env.local` files
- Falls back to existing OpenAI config if LangChain-specific vars not set
- Provides sensible defaults
- Logs configuration loading (debug level)

**Example**:

```python
from brain_core.langchain.config import get_langchain_config

config = get_langchain_config()
# Returns: {
#     "openai_api_key": "sk-...",
#     "model": "gpt-3.5-turbo",
#     "temperature": 0.7
# }
```

## Module: `brain_core.langchain.llm`

### `create_openai_llm(model: str = None, temperature: float = None) -> ChatOpenAI`

**Location**: `brain_core/langchain/llm.py`

**Purpose**: Create LangChain OpenAI LLM instance

**Parameters**:

- `model`: Optional model name (overrides config default)
- `temperature`: Optional temperature (overrides config default)

**Returns**: LangChain `ChatOpenAI` instance

**Behavior**:

- Uses configuration from `get_langchain_config()`
- Applies parameter overrides if provided
- Creates and returns `ChatOpenAI` instance
- Handles missing API key gracefully (raises clear error)

**Example**:

```python
from brain_core.langchain.llm import create_openai_llm

# Use defaults from config
llm = create_openai_llm()

# Override model
llm = create_openai_llm(model="gpt-4")

# Override temperature
llm = create_openai_llm(temperature=0.5)
```

**Dependencies**:

- Requires `langchain-openai` package installed
- Requires `OPENAI_API_KEY` environment variable set

## Module: `brain_core.langchain.memory`

### `create_conversation_memory() -> ChatMessageHistory`

**Location**: `brain_core/langchain/memory.py`

**Purpose**: Create LangChain memory instance (preparation for future agents)

**Parameters**: None

**Returns**: LangChain `ChatMessageHistory` instance (from langchain_community) or None if not installed

**Behavior**:

- Creates ChatMessageHistory instance (LangChain v1.0+ approach)
- ConversationBufferMemory is deprecated in v1.0, using ChatMessageHistory instead
- Ready for future agent integration
- Not yet used in production code
- Returns None if langchain-community not installed (logs warning)

**Example**:

```python
from brain_core.langchain.memory import create_conversation_memory

memory = create_conversation_memory()
# Returns: ConversationBufferMemory instance
# Ready for future agent use
```

**Future Integration**:

- Will integrate with existing conversation storage
- Will load conversation history from PostgreSQL
- Will persist memory state to conversation storage

## Module: `brain_core.langchain`

### Module Exports

**Location**: `brain_core/langchain/__init__.py`

**Purpose**: Provide convenient imports for LangChain functionality

**Exports**:

- `get_langchain_config` from `.config`
- `create_openai_llm` from `.llm`
- `create_conversation_memory` from `.memory`

**Example**:

```python
from brain_core.langchain import create_openai_llm, get_langchain_config

config = get_langchain_config()
llm = create_openai_llm()
```

## Error Handling

### Missing API Key

**Error**: `ValueError` with message: "OPENAI_API_KEY not found in environment"

**Handling**:

- Check `.env` or `.env.local` file
- Verify `OPENAI_API_KEY` is set
- Falls back to existing OpenAI config if available

### Missing Dependencies

**Error**: `ImportError` when importing LangChain modules

**Handling**:

- Install LangChain dependencies: `pip install -r requirements.txt`
- Verify `langchain` and `langchain-openai` packages installed

### Configuration Errors

**Error**: Invalid configuration values

**Handling**:

- Logs warning and uses defaults
- Does not raise exceptions for optional config
- Only raises for required config (API key)

## Compatibility

### With Existing OpenAI SDK

- Both can coexist in same environment
- Same API key works for both
- No conflicts between packages
- Existing code continues to work unchanged

### With Existing Configuration

- Reuses existing `.env` structure
- Shares `OPENAI_API_KEY` environment variable
- Extends rather than replaces existing config
- Maintains backward compatibility
