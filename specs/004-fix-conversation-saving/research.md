# Research: Fix Conversation Saving and Project Switching

**Feature**: 004-fix-conversation-saving  
**Date**: 2025-01-27

## Research Tasks

### 1. How to trigger save operation programmatically

**Question**: How do we call the `/save` command function from within the code?

**Findings**:
- The `/save` command is handled in `handle_command()` which returns `special="save"`
- The save logic is executed in the main loop when `special == "save"`
- The save operation calls `index_session(conv_id, override_project=current_project)`
- This is a blocking operation that may take 5-10 seconds (Ollama indexing)

**Decision**: Create a helper function `save_current_conversation(conv_id, current_project)` that directly calls `index_session()` with error handling. This avoids duplicating the save logic and ensures consistency.

**Rationale**: Reusing existing `index_session()` function maintains consistency with manual `/save` behavior. Error handling ensures graceful failure if save doesn't complete.

**Alternatives considered**:
- Duplicating save logic: Rejected - violates DRY principle
- Calling handle_command("/save"): Rejected - would require refactoring command handling

---

### 2. How to create new conversation on project switch

**Question**: When switching projects, should we create a new conversation or update the existing one? What is the exact order of operations?

**Findings**:
- Current behavior: Project switch only changes `current_project` variable, doesn't create new conversation
- Database: `conversations` table has `id`, `title`, `project` columns
- `create_conversation(title, project)` function creates new conversation with new UUID
- Messages are linked to conversation via `conversation_id` foreign key
- User requirement: Exact order must be: (1) save, (2) prompt for title, (3) switch project context, (4) continue

**Decision**: Create a new conversation when switching projects. The exact sequence is: (1) Run `/save` to save current conversation, (2) Prompt user for new title (required, loop until provided), (3) Create new conversation with new title and project, switch project context, (4) Continue conversation with new conversation_id.

**Rationale**: User requirement explicitly states conversations should be stored separately and specifies the exact order. Creating new conversation ensures clean separation. Old conversation is preserved via save operation. Project context switch happens AFTER title is entered, not before.

**Alternatives considered**:
- Update existing conversation project: Rejected - would mix topics from different projects
- Keep same conversation but change project: Rejected - violates requirement for separate storage
- Switch project context before prompting for title: Rejected - violates user's specified order

---

### 3. Title validation approach

**Question**: How should we validate that title is non-empty?

**Findings**:
- Current code: `title = input("Conversation title (blank for default): ").strip()` then checks `if not title:`
- Python `input()` returns empty string if user just presses Enter
- `.strip()` removes whitespace, so "   " becomes ""
- Need to loop until non-empty input provided

**Decision**: Use a while loop that prompts for title until non-empty string is provided. Display "A title is required" message when empty input detected.

**Rationale**: Simple, clear validation. Matches user requirement exactly. No need for complex validation rules.

**Alternatives considered**:
- Allow whitespace-only titles: Rejected - user requirement states title must be non-empty
- Auto-generate title if empty: Rejected - user requirement states title is mandatory

---

### 4. Error handling during auto-save

**Question**: What should happen if save fails during project switch or exit?

**Findings**:
- `index_session()` can raise `OllamaError`, `ValueError`, or generic `Exception`
- Current `/save` command handles errors gracefully, displays error message, continues
- Save failures shouldn't block user from switching projects or exiting

**Decision**: Catch exceptions during auto-save, display warning message, but allow operation to continue (project switch or exit). Log error for debugging.

**Rationale**: User shouldn't be stuck if save fails. Warning message informs user that save didn't complete. Operation can continue since save is a "nice to have" for organization.

**Alternatives considered**:
- Block operation if save fails: Rejected - poor UX, user might be stuck
- Silent failure: Rejected - user should know save didn't complete

---

### 5. Signal handler integration

**Question**: How to handle auto-save in SIGINT (Ctrl+C) signal handler?

**Findings**:
- Current `_signal_handler()` displays usage summary and exits
- Signal handlers should be fast and avoid blocking operations
- `index_session()` is a blocking operation (5-10 seconds)

**Decision**: Call save operation in signal handler, but with timeout or async approach. If save takes too long, display warning and exit anyway. Alternatively, save synchronously but inform user it may take a moment.

**Rationale**: User expects save on exit. Signal handler is appropriate place, but shouldn't block indefinitely. Timeout ensures user can always exit.

**Alternatives considered**:
- Skip save on Ctrl+C: Rejected - violates requirement for auto-save on exit
- Always timeout after 5 seconds: Considered - may be acceptable if save is taking too long

---

## Technical Decisions Summary

1. **Save Helper Function**: Create `save_current_conversation()` helper that calls `index_session()` directly
2. **New Conversation on Switch**: Create new conversation when switching projects, old conversation saved first
3. **Title Validation**: While loop with "A title is required" message for empty input
4. **Error Handling**: Catch exceptions, display warning, but continue operation
5. **Signal Handler**: Call save in signal handler, but consider timeout for long operations

## Implementation Approach

1. Extract save logic into reusable helper function
2. Modify `handle_command()` to trigger save before project switch
3. Modify `/exit` handler to trigger save before exit
4. Modify signal handler to trigger save before exit
5. Add title validation loop in `main()` startup
6. Add title prompt and new conversation creation after project switch

## No Unresolved Clarifications

All technical questions have been resolved. Implementation can proceed to Phase 1 design.

