# CLI Contracts: Fix Conversation Saving and Project Switching

## Project Switch Commands

### `/thn`, `/daas`, `/ff`, `/700b`, `/general`

**Purpose**: Switch active project context. Now includes auto-save before switch.

**Request Flow** (EXACT ORDER):
1. User types project switch command (e.g., `/thn`)
2. System detects project switch in `handle_command()`
3. **STEP 1: Save current conversation**
   - System calls `save_current_conversation(conv_id, current_project)` → `index_session(conv_id)`
   - Wait for save to complete (with spinner/feedback)
4. **STEP 2: Prompt for new title**
   - System prompts "Conversation title for [PROJECT] (required):"
   - User must provide non-empty title (loops until provided)
   - System validates title is non-empty
5. **STEP 3: Switch to new project context**
   - System calls `create_conversation(new_title, new_project)`
   - System updates `conv_id` to new conversation UUID
   - System updates `current_project` to new project
   - System displays "Switched active project context to [PROJECT] [emoji]"
6. **STEP 4: Continue conversation**
   - Conversation continues with new conversation_id and new project context
   - All subsequent messages are linked to the new conversation

**Success Output** (stdout):
```
Indexing conversation...
✓ Indexed: [title] [[project]]
Conversation title for THN (required): [user input]
Switched active project context to THN 🟢
```

**Error Handling**:
- If save fails: Display warning "⚠ Save failed: [error]", but continue with project switch
- If title is empty: Display "A title is required" and prompt again
- If save times out: Display warning "⚠ Save timed out", but continue with project switch

**Side Effects**: 
- Old conversation is indexed and saved to `conversation_index`
- New conversation record created in `conversations` table
- `conv_id` variable updated to new conversation UUID
- Messages after switch are linked to new conversation

---

### `/project TAG`

**Purpose**: Switch active project context using explicit project tag. Same behavior as project-specific commands.

**Request Flow**: Same as `/thn` etc.

**Success Output**: Same as `/thn` etc.

**Error Handling**: Same as `/thn` etc.

---

## Exit Commands

### `/exit`

**Purpose**: Exit the program. Now includes auto-save before exit.

**Request Flow**:
1. User types `/exit`
2. System calls `save_current_conversation(conv_id, current_project)` → `index_session(conv_id)`
3. System displays usage summary
4. System displays "Bye."
5. Program exits

**Success Output** (stdout):
```
Indexing conversation...
✓ Indexed: [title] [[project]]
[Usage summary]
Bye.
```

**Error Handling**:
- If save fails: Display warning "⚠ Save failed: [error]", but continue with exit
- If save times out: Display warning "⚠ Save timed out", but continue with exit

**Side Effects**: 
- Current conversation is indexed and saved to `conversation_index`
- Program exits

---

### Ctrl+C (SIGINT)

**Purpose**: Exit the program via interrupt signal. Now includes auto-save before exit.

**Request Flow**:
1. User presses Ctrl+C
2. Signal handler `_signal_handler()` is called
3. System calls `save_current_conversation(conv_id, current_project)` → `index_session(conv_id)`
4. System displays usage summary
5. System displays "Exiting."
6. Program exits

**Success Output** (stdout):
```
Indexing conversation...
✓ Indexed: [title] [[project]]
[Usage summary]
Exiting.
```

**Error Handling**:
- If save fails: Display warning "⚠ Save failed: [error]", but continue with exit
- If save times out: Display warning "⚠ Save timed out", but continue with exit
- Consider timeout (5-10 seconds) to avoid blocking exit indefinitely

**Side Effects**: 
- Current conversation is indexed and saved to `conversation_index`
- Program exits

---

## Startup Flow

### Title Input (NEW - Required)

**Purpose**: Get conversation title from user. Title is now mandatory.

**Request Flow**:
1. Program starts, displays banner
2. System prompts "Conversation title (required):"
3. User enters title (or presses Enter)
4. If title is empty (after `.strip()`): Display "A title is required" and prompt again
5. Loop until non-empty title provided
6. System proceeds to project selection

**Success Output** (stdout):
```
Conversation title (required): [user input]
Project tag [general/THN/DAAS/FF/700B] (default: general): [user input]
```

**Error Handling**:
- If user presses Enter without input: Display "A title is required" and prompt again
- If user enters only whitespace: Treated as empty, prompt again
- If user cancels (Ctrl+C): Exit program (existing behavior)

**Side Effects**: None (title stored for conversation creation)

---

## Helper Functions

### `save_current_conversation(conv_id: UUID, current_project: str) -> bool`

**Purpose**: Save current conversation by calling indexing function.

**Implementation**:
- Calls `index_session(conv_id, override_project=current_project)`
- Handles exceptions gracefully
- Returns `True` if save succeeded, `False` if failed
- Displays spinner during save operation
- Displays success/error messages

**Error Handling**:
- Catches `OllamaError`: Returns `False`, logs error
- Catches `ValueError`: Returns `False`, logs error
- Catches generic `Exception`: Returns `False`, logs error
- Always displays user-friendly error message

**Side Effects**: 
- Updates `conversation_index` table
- May update `conversations.project` if conversation was "general" and override_project is specific

