# Feature Specification: Fix API Usage Display and Add Pause Feature

**Feature Branch**: `006-fix-api-usage-and-pause-feature`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: User description: "There is one bug that needs fixing and one minor feature that needs implementing. The API usage details is not showing the correct information when the user hits /exit. When the response is being generated on the screen, sometimes I want to pause the output and go back to typing or rewording a prompt. This is a common function when using chatgpt. There is the pause button and then the edit button to edit the original prompt. I want a simple function that mimics that. I don't need to redit the prompt function, but I would like to pause the response mid text by typing @@"

## User Scenarios & Testing

### User Story 1 - Fix API Usage Display on Exit (Priority: P1)

A user wants to see accurate API usage information when they exit the program, but currently the system shows "No API calls made during this session" even when API calls were made.

**Why this priority**: This is a bug fix - users need accurate usage information to track costs and API consumption.

**Independent Test**: Can be fully tested by running the CLI, making API calls (asking questions), then typing `/exit` and verifying the usage summary shows correct token counts, costs, and API call count.

**Acceptance Scenarios**:

1. **Given** the user makes API calls during a session, **When** they type `/exit`, **Then** the system displays accurate usage summary with total tokens, cost, and API call count
2. **Given** the user makes no API calls during a session, **When** they type `/exit`, **Then** the system displays "No API calls made during this session"
3. **Given** the user makes API calls and then exits, **When** the usage summary is displayed, **Then** it shows the correct number of API calls, total tokens (prompt + completion), and estimated cost

---

### User Story 2 - Pause Streaming Response with @@ (Priority: P2)

A user wants to pause a streaming response mid-generation by typing `@@` so they can interrupt the response and type a new prompt, similar to ChatGPT's pause functionality.

**Why this priority**: This improves user experience by allowing users to stop responses they don't want to wait for and immediately ask a new question.

**Independent Test**: Can be fully tested by running the CLI, asking a question that generates a long response, typing `@@` during streaming, and verifying the response stops and the user can immediately type a new prompt.

**Acceptance Scenarios**:

1. **Given** a streaming response is being generated and displayed, **When** the user types `@@`, **Then** the streaming stops immediately and the user can type a new prompt
2. **Given** the user types `@@` during streaming, **When** the response stops, **Then** any partial response received is saved to the conversation (if any content was received)
3. **Given** the user types `@@` during streaming, **When** the response stops, **Then** the user is immediately returned to the input prompt (You (PROJECT) 🟢:) to type a new message
4. **Given** the user types `@@` when no response is streaming, **When** the system processes the input, **Then** it treats `@@` as regular text (not a command) and sends it as part of the message

---

### Edge Cases

- What happens if user types `@@` at the very beginning of streaming (before first chunk)? (Should stop immediately, no partial response to save)
- What happens if user types `@@` after streaming completes? (Should be treated as regular text, not a pause command)
- What happens if user types `@@` in the middle of a regular message (not during streaming)? (Should be treated as regular text)
- What happens if API usage tracking fails during streaming? (Should still display usage summary, handle gracefully)
- What happens if user exits during streaming? (Should stop streaming, save partial response if any, then show usage summary)

## Requirements

### Functional Requirements

- **FR-001**: System MUST display accurate API usage summary when user types `/exit`
- **FR-002**: System MUST show correct API call count, token counts (prompt, completion, total), and estimated cost in usage summary
- **FR-003**: System MUST handle case where no API calls were made (display "No API calls made during this session")
- **FR-004**: System MUST allow user to pause streaming response by typing `@@` during response generation
- **FR-005**: System MUST stop streaming immediately when `@@` is detected
- **FR-006**: System MUST save any partial response content received before pause
- **FR-007**: System MUST return user to input prompt immediately after pause
- **FR-008**: System MUST treat `@@` as regular text when not during streaming (allow it in messages)

### Key Entities

- **SessionUsageTracker**: Tracks API usage data for the entire CLI session. Must correctly aggregate usage from all API calls.
- **Streaming Response**: Progressive text display that can be interrupted by user input.
- **Usage Summary**: Display of aggregated usage data shown on exit.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Usage summary on `/exit` shows correct API call count matching actual calls made
- **SC-002**: Usage summary on `/exit` shows correct token counts (prompt + completion = total)
- **SC-003**: Usage summary on `/exit` shows correct estimated cost based on model pricing
- **SC-004**: User can pause streaming response by typing `@@` within 1 second of typing
- **SC-005**: Streaming stops immediately (within 100ms) when `@@` is detected
- **SC-006**: Partial responses are saved correctly when streaming is paused
- **SC-007**: User can immediately type new prompt after pausing (no delay or hanging)

