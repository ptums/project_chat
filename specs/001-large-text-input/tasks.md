# Implementation Tasks: Large Text Input Support

**Feature**: Large Text Input Support  
**Branch**: `001-large-text-input`  
**Date**: 2025-01-27  
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Summary

This feature enables large text input support in CLI and API by removing character limits and implementing proper input handling for text blocks up to 100,000+ characters.

**Total Tasks**: 22  
**MVP Scope**: Phases 1-3 (User Story 1) - Core large text input functionality (11 tasks)

## Dependencies

### User Story Completion Order

1. **Phase 1 (Setup)** → Must complete first
2. **Phase 2 (Foundational)** → Blocks all user stories
3. **Phase 3 (US1)** → Core functionality - must complete before US2/US3
4. **Phase 4 (US2)** → Depends on US1 (enhances normal input)
5. **Phase 5 (US3)** → Depends on US1 (adds feedback)
6. **Phase 6 (Polish)** → Depends on all previous phases

### Parallel Execution Opportunities

- **Phase 3 (US1) CLI + API**: Can be done in parallel (different files, no dependencies)
- **Phase 4 (US2) + Phase 5 (US3)**: Can be done in parallel (different features)

## Implementation Strategy

**MVP First**: Implement Phases 1-3 (Setup, Foundational, US1) to deliver core large text input functionality. This enables users to paste large text blocks without truncation.

**Incremental Delivery**: 
- After MVP: Users can paste large text in `/paste` mode and via API
- Phase 4: Enhances normal input mode
- Phase 5: Adds user feedback
- Phase 6: Polish and edge cases

---

## Phase 1: Setup

**Goal**: Prepare for implementation by understanding current limitations and testing approach.

**Independent Test**: Verify current input limitations can be identified and test cases can be created.

### Tasks

- [x] T001 Investigate current text input limitations in `chat_cli.py` by testing with large text blocks to identify truncation points
- [x] T002 Create test file with large text sample (10,000+ characters) for testing large input functionality in `/Users/petertumulty/Documents/Sites/overclockai/week2/project_chat/test_large_input.txt`

---

## Phase 2: Foundational

**Goal**: Implement core infrastructure for large text reading using standard library.

**Independent Test**: Verify `sys.stdin.read()` can be used to read large text blocks without truncation.

### Tasks

- [x] T003 [P] Create helper function `read_large_text_block()` in `chat_cli.py` using `sys.stdin.read()` to read text until EOF or end token
- [x] T004 [P] Add error handling to `read_large_text_block()` for EOF, cancellation (Ctrl+C), and encoding issues in `chat_cli.py`
- [x] T005 [P] Add type hints to `read_large_text_block()` function in `chat_cli.py` for better code clarity

---

## Phase 3: User Story 1 - Paste Large Text Blocks Without Truncation

**Goal**: Enable `/paste` mode to accept large text blocks without any truncation.

**Independent Test**: Paste a 10,000+ character text block using `/paste` and verify entire content is captured and processed without truncation.

**Acceptance Criteria**:
- `/paste` mode captures text blocks of 10,000+ characters completely
- Text blocks of 50,000+ characters are handled without errors
- All text content including newlines and special characters is preserved
- User receives confirmation when large text is received

### Tasks

- [x] T006 [US1] Fix bug in `read_multiline_block()` function in `chat_cli.py` - ensure all lines are captured correctly (verify line 124 logic)
- [x] T007 [US1] Replace `read_multiline_block()` implementation in `chat_cli.py` to use `sys.stdin.read()` for large text blocks instead of line-by-line `input()`
- [x] T008 [US1] Update `read_multiline_block()` in `chat_cli.py` to handle EOF (Ctrl+D) and end token ("EOF") detection correctly for large pastes
- [x] T009 [US1] Add character count feedback in `chat_cli.py` when large text is received in paste mode (e.g., "Received X characters. Processing...")
- [x] T010 [US1] Configure Flask `MAX_CONTENT_LENGTH` in `api_server.py` to allow large text payloads (set to 16MB or higher)
- [x] T011 [US1] Test `/paste` mode with large text blocks (10,000+, 50,000+ characters) to verify no truncation occurs

---

## Phase 4: User Story 2 - Support Large Text in Normal Input Mode

**Goal**: Enable normal input mode to accept large text pastes without requiring `/paste` command.

**Independent Test**: Paste a large text block directly at the normal prompt and verify it is captured completely.

**Acceptance Criteria**:
- Normal input mode detects and handles large pastes automatically
- Large text pasted at normal prompt is captured completely
- Special characters and formatting are preserved
- User experience is seamless (no need to use `/paste` for large normal inputs)

### Tasks

- [x] T012 [US2] Add detection logic in `chat_cli.py` main loop to identify large pastes in normal input (check for newlines or length threshold)
- [x] T013 [US2] Implement automatic multiline reading in `chat_cli.py` when large paste is detected in normal input mode
- [x] T014 [US2] Test normal input mode with large text pastes to verify automatic detection and capture works correctly

---

## Phase 5: User Story 3 - Clear Feedback for Large Input Processing

**Goal**: Provide clear feedback to users when processing large text inputs.

**Independent Test**: Submit a large text block and verify appropriate feedback is provided about input size and processing status.

**Acceptance Criteria**:
- Users see character count or size indicator when large text is received
- Processing status is clearly communicated
- Feedback helps users understand system is handling their content

### Tasks

- [x] T015 [US3] Enhance feedback messages in `chat_cli.py` to show character count for inputs over 1000 characters
- [x] T016 [US3] Add processing status messages in `chat_cli.py` for large text inputs (e.g., "Processing large input (X characters)...")
- [x] T017 [US3] Test feedback messages with various input sizes to ensure appropriate messaging

---

## Phase 6: Polish & Cross-Cutting Concerns

**Goal**: Address edge cases, improve error handling, and ensure production readiness.

**Independent Test**: Test edge cases and verify all error scenarios are handled gracefully.

### Tasks

- [x] T018 Add validation for text encoding (UTF-8) in `chat_cli.py` with clear error messages for invalid encoding
- [x] T019 Test cancellation handling (Ctrl+C) during large text input in `chat_cli.py` to ensure graceful exit
- [x] T020 Test with extremely large text blocks (100,000+ characters) to verify memory handling and performance
- [x] T021 Verify all special characters, newlines, and formatting are preserved in both CLI and API inputs
- [x] T022 Test API endpoint with large text payloads to verify Flask configuration works correctly

---

## Task Summary by User Story

- **Setup (Phase 1)**: 2 tasks
- **Foundational (Phase 2)**: 3 tasks
- **User Story 1**: 6 tasks
- **User Story 2**: 3 tasks
- **User Story 3**: 3 tasks
- **Polish (Phase 6)**: 5 tasks

**Total**: 22 tasks

## Parallel Execution Examples

### Example 1: Phase 3 CLI + API (US1)
Can be done in parallel:
- Developer A: Works on T006-T009 (CLI paste mode improvements)
- Developer B: Works on T010 (API configuration)

No conflicts: Different files, no dependencies between them.

### Example 2: Phase 4 + Phase 5 (US2 + US3)
Can be done in parallel:
- Developer A: Works on T012-T014 (US2 - normal input enhancement)
- Developer B: Works on T015-T017 (US3 - feedback improvements)

No conflicts: Different features, can enhance independently.

## Notes

- Critical bug identified: `read_multiline_block()` may have issues with large text due to line-by-line reading
- Solution uses standard library (`sys.stdin`) - no new dependencies
- Database already supports large text (TEXT field) - no schema changes needed
- API endpoint already accepts text strings - just needs Flask configuration
- MVP scope (Phases 1-3) delivers core functionality for large text input

