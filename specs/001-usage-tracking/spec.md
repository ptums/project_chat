# Feature Specification: OpenAI Usage and Cost Tracking

**Feature Branch**: `001-usage-tracking`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: User description: "Since I am using Open AI SDK and it costs me money. I would like to keep abreast with the impact of the session on my billing and token usage. So when I type /exit before the program ends. I want to be able to get a small report on the usage details. I'm a bit ignorant on what impacts spending usage so please a list of all the important details available in Open AI SDK about usage and cost before the program exits."

## User Scenarios & Testing _(mandatory)_

### User Story 1 - View Session Usage Summary on Exit (Priority: P1)

As a user, I want to see a summary of my OpenAI API usage and costs for the current CLI session when I type `/exit`, so that I can understand the financial impact of my session before the program ends.

**Why this priority**: This is the core requirement - users need visibility into their API costs to manage spending. Without this, users have no way to track costs during development and usage.

**Independent Test**: Can be fully tested by running the CLI, making several API calls, then typing `/exit` and verifying a usage summary is displayed. This delivers immediate value by providing cost transparency.

**Acceptance Scenarios**:

1. **Given** I have made multiple API calls during a CLI session, **When** I type `/exit`, **Then** I see a summary report showing total tokens used, cost estimate, and number of API calls
2. **Given** I have made no API calls (or only used mock mode), **When** I type `/exit`, **Then** I see a message indicating no API usage or that mock mode was used
3. **Given** I have used different models during the session, **When** I type `/exit`, **Then** I see usage broken down by model if applicable
4. **Given** I exit the program via Ctrl+C or other method, **When** the program terminates, **Then** I see the usage summary if available

---

### User Story 2 - Track Token Usage Per API Call (Priority: P2)

As a user, I want the system to track token usage from each OpenAI API call, so that I can see detailed breakdown of prompt tokens, completion tokens, and total tokens used.

**Why this priority**: Understanding token breakdown helps users understand what drives costs (input size vs output size). This is secondary to the summary but provides valuable detail.

**Independent Test**: Can be fully tested by making API calls and verifying token counts are tracked correctly. This delivers detailed cost insights.

**Acceptance Scenarios**:

1. **Given** I make an API call with a large input, **When** the response is received, **Then** prompt tokens are tracked accurately
2. **Given** I receive a long response from the API, **When** the response is processed, **Then** completion tokens are tracked accurately
3. **Given** I make multiple API calls, **When** I view the summary, **Then** I see cumulative totals for prompt, completion, and total tokens

---

### User Story 3 - Calculate and Display Cost Estimates (Priority: P2)

As a user, I want to see cost estimates for my API usage based on current OpenAI pricing, so that I can understand the financial impact in dollars/cents.

**Why this priority**: Token counts alone don't tell users the cost - they need dollar amounts to understand spending. This is essential for cost management.

**Independent Test**: Can be fully tested by making API calls and verifying cost calculations match expected values based on model pricing. This delivers financial transparency.

**Acceptance Scenarios**:

1. **Given** I use a specific model (e.g., gpt-4), **When** I view the usage summary, **Then** I see cost calculated using that model's pricing
2. **Given** I use multiple models in one session, **When** I view the summary, **Then** I see costs broken down by model
3. **Given** I view the cost estimate, **When** I see the amount, **Then** it is displayed in a clear format (e.g., "$0.05" or "$0.0012")

---

### Edge Cases

- What happens when the session has no API calls (all mock mode or no interactions)?
- How does the system handle API calls that fail or are interrupted?
- What happens if usage data cannot be retrieved from an API response?
- How does the system handle different OpenAI models with different pricing?
- What happens if pricing information is not available for a model?
- How does the system handle very large token counts (millions of tokens)?
- What happens if the user exits via Ctrl+C instead of `/exit`?

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: System MUST track token usage from each OpenAI API call during the CLI session
- **FR-002**: System MUST extract and store prompt_tokens, completion_tokens, and total_tokens from each API response
- **FR-003**: System MUST calculate cost estimates based on OpenAI model pricing (input and output token costs)
- **FR-004**: System MUST display a usage summary when user types `/exit` before program termination
- **FR-005**: System MUST display total tokens used (prompt + completion) for the session
- **FR-006**: System MUST display total cost estimate for the session
- **FR-007**: System MUST display number of API calls made during the session
- **FR-008**: System MUST display model name(s) used during the session
- **FR-009**: System MUST handle cases where usage data is not available (e.g., mock mode, failed calls)
- **FR-010**: System MUST display usage summary in a clear, readable format
- **FR-011**: System MUST track usage only for successful API calls (exclude failed/interrupted calls)
- **FR-012**: System MUST support different OpenAI models with their respective pricing structures

### Key Entities _(include if feature involves data)_

- **Usage Record**: Represents a single API call's usage data, including prompt_tokens, completion_tokens, total_tokens, model name, timestamp, and calculated cost.

- **Session Summary**: Aggregated usage data for the entire CLI session, including total tokens, total cost, number of calls, and model breakdown.

- **Model Pricing**: Pricing information for OpenAI models, including input token cost and output token cost per 1K tokens.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: Users can view their session usage summary 100% of the time when typing `/exit` (if API calls were made)
- **SC-002**: Cost estimates are accurate within 0.1% of actual OpenAI billing (based on published pricing)
- **SC-003**: Usage summary displays all key metrics (tokens, cost, calls, model) in under 2 seconds
- **SC-004**: System correctly tracks usage for 100% of successful API calls
- **SC-005**: Users can understand their session costs without needing external tools or documentation
- **SC-006**: Usage summary is displayed even if program exits via Ctrl+C or other interruption methods

## Assumptions

- OpenAI API responses include `usage` object with token counts (standard OpenAI SDK behavior)
- Model pricing is available and can be looked up (either hardcoded or from configuration)
- Users primarily care about session-level totals, not per-call details (though per-call may be available)
- Cost estimates are approximations based on published pricing (actual billing may vary slightly)
- Mock mode usage should be clearly indicated as having zero cost
- The summary should be concise but informative (not overwhelming with details)

## Dependencies

- Existing OpenAI SDK integration (`brain_core/chat.py`)
- Existing CLI exit handling (`chat_cli.py`)
- OpenAI API response structure (usage object availability)

## Out of Scope

- Historical usage tracking across multiple sessions
- Per-project or per-conversation usage breakdown
- Real-time usage display during the session (only on exit)
- Integration with OpenAI billing API
- Usage alerts or spending limits
- Exporting usage data to files
- Per-message token counting (only API call level)
