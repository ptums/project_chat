# Implementation Tasks: OpenAI Usage and Cost Tracking

**Feature**: OpenAI Usage and Cost Tracking  
**Branch**: `001-usage-tracking`  
**Date**: 2025-01-27  
**Spec**: [spec.md](./spec.md)

## Summary

This feature enables tracking and display of OpenAI API usage and cost information when users exit the CLI session, providing transparency into token usage and financial impact.

**Total Tasks**: 25  
**MVP Scope**: Phases 1-3 (User Story 1) - Core usage tracking and summary display (12 tasks)

## Dependencies

### User Story Completion Order

1. **Phase 1 (Setup)** → Must complete first
2. **Phase 2 (Foundational)** → Blocks all user stories
3. **Phase 3 (US1)** → Core functionality - must complete before US2/US3
4. **Phase 4 (US2)** → Depends on US1 (adds detailed token tracking)
5. **Phase 5 (US3)** → Depends on US1 (adds cost calculation)
6. **Phase 6 (Polish)** → Depends on all previous phases

### Parallel Execution Opportunities

- **Phase 4 (US2) + Phase 5 (US3)**: Can be done in parallel (different features - token tracking vs cost calculation)

## Implementation Strategy

**MVP First**: Implement Phases 1-3 (Setup, Foundational, US1) to deliver core usage tracking and summary display. This enables users to see their session usage when exiting.

**Incremental Delivery**: 
- After MVP: Users can see basic usage summary on exit
- Phase 4: Adds detailed token breakdown
- Phase 5: Adds cost calculations
- Phase 6: Polish and edge cases

---

## Phase 1: Setup

**Goal**: Prepare for implementation by understanding OpenAI response structure and pricing information.

**Independent Test**: Verify OpenAI response structure can be accessed and pricing data can be obtained.

### Tasks

- [x] T001 Research OpenAI SDK response structure to identify where usage data is located (response.usage object)
- [x] T002 Research OpenAI model pricing information and create pricing reference data structure

---

## Phase 2: Foundational

**Goal**: Implement core infrastructure for tracking usage data during CLI session.

**Independent Test**: Verify usage data can be extracted from API responses and stored in session.

### Tasks

- [x] T003 Create usage tracking module `brain_core/usage_tracker.py` with session state management
- [x] T004 [P] Implement `UsageRecord` class in `brain_core/usage_tracker.py` to store single API call usage data (prompt_tokens, completion_tokens, total_tokens, model, cost)
- [x] T005 [P] Implement `SessionUsageTracker` class in `brain_core/usage_tracker.py` to aggregate usage across session
- [x] T006 [P] Create model pricing lookup function in `brain_core/usage_tracker.py` to get input/output costs per 1K tokens for different models

---

## Phase 3: User Story 1 - View Session Usage Summary on Exit

**Goal**: Display usage summary when user types `/exit` before program termination.

**Independent Test**: Run CLI, make API calls, type `/exit`, and verify usage summary is displayed with total tokens, cost, and number of calls.

**Acceptance Criteria**:
- Usage summary displays when `/exit` is typed
- Summary shows total tokens, cost estimate, and number of API calls
- Summary handles mock mode (shows zero usage)
- Summary handles no API calls gracefully

### Tasks

- [x] T007 [US1] Extract usage data from OpenAI API response in `brain_core/chat.py` after API call (response.usage.prompt_tokens, response.usage.completion_tokens, response.usage.total_tokens, response.model)
- [x] T008 [US1] Record usage data in session tracker in `brain_core/chat.py` after each successful API call
- [x] T009 [US1] Create `display_usage_summary()` function in `chat_cli.py` to format and display usage report
- [x] T010 [US1] Call `display_usage_summary()` when user types `/exit` in `chat_cli.py` main loop
- [x] T011 [US1] Handle mock mode in usage summary display (show zero usage or indicate mock mode was used)
- [x] T012 [US1] Test usage summary display with multiple API calls to verify aggregation works correctly

---

## Phase 4: User Story 2 - Track Token Usage Per API Call

**Goal**: Track detailed token breakdown (prompt, completion, total) from each API call.

**Independent Test**: Make API calls and verify prompt_tokens, completion_tokens, and total_tokens are tracked accurately.

**Acceptance Criteria**:
- Prompt tokens are tracked from each API call
- Completion tokens are tracked from each API call
- Total tokens are calculated correctly
- Cumulative totals are displayed in summary

### Tasks

- [x] T013 [US2] Enhance usage tracking to store detailed token breakdown per call in `brain_core/usage_tracker.py`
- [x] T014 [US2] Update usage summary display in `chat_cli.py` to show prompt tokens, completion tokens, and total tokens separately
- [x] T015 [US2] Test token tracking with various input/output sizes to verify accuracy

---

## Phase 5: User Story 3 - Calculate and Display Cost Estimates

**Goal**: Calculate and display cost estimates based on OpenAI model pricing.

**Independent Test**: Make API calls with known models and verify cost calculations match expected values.

**Acceptance Criteria**:
- Costs are calculated using model-specific pricing
- Costs are displayed in clear format (dollars/cents)
- Multiple models show cost breakdown by model
- Cost calculations are accurate within 0.1%

### Tasks

- [x] T016 [US3] Implement cost calculation function in `brain_core/usage_tracker.py` using model pricing (input_cost * prompt_tokens/1000 + output_cost * completion_tokens/1000)
- [x] T017 [US3] Update usage summary display in `chat_cli.py` to show cost estimates in formatted currency format
- [x] T018 [US3] Add model breakdown to usage summary if multiple models were used in `chat_cli.py`
- [x] T019 [US3] Test cost calculations with different models to verify pricing accuracy

---

## Phase 6: Polish & Cross-Cutting Concerns

**Goal**: Address edge cases, improve error handling, and ensure production readiness.

**Independent Test**: Test edge cases and verify all error scenarios are handled gracefully.

### Tasks

- [x] T020 Add handling for failed/interrupted API calls (don't track usage for failed calls) in `brain_core/chat.py`
- [x] T021 Add handling for missing usage data in API response (graceful degradation) in `brain_core/chat.py`
- [x] T022 Add handling for unknown models (fallback pricing or clear indication) in `brain_core/usage_tracker.py`
- [x] T023 Add usage summary display on Ctrl+C exit (signal handler) in `chat_cli.py`
- [x] T024 Test with very large token counts to verify formatting and display work correctly
- [x] T025 Verify usage summary displays correctly in both development (mock) and production modes

---

## Task Summary by User Story

- **Setup (Phase 1)**: 2 tasks
- **Foundational (Phase 2)**: 4 tasks
- **User Story 1**: 6 tasks
- **User Story 2**: 3 tasks
- **User Story 3**: 4 tasks
- **Polish (Phase 6)**: 6 tasks

**Total**: 25 tasks

## Parallel Execution Examples

### Example 1: Phase 2 Foundational Tasks
Can be done in parallel:
- Developer A: Works on T004 (UsageRecord class)
- Developer B: Works on T005 (SessionUsageTracker class)
- Developer C: Works on T006 (Model pricing lookup)

No conflicts: Different classes/functions, no dependencies between them.

### Example 2: Phase 4 + Phase 5 (US2 + US3)
Can be done in parallel:
- Developer A: Works on T013-T015 (US2 - detailed token tracking)
- Developer B: Works on T016-T019 (US3 - cost calculation)

No conflicts: Different features, can enhance independently.

## Notes

- OpenAI SDK response includes `response.usage` object with `prompt_tokens`, `completion_tokens`, `total_tokens`
- Model pricing needs to be looked up (can be hardcoded or from config)
- Usage tracking should only happen for successful API calls
- Mock mode should show zero usage or indicate mock mode
- Cost calculations are estimates based on published pricing
- MVP scope (Phases 1-3) delivers core usage tracking and summary display

