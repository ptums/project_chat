# Quickstart: Fix Conversation Saving and Project Switching

## Overview

This feature fixes conversation organization by:
1. Auto-saving conversations when switching projects
2. Auto-saving conversations when exiting
3. Making conversation titles mandatory
4. Prompting for new title when switching projects

## Testing the Feature

### Test 1: Mandatory Title on Startup

```bash
# Start the program
python3 chat_cli.py

# When prompted for title, press Enter without input
Conversation title (required): [press Enter]

# Expected: "A title is required" message, prompt again
# Enter a title
Conversation title (required): My Test Conversation

# Expected: Proceeds to project selection
```

### Test 2: Auto-Save on Project Switch

```bash
# Start conversation in "general"
python3 chat_cli.py
Conversation title (required): Hobbit Discussion
Project tag [general/THN/DAAS/FF/700B] (default: general): general

# Exchange some messages
You (GENERAL) 🔵: Tell me about hobbits
AI (GENERAL) 🔵: [response]

# Switch to THN project
You (GENERAL) 🔵: /thn

# Expected sequence (EXACT ORDER):
# STEP 1: Save current conversation
#   1. "Indexing conversation..." spinner
#   2. "✓ Indexed: Hobbit Discussion [general]"
# STEP 2: Prompt for new title
#   3. "Conversation title for THN (required):" prompt
#   4. Enter title: "Bitcoin Project Ideas"
# STEP 3: Switch to new project context
#   5. "Switched active project context to THN 🟢"
# STEP 4: Continue conversation
#   6. Continue conversation under new project (new conversation_id)
```

### Test 3: Auto-Save on Exit

```bash
# Start conversation and exchange messages
python3 chat_cli.py
Conversation title (required): Test Conversation
Project tag [general/THN/DAAS/FF/700B] (default: general): THN

You (THN) 🟢: Some message
AI (THN) 🟢: [response]

# Exit program
You (THN) 🟢: /exit

# Expected:
# 1. "Indexing conversation..." spinner
# 2. "✓ Indexed: Test Conversation [THN]"
# 3. Usage summary displayed
# 4. "Bye."
# 5. Program exits
```

### Test 4: Auto-Save on Ctrl+C

```bash
# Start conversation and exchange messages
python3 chat_cli.py
Conversation title (required): Test Conversation
Project tag [general/THN/DAAS/FF/700B] (default: general): THN

You (THN) 🟢: Some message
AI (THN) 🟢: [response]

# Press Ctrl+C
[Ctrl+C]

# Expected:
# 1. "Indexing conversation..." spinner
# 2. "✓ Indexed: Test Conversation [THN]"
# 3. Usage summary displayed
# 4. "Exiting."
# 5. Program exits
```

### Test 5: Title Required After Project Switch

```bash
# Start conversation in "general"
python3 chat_cli.py
Conversation title (required): Initial Conversation
Project tag [general/THN/DAAS/FF/700B] (default: general): general

# Exchange messages, then switch project
You (GENERAL) 🔵: /thn

# When prompted for title, press Enter without input
Conversation title for THN (required): [press Enter]

# Expected: "A title is required" message, prompt again
# Enter title
Conversation title for THN (required): New THN Conversation

# Expected: Proceeds with project switch
```

## Implementation Checklist

- [ ] Create `save_current_conversation()` helper function in `chat_cli.py`
- [ ] Modify `handle_command()` to detect project switch and return special flag for project switch flow
- [ ] In main loop, when project switch detected: 
  - [ ] STEP 1: Call `save_current_conversation()` and wait for completion
  - [ ] STEP 2: Prompt for new title (required, loop until non-empty)
  - [ ] STEP 3: Create new conversation with `create_conversation(new_title, new_project)`
  - [ ] STEP 4: Update `conv_id` and `current_project`, display switch message, continue
- [ ] Modify `/exit` handler to call save before exit
- [ ] Modify `_signal_handler()` to call save before exit
- [ ] Add title validation loop in `main()` startup (require non-empty input)
- [ ] Test all scenarios above, verifying exact order of operations

## Key Functions to Modify

### `chat_cli.py`

1. **`save_current_conversation(conv_id, current_project)`** (NEW)
   - Helper function to save conversation
   - Calls `index_session()` with error handling
   - Returns success/failure status

2. **`handle_command(text, current_project, conversation_id)`** (MODIFY)
   - Detect project switch commands
   - Call `save_current_conversation()` before returning new project
   - Return special flag to indicate title prompt needed

3. **`main()`** (MODIFY)
   - Add title validation loop at startup
   - Add title prompt and new conversation creation after project switch
   - Call `save_current_conversation()` before exit

4. **`_signal_handler(signum, frame)`** (MODIFY)
   - Call `save_current_conversation()` before displaying usage summary

## Database Verification

After testing, verify conversations are stored separately:

```sql
-- Check conversations table
SELECT id, title, project, created_at 
FROM conversations 
ORDER BY created_at DESC 
LIMIT 10;

-- Check conversation_index table
SELECT session_id, title, project, indexed_at 
FROM conversation_index 
ORDER BY indexed_at DESC 
LIMIT 10;
```

Expected: Each project switch creates a new conversation record, and each is indexed separately.

