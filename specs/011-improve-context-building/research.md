# Research Notes: Improve Context Building with Base System Prompt

## 1. Base System Prompt Storage

- **Decision**: Store base system prompt in `brain_core/base_system_prompt.txt` as a plain text file.
- **Rationale**: Simple, editable, version-controlled, no parsing overhead. Text file is the most straightforward approach for content that users may need to edit frequently.
- **Alternatives Considered**:
  - Database storage (project_knowledge table). Rejected because base prompt is not project-specific and should be easily editable without database access.
  - YAML/JSON configuration file. Rejected due to unnecessary complexity for a single text block.
  - Environment variable. Rejected because it's not user-friendly for editing multi-line content.

## 2. System Prompt Composition Strategy

- **Decision**: Use string concatenation to compose base prompt + project-specific extension. Base prompt is loaded once at module import or function call, project extension is appended when project is not "general".
- **Rationale**: Simple, performant, clear separation of concerns. Base prompt is universal, project extensions are additive.
- **Alternatives Considered**:
  - Template-based system (Jinja2). Rejected due to unnecessary dependency for simple string composition.
  - Separate system message per component. Rejected because OpenAI API works best with a single coherent system message per conversation.

## 3. Project-Specific Context Format

- **Decision**: Append project context in format: "In this current conversation is tagged as project <project_name> and here we are going to discuss <overview column from project_knowledge>."
- **Rationale**: Clear, consistent format that explicitly states the project context. Uses existing project_knowledge table's overview column.
- **Alternatives Considered**:
  - Separate system message for project context. Rejected to keep system messages minimal and focused.
  - Embed project context in RAG retrieval results. Rejected because system prompt should be separate from retrieved context.

## 4. Context Builder Refactoring

- **Decision**: Refactor `context_builder.py` to:
  1. Load base system prompt from file
  2. Append project-specific extension if project != "general"
  3. Keep existing RAG retrieval logic separate (only used for project-specific conversations)
  4. Return composed system prompt + RAG context separately
- **Rationale**: Maintains separation between system prompt (behavioral instructions) and RAG context (retrieved knowledge). Makes future extensions easier.
- **Alternatives Considered**:
  - Merge system prompt and RAG into single context string. Rejected because they serve different purposes and should be composable independently.

## 5. Hardcoded Prompt Removal

- **Decision**: Remove hardcoded `base_system` string from `chat.py` (lines 75-89) and replace with call to context builder's base prompt loader.
- **Rationale**: Single source of truth for base prompt. Eliminates duplication and makes updates easier.
- **Alternatives Considered**:
  - Keep hardcoded prompt but sync with file. Rejected because it creates maintenance burden and risk of drift.

## 6. Extensibility Design

- **Decision**: Design system prompt composition as a chain: base → project extension → (future: project-specific custom prompt). Each layer is optional and additive.
- **Rationale**: Supports future requirements for project-specific system prompts without breaking existing functionality.
- **Alternatives Considered**:
  - Single monolithic prompt file per project. Rejected because it doesn't support shared base behavior across all projects.

## 7. File Loading Strategy

- **Decision**: Load base system prompt file on-demand (lazy loading) with caching to avoid repeated file I/O. Cache is module-level variable.
- **Rationale**: Efficient for repeated calls, simple implementation, no startup overhead.
- **Alternatives Considered**:
  - Load at module import time. Rejected because it makes testing harder and adds startup time.
  - Load every time without caching. Rejected due to unnecessary I/O overhead.

## 8. Error Handling

- **Decision**: If base system prompt file is missing or unreadable, fall back to a minimal hardcoded default and log warning.
- **Rationale**: Graceful degradation ensures system continues to work even if file is accidentally deleted.
- **Alternatives Considered**:
  - Fail hard if file missing. Rejected because it breaks the system for a non-critical configuration issue.
