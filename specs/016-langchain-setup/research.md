# Research: LangChain Environment Setup

## Research Questions

### 1. LangChain Version Selection

**Question**: Which LangChain version to use? Latest stable vs LTS?

**Findings**:

- LangChain v1.0 is now generally available (as of December 2025)
- v1.0 is production-ready after extensive testing
- v0.x release line remains supported for those not ready to migrate
- Versioning policy: Breaking changes will have minor version increments and deprecation notices
- Release cycle: Minor versions every 2-3 months, frequent patch releases

**Decision**: Use LangChain v1.0 (latest stable)

**Rationale**:

- Production-ready and stable
- Modern architecture with modular packages
- Active support and development
- Better integration patterns for OpenAI
- Future-proof for agent development

**Alternatives Considered**:

- v0.x: Still supported but legacy, may lack newer features
- Pre-release versions: Too unstable for production setup

### 2. LangChain Package Structure

**Question**: Should we use `langchain` + `langchain-openai` or `langchain[openai]`?

**Findings**:

- LangChain v1.0 uses modular architecture:
  - `langchain-core`: Base abstractions, lightweight dependencies
  - `langchain`: Main package with chains and retrieval strategies
  - `langchain-openai`: Dedicated OpenAI integration package
  - `langchain-community`: Community-maintained third-party integrations
- `langchain-openai` is a separate package for better:
  - Dedicated implementation and testing
  - Better tree-shaking (no optional dependencies)
  - Provider-specific features and optimizations
  - Faster release cycles

**Decision**: Use `langchain` + `langchain-openai` (separate packages)

**Rationale**:

- Modular architecture aligns with project structure
- Better dependency management
- Cleaner separation of concerns
- Easier to add other providers later (Anthropic, etc.)
- Follows LangChain v1.0 best practices

**Alternatives Considered**:

- `langchain[openai]`: Less explicit, harder to manage versions
- `langchain-community` only: Missing core functionality

### 3. OpenAI Integration Strategy

**Question**: How to integrate LangChain OpenAI alongside existing OpenAI SDK?

**Findings**:

- LangChain OpenAI uses same API key as OpenAI SDK (`OPENAI_API_KEY`)
- Both can coexist in same environment
- LangChain wraps OpenAI SDK internally
- Configuration can be shared (same API key, model names)
- No conflicts between packages

**Decision**: Use shared configuration, separate initialization

**Rationale**:

- Same API key works for both
- Model names are compatible (gpt-4, gpt-3.5-turbo, etc.)
- Can use existing `.env` configuration
- No need to duplicate API keys
- LangChain can fall back to existing OpenAI config

**Alternatives Considered**:

- Separate API keys: Unnecessary, adds complexity
- Replace OpenAI SDK entirely: Too risky, breaks existing code

### 4. Configuration Management

**Question**: How to manage LangChain config in existing `.env` structure?

**Findings**:

- Existing config uses `python-dotenv` and `.env` files
- LangChain reads `OPENAI_API_KEY` from environment automatically
- Can use same environment variables as existing OpenAI SDK
- Model names are compatible
- Temperature and other parameters can be configured

**Decision**: Extend existing config system, add LangChain-specific config module

**Rationale**:

- Reuse existing `.env` structure
- Share `OPENAI_API_KEY` (no duplication)
- Add LangChain-specific config in `brain_core.langchain.config`
- Maintain backward compatibility
- Clear separation of concerns

**Alternatives Considered**:

- Separate config file: Unnecessary complexity
- Hardcode values: Not flexible, bad practice

### 5. Memory/State Management

**Question**: What LangChain memory patterns to prepare for?

**Findings**:

- LangChain provides several memory types:
  - `ConversationBufferMemory`: Simple conversation history
  - `ConversationBufferWindowMemory`: Limited window of messages
  - `ConversationSummaryMemory`: Summarized conversation history
  - `ConversationSummaryBufferMemory`: Combination of buffer and summary
- For agents, memory is typically managed per conversation
- Can integrate with existing conversation storage (PostgreSQL)
- Memory can be persisted and loaded

**Decision**: Prepare `ConversationBufferMemory` structure, integrate with existing conversation storage later

**Rationale**:

- Start simple with buffer memory
- Can upgrade to summary memory later if needed
- Existing PostgreSQL conversation storage can be used
- Memory structure ready for agent migration
- No database changes needed initially

**Alternatives Considered**:

- Summary memory from start: More complex, may not be needed
- Custom memory implementation: Unnecessary, LangChain provides good options

## Implementation Notes

### Package Installation

**Required Packages**:

```bash
langchain>=1.0.0
langchain-openai>=1.0.0
```

**Optional Packages** (for future use):

```bash
langchain-community>=1.0.0  # For additional integrations
```

### Configuration Structure

**Environment Variables** (reuse existing):

- `OPENAI_API_KEY` - Shared with existing OpenAI SDK
- `OPENAI_MODEL` - Model name (optional, defaults to gpt-3.5-turbo)

**New Configuration Module**:

- `brain_core.langchain.config` - LangChain-specific configuration
- Reads from existing `.env` files
- Provides defaults for LangChain-specific settings

### Module Structure

**New Module**: `brain_core/langchain/`

- `__init__.py` - Module exports
- `config.py` - Configuration management
- `llm.py` - LLM initialization
- `memory.py` - Memory setup (preparation)

### Integration Points

**Phase 1 (This Feature)**:

- Install packages
- Create module structure
- Set up configuration
- Test LLM initialization
- Prepare memory structure

**Phase 2 (Future - Agent Migration)**:

- Create base agent class
- Migrate one project to agent
- Integrate memory with conversation storage
- Test agent patterns

**Phase 3 (Future - Full Migration)**:

- Migrate all projects to agents
- Full agent-based architecture
