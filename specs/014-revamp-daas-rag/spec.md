# Feature Specification: Revamp DAAS RAG System

**Feature ID**: `014-revamp-daas-rag`  
**Date**: 2025-01-27  
**Status**: Planning

## Overview

Revamp the DAAS (Dream Analysis and Symbolism) RAG system to provide a focused, cost-effective retrieval system that enriches dream analysis without confusing conversation history. The new system will retrieve related DAAS-embedded data by themes, symbols, or events to provide symbolic parallels and deeper meaning while keeping each dream's events separate and self-contained.

## Requirements

### Functional Requirements

1. **Remove Current DAAS RAG Implementation**

   - Remove `daas_retrieval.py` file and all its functions
   - Remove DAAS-specific retrieval logic from `build_project_context()` in `context_builder.py`
   - Remove single-dream mode and pattern-based mode implementations
   - Clean up any DAAS-specific retrieval code that uses conversation history

2. **Implement New DAAS RAG System**

   **Core Principles:**

   - Retrieve related DAAS-embedded data by themes, symbols, or events
   - Highlight symbolic parallels or contrasts without merging dream events
   - Keep each dream's events, characters, and timelines separate and self-contained
   - Compare symbols and themes only at the conceptual level
   - Integrate DAAS's multitradition framework naturally
   - Limit retrieval strictly to DAAS-tagged data (no outside references)
   - Provide concise, thoughtful guidance without over-explaining
   - If no relevant retrieval results, focus on unique details of current dream

   **Retrieval Strategy:**

   - Use vector similarity search on `conversation_index` table for DAAS project
   - Search by themes, symbols, or events from the current dream/query
   - Return top-k relevant dreams (configurable, default: 3-5)
   - Format retrieved dreams with clear separation and boundaries
   - Include only essential fields: title, key themes, symbols, summary

3. **Remove Debugging Messages**

   - Remove "Thinking for [PROJECT]" spinner messages from `chat_cli.py`
   - Remove or reduce verbose logging during RAG generation
   - Keep only essential error logging

4. **Cost Optimization**

   - Limit retrieved content to essential information only
   - Truncate long summaries or memory snippets
   - Use efficient vector search queries
   - Consider token limits when formatting RAG context

### Non-Functional Requirements

1. **Performance**

   - RAG generation should complete in <500ms (similar to THN RAG target)
   - Vector similarity search should use existing indexes

2. **Token Efficiency**

   - Keep RAG context concise (target: <1000 tokens)
   - Truncate retrieved content appropriately
   - Avoid redundant information

3. **Maintainability**
   - Clear separation between DAAS RAG and other project RAG systems
   - Well-documented retrieval logic
   - Easy to adjust retrieval parameters

## Design Constraints

1. **No Conversation History in RAG**

   - Do not include conversation history in RAG context
   - Focus only on dream data from `conversation_index` table
   - Keep dream analysis focused and unconfused

2. **DAAS-Only Data**

   - Strictly limit retrieval to DAAS-tagged entries
   - No cross-project data retrieval
   - No external references

3. **Dream Separation**
   - Each retrieved dream must be clearly separated
   - No merging of dream events or timelines
   - Maintain clear boundaries between dreams

## Integration Points

1. **`build_project_context()` in `context_builder.py`**

   - Replace DAAS retrieval logic with new implementation
   - Follow pattern similar to THN RAG but with DAAS-specific rules

2. **`chat_cli.py`**

   - Remove "Thinking for [PROJECT]" spinner messages
   - Ensure smooth user experience without debugging noise

3. **Database**
   - Use existing `conversation_index` table with DAAS project filter
   - Leverage existing embedding indexes for vector search

## Success Criteria

1. ✅ Old DAAS RAG code completely removed
2. ✅ New DAAS RAG retrieves relevant dreams by themes/symbols/events
3. ✅ Retrieved dreams are clearly separated and self-contained
4. ✅ No conversation history included in RAG
5. ✅ Debugging messages removed from chat interface
6. ✅ RAG generation completes in <500ms
7. ✅ Token usage is optimized (<1000 tokens for RAG context)
