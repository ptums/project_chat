# Implementation Plan: LangChain Environment Setup

**Branch**: `016-langchain-setup` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/016-langchain-setup/spec.md`

## Summary

Set up project_chat with LangChain infrastructure to prepare for future migration of projects (DAAS, FF, THN, 700B, General) into their own agents. This foundational phase establishes the environment, dependencies, and module structure without implementing full agent migration.

## Technical Context

**Language/Version**: Python 3.10+ (existing project standard)  
**Primary Dependencies**:

- Existing: psycopg2-binary, python-dotenv, openai, requests, gitpython, python-frontmatter, markdown
- New: langchain, langchain-openai, langchain-community (optional)
  **Storage**: PostgreSQL (existing schema, no changes)  
  **Testing**: Manual testing (consistent with project standards)  
  **Target Platform**: Linux/macOS CLI application  
  **Project Type**: Single project (Python CLI)  
  **Performance Goals**: No performance impact (setup only, not used in production code yet)  
  **Constraints**:

- Must not break existing functionality
- Must be optional/gradual migration path
- Must support both LangChain and direct OpenAI SDK during transition
- LangChain version must be stable and well-supported
- Compatibility with Python 3.10+ required

**Scale/Scope**:

- Installation and configuration only
- Module structure preparation
- No production code changes
- No database migrations
- Foundation for future agent development

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

No constitution violations identified. This feature:

- Adds new dependencies (standard practice)
- Creates new module structure (organizational improvement)
- Maintains backward compatibility (no breaking changes)
- Follows existing project patterns (module organization)
- Prepares for future features (agent migration)

## Project Structure

### Documentation (this feature)

```text
specs/016-langchain-setup/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
brain_core/
├── langchain/            # NEW: LangChain module
│   ├── __init__.py       # Module initialization
│   ├── config.py         # LangChain configuration
│   ├── llm.py            # LangChain LLM setup
│   └── memory.py         # LangChain memory setup (preparation)
├── chat.py               # UNCHANGED: Existing chat functionality
├── context_builder.py    # UNCHANGED: Existing context building
└── config.py             # UNCHANGED: Existing configuration

requirements.txt          # MODIFY: Add LangChain dependencies
```

**Structure Decision**: Add new `brain_core/langchain/` module. Existing code remains unchanged. LangChain is available but not yet integrated into production code paths.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations identified.

## Phase 0: Research & Design Decisions ✅

**Status**: Complete - See `research.md` for all decisions.

### Research Tasks

1. **LangChain Version Selection**

   - Research: Which LangChain version to use? Latest stable vs LTS?
   - Decision: Use LangChain v1.0 (latest stable, production-ready)
   - Rationale: Production-ready, modern architecture, active support

2. **LangChain Package Structure**

   - Research: Should we use `langchain` + `langchain-openai` or `langchain[openai]`?
   - Decision: Use `langchain` + `langchain-openai` (separate packages)
   - Rationale: Modular architecture, better dependency management, follows v1.0 best practices

3. **OpenAI Integration Strategy**

   - Research: How to integrate LangChain OpenAI alongside existing OpenAI SDK?
   - Decision: Use shared configuration, separate initialization
   - Rationale: Same API key works for both, no conflicts, can reuse existing config

4. **Configuration Management**

   - Research: How to manage LangChain config in existing `.env` structure?
   - Decision: Extend existing config system, add LangChain-specific config module
   - Rationale: Reuse existing `.env` structure, share API key, maintain backward compatibility

5. **Memory/State Management**
   - Research: What LangChain memory patterns to prepare for?
   - Decision: Prepare `ConversationBufferMemory` structure, integrate with existing storage later
   - Rationale: Start simple, can upgrade later, existing PostgreSQL can be used

## Phase 1: Design & Contracts ✅

**Status**: Complete - See `data-model.md`, `contracts/api.md`, and `quickstart.md`.

### Data Model

**No Schema Changes Required**

- Existing database schema unchanged
- No new tables or columns
- LangChain state will be managed in-memory or via existing conversation storage

### API Contracts

**Module: `brain_core.langchain.config`**

- **Function**: `get_langchain_config() -> Dict[str, Any]`
- **Purpose**: Load LangChain configuration from environment
- **Returns**: Configuration dictionary with OpenAI API key, model settings, etc.

**Module: `brain_core.langchain.llm`**

- **Function**: `create_openai_llm(model: str = None, temperature: float = None) -> ChatOpenAI`
- **Purpose**: Create LangChain OpenAI LLM instance
- **Returns**: LangChain ChatOpenAI instance
- **Behavior**: Uses configuration from `langchain.config`, falls back to existing OpenAI config

**Module: `brain_core.langchain.memory`**

- **Function**: `create_conversation_memory() -> ConversationBufferMemory` (or similar)
- **Purpose**: Create LangChain memory instance (preparation for future agents)
- **Returns**: LangChain memory instance
- **Behavior**: Prepares memory structure, not yet integrated into chat flow

### Quickstart Guide

**For Developers:**

1. Install LangChain dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Verify LangChain installation:

   ```python
   from brain_core.langchain.llm import create_openai_llm
   llm = create_openai_llm()
   # Should create LLM instance without errors
   ```

3. Test configuration:
   ```python
   from brain_core.langchain.config import get_langchain_config
   config = get_langchain_config()
   # Should return configuration dict
   ```

**For Users:**

- No changes to CLI interface
- No changes to existing functionality
- LangChain is installed but not yet used in production code

## Success Metrics

1. ✅ LangChain dependencies installed
2. ✅ LangChain modules importable
3. ✅ LangChain configuration module created
4. ✅ LangChain OpenAI LLM can be initialized
5. ✅ No breaking changes to existing functionality
6. ✅ Environment ready for future agent development
7. ✅ Clear documentation for future migration
