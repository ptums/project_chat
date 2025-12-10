# LangChain Environment Setup

## Overview

Set up project_chat with LangChain infrastructure to prepare for future migration of projects (DAAS, FF, THN, 700B, General) into their own agents. This is a foundational setup phase that establishes the environment and patterns without implementing full agent migration.

## Requirements

### 1. LangChain Installation and Configuration

**Current State:**

- Project uses OpenAI SDK directly via `openai` package
- No LangChain dependencies installed
- No agent framework in place

**New State:**

- LangChain installed and configured
- LangChain OpenAI integration set up
- Environment ready for agent development
- No breaking changes to existing functionality

**Changes Required:**

- Add LangChain dependencies to `requirements.txt`
- Create LangChain configuration module
- Set up LangChain OpenAI integration alongside existing OpenAI SDK
- Ensure compatibility with existing code

### 2. LangChain Integration Points

**Integration Areas:**

- OpenAI LLM integration (replace or complement existing OpenAI SDK usage)
- Memory/state management (prepare for agent state)
- Tool/function calling infrastructure (prepare for agent tools)
- Chain composition patterns (prepare for agent workflows)

**Constraints:**

- Must not break existing functionality
- Must be optional/gradual migration path
- Must support both LangChain and direct OpenAI SDK during transition

### 3. Project Structure Preparation

**Current Structure:**

```
brain_core/
├── chat.py
├── context_builder.py
├── config.py
└── ...
```

**New Structure (Preparation):**

```
brain_core/
├── chat.py (existing)
├── context_builder.py (existing)
├── config.py (existing)
├── langchain/ (new)
│   ├── __init__.py
│   ├── config.py (LangChain configuration)
│   ├── llm.py (LangChain LLM setup)
│   └── memory.py (LangChain memory setup)
└── ...
```

**Future Structure (Post-Migration):**

```
brain_core/
├── agents/ (future)
│   ├── base_agent.py
│   ├── daas_agent.py
│   ├── thn_agent.py
│   ├── ff_agent.py
│   ├── 700b_agent.py
│   └── general_agent.py
└── ...
```

### 4. Configuration Management

**Requirements:**

- LangChain configuration in `.env` files
- Support for both development and production environments
- Backward compatibility with existing OpenAI configuration
- Clear separation between LangChain and direct OpenAI SDK configs

## Technical Details

### Dependencies

**New Dependencies:**

- `langchain` - Core LangChain framework
- `langchain-openai` - OpenAI integration for LangChain
- `langchain-community` - Community integrations (optional, for future use)

**Version Constraints:**

- Use stable, well-supported versions
- Ensure compatibility with Python 3.10+
- Ensure compatibility with existing OpenAI SDK

### Integration Strategy

**Phase 1 (This Feature):**

- Install LangChain dependencies
- Set up basic LangChain configuration
- Create LangChain module structure
- Test LangChain LLM initialization
- Ensure no breaking changes

**Phase 2 (Future):**

- Migrate one project to LangChain agent (pilot)
- Test agent patterns
- Refine architecture

**Phase 3 (Future):**

- Migrate remaining projects to agents
- Full agent-based architecture

### Compatibility

**Must Maintain:**

- Existing OpenAI SDK usage continues to work
- Existing chat functionality unchanged
- Existing RAG functionality unchanged
- Existing project-specific extensions unchanged

**Can Add:**

- LangChain as parallel option
- LangChain configuration
- LangChain module structure
- LangChain utilities (not yet used in production code)

## Success Criteria

1. ✅ LangChain installed and importable
2. ✅ LangChain configuration module created
3. ✅ LangChain OpenAI LLM can be initialized
4. ✅ No breaking changes to existing functionality
5. ✅ Environment ready for future agent development
6. ✅ Clear path for gradual migration
