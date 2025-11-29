# Research: OpenAI Usage and Cost Tracking

**Feature**: OpenAI Usage and Cost Tracking  
**Date**: 2025-01-27  
**Status**: Complete

## Research Summary

No critical unknowns identified. Solution uses existing OpenAI SDK response structure and standard Python patterns for in-memory session tracking.

## Technical Decisions

### Decision 1: Extract Usage Data from OpenAI API Response

**Decision**: Extract usage data from `response.usage` object after each API call in `brain_core/chat.py`.

**Rationale**:
- OpenAI SDK response includes `response.usage` object with `prompt_tokens`, `completion_tokens`, `total_tokens`
- Standard SDK behavior - no additional API calls needed
- Available immediately after API call completes
- Aligns with constitution principle of "Simple Solutions"

**Alternatives Considered**:
- Query OpenAI billing API: More complex, requires additional API calls, not needed for session-level tracking
- Estimate tokens from message length: Less accurate, doesn't match actual billing

### Decision 2: In-Memory Session Tracking

**Decision**: Track usage data in-memory using a session-level tracker object, no database persistence.

**Rationale**:
- Session-level tracking only (per spec requirement)
- No need for persistence across sessions
- Simple implementation - standard Python classes
- Minimal memory overhead
- Aligns with constitution principle of "Simple Solutions" and "Rapid Development"

**Alternatives Considered**:
- Database persistence: Overkill for session-only tracking, adds complexity
- File-based persistence: Not needed per spec (out of scope: historical tracking)

### Decision 3: Hardcoded Model Pricing Lookup

**Decision**: Use hardcoded dictionary of model pricing (input/output costs per 1K tokens) in `usage_tracker.py`.

**Rationale**:
- Simple and fast lookup
- Pricing changes infrequently
- No external dependencies
- Can be updated easily when pricing changes
- Aligns with constitution principle of "Simple Solutions"

**Alternatives Considered**:
- Configuration file: More complex, not needed for infrequent pricing updates
- API-based pricing lookup: Requires additional API calls, adds complexity
- Environment variables: More complex setup, pricing is stable

### Decision 4: Display Summary on Exit Only

**Decision**: Display usage summary only when user types `/exit` or program terminates (Ctrl+C), not during session.

**Rationale**:
- Per spec requirement (out of scope: real-time display)
- Reduces noise during active use
- Summary is most useful at session end
- Simple implementation - single display function
- Aligns with constitution principle of "Simple Solutions"

**Alternatives Considered**:
- Real-time display: Not in scope, adds complexity
- Per-call display: Too noisy, not requested

### Decision 5: Handle Mock Mode Explicitly

**Decision**: Track mock mode separately and display zero usage or indicate mock mode was used.

**Rationale**:
- Mock mode doesn't make API calls, so no usage data
- Users should know when they're in development mode
- Clear indication prevents confusion
- Aligns with constitution principle of "No Silent Failures"

**Alternatives Considered**:
- Skip tracking in mock mode: Less informative, users might wonder why no data
- Fake usage data: Misleading, violates accuracy principle

### Decision 6: Cost Calculation Formula

**Decision**: Calculate cost as `(input_cost_per_1k * prompt_tokens / 1000) + (output_cost_per_1k * completion_tokens / 1000)`.

**Rationale**:
- Standard OpenAI pricing model (per 1K tokens)
- Matches actual billing calculation
- Simple arithmetic
- Accurate within 0.1% per SC-002 requirement
- Aligns with constitution principle of "Accuracy"

**Alternatives Considered**:
- Per-token calculation: More precise but unnecessary (OpenAI bills per 1K tokens)
- Rounded calculation: Less accurate, violates SC-002

## Implementation Notes

- OpenAI SDK response structure: `response.usage.prompt_tokens`, `response.usage.completion_tokens`, `response.usage.total_tokens`, `response.model`
- Usage data is always present in successful API responses (standard SDK behavior)
- Model pricing needs to be maintained manually (pricing changes infrequently)
- Session tracker should be initialized at CLI startup and accessible throughout session
- Display function should format numbers with commas and currency with appropriate precision

## No Critical Unknowns

All technical decisions are straightforward:
- OpenAI SDK response structure is well-documented
- In-memory tracking is standard Python pattern
- Cost calculation is simple arithmetic
- Display formatting is standard string formatting

No additional research needed.

