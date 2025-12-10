# Data Model: LangChain Environment Setup

## Overview

No new data models required. This feature adds LangChain infrastructure without changing data structures. Future agent migration may use existing conversation storage.

## Existing Entities (Unchanged)

### Conversation Storage

**Location**: PostgreSQL `conversations` and `messages` tables

**Current Behavior**:

- Conversations stored in `conversations` table
- Messages stored in `messages` table
- Conversation history available for retrieval

**New Behavior**:

- No changes to data model
- LangChain memory can use existing conversation storage
- Future agents will integrate with existing tables

**Data Flow** (Future):

```
LangChain Agent → ConversationBufferMemory → PostgreSQL (conversations/messages)
```

### Configuration

**Location**: `.env` files and `brain_core/config.py`

**Current Behavior**:

- Configuration loaded from `.env` or `.env.local`
- OpenAI API key stored as `OPENAI_API_KEY`
- Model configuration in `brain_core/config.py`

**New Behavior**:

- LangChain uses same `OPENAI_API_KEY` environment variable
- LangChain-specific config in `brain_core/langchain/config.py`
- Shared configuration, separate initialization

**Data Flow**:

```
.env → brain_core/config.py (existing)
.env → brain_core/langchain/config.py (new, reads same vars)
```

## New Entities (Configuration Only)

### LangChain Configuration

**Location**: `brain_core/langchain/config.py`

**Purpose**: Manage LangChain-specific configuration

**Fields**:

- `OPENAI_API_KEY`: Shared with existing OpenAI SDK
- `OPENAI_MODEL`: Model name (optional, defaults to gpt-3.5-turbo)
- `LANGCHAIN_TEMPERATURE`: Temperature setting (optional)
- `LANGCHAIN_MAX_TOKENS`: Max tokens (optional)

**Behavior**:

- Reads from existing `.env` files
- Falls back to existing OpenAI config if LangChain-specific vars not set
- Provides defaults for LangChain-specific settings

### LangChain LLM Instance

**Location**: `brain_core/langchain/llm.py`

**Purpose**: Create and configure LangChain OpenAI LLM instances

**Type**: LangChain `ChatOpenAI` instance

**Configuration**:

- Uses `OPENAI_API_KEY` from environment
- Model from config or default
- Temperature and other parameters from config

**Behavior**:

- Creates LangChain LLM instance
- Not yet used in production code
- Available for future agent development

### LangChain Memory Instance

**Location**: `brain_core/langchain/memory.py`

**Purpose**: Prepare memory structure for future agents

**Type**: LangChain `ConversationBufferMemory` (or similar)

**Configuration**:

- Memory type: `ConversationBufferMemory` (simple buffer)
- Can be upgraded to summary memory later
- Will integrate with existing conversation storage

**Behavior**:

- Creates memory instance structure
- Not yet integrated into chat flow
- Ready for future agent integration

## No Schema Changes

- No database migrations required
- No new tables or columns
- All LangChain state will be managed in-memory or via existing conversation storage
- Future agents may use existing `conversations` and `messages` tables

## Future Integration Points

### Agent State (Future)

**Potential Storage**:

- In-memory during conversation
- Persisted to existing `conversations` table
- Agent-specific metadata in conversation metadata field

### Memory Persistence (Future)

**Potential Approach**:

- Load conversation history from `messages` table
- Populate LangChain memory from existing data
- Save memory state back to conversation storage

**No Schema Changes Required**: Existing tables can support agent memory
