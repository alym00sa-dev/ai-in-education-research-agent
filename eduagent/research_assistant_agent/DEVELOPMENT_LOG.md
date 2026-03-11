# EDU Deep Research Agent — Development Log

## Overview

This document tracks the major work completed on the EDU Deep Research Agent — a Streamlit-based multi-mode research tool that synthesizes academic literature using LangGraph-powered deep research, Neo4j knowledge graph storage, and LLM-based structured extraction.

---

## Codebase Architecture

```
research_assistant_agent/
├── app.py                          # Streamlit entry point (st.navigation multipage)
├── pages/
│   └── research_agent.py           # Main page — all modes dispatched here
├── src/
│   ├── pipeline/                   # Deep research engine (mode-agnostic)
│   │   ├── orchestrator.py         # Async ResearchPipeline orchestrator
│   │   ├── langgraph_client.py     # LangGraph HTTP client (streaming + batch)
│   │   ├── sync_wrapper.py         # Sync bridge for Streamlit context
│   │   └── prompts.py              # OUTLINE_PROMPT, CLARIFY_PROMPT
│   ├── deep_guided/                # Deep Guided mode connector
│   │   ├── config_schema.py        # ResearchGoal, TechConfig, Codebook dataclasses
│   │   ├── goal_agent.py           # Goal discovery chat + codebook generation agent
│   │   ├── pdf_ingester.py         # PDF bytes → text extraction
│   │   ├── multi_goal_runner.py    # Parallel goal runner (stub, ready to wire)
│   │   ├── prompts.py              # Goal chat, codebook, PDF annotation prompts
│   │   └── ui.py                   # Full 7-step Deep Guided UI
│   ├── exports.py                  # Word (.docx) + JSON audit trail export
│   ├── kg_extractor.py             # LLM-based structured paper extraction → Neo4j
│   ├── session_manager.py          # Neo4j session lifecycle management
│   ├── neo4j_config.py             # Neo4j connection + controlled vocabularies
│   └── research_pipeline.py        # Shim (re-exports from src/pipeline/)
```

---

## Work Completed

### Phase 1 — Codebase Modularization

**Goal:** Split the monolithic `research_pipeline.py` into a clean `src/pipeline/` package.

- Created `src/pipeline/` with `orchestrator.py`, `langgraph_client.py`, `sync_wrapper.py`, `prompts.py`
- `src/research_pipeline.py` converted to a thin shim for backwards compatibility
- `src/exports.py` created for Word and JSON export utilities
- `src/session_manager.py` updated to import from new paths

### Phase 2 — Live Streaming Research View

**Goal:** Replace the blocking research call with a real-time streaming UI.

**LangGraph streaming (`langgraph_client.py`):**
- `stream_open_deep_research()` — async generator using `httpx` with `stream_mode: ["values", "events"]`
- Event types yielded: `section_start`, `section_end`, `sub_researcher_start`, `sub_researcher_done`, `thought`, `token`, `result`, `error`, `done`
- Sub-researcher topics extracted from `supervisor_tools` `on_chain_start` input state (ConductResearch tool calls)
- `compress_research` `on_chain_end` → `sub_researcher_done`
- `think_tool` `on_tool_start` → `thought` events

**Sync bridge (`sync_wrapper.py`):**
- Thread + queue pattern: async generator runs in `asyncio.run()` daemon thread, events passed via `queue.Queue` to Streamlit's sync context

**Streaming UI (`pages/research_agent.py`):**
- User query bubble at top
- System Setup expander (supervisor thoughts)
- Per-sub-researcher expanders with first-person narration ("I'm investigating: [topic]")
- Final Report expander with live token streaming
- "Saving to database" status shown inside Final Report expander (not as separate spinner)
- Clean white-screen transition: `st.empty()` + `_clear = [st.empty() for _ in range(11)]` to atomically replace construction screen

### Phase 3 — Results View Refinements

- Removed Data Extraction tab; summary table moved to bottom of Report tab
- Two tabs: **Report** (full markdown + summary table + downloads) and **Thought Log** (replay of all streaming sections)
- Word export (`.docx`) and audit trail (`.json`) download buttons
- Summary table columns: Title, Year, Study Design, Population, Outcome, Study Measure, Finding Direction, Effect Size, Study Size
- Fixed `orchestrator._finalize()` to include all `StructuredPaper` fields (`year`, `venue`, `population`, `user_type`, `study_design`) in the returned dict — previously these were missing, causing empty columns
- Fixed sidebar session loading to include the same fields when building structured_papers from Neo4j history
- Removed `population` fallback to `objective` extractor

### Phase 4 — Multi-Mode Architecture

**Goal:** Add Deep Guided and Strategic Canvas modes under a single-page dispatch pattern.

**Mode dispatch (`pages/research_agent.py`):**
- Sidebar mode selector drives all rendering — no new pages created
- Shared header (title → mode-specific callout → progress tracker → divider) renders on every mode/step
- Each mode's content renders below the shared header

**Shared header:**
- `st.title("📚 EDU Deep Research Agent")` always visible
- Mode-specific `st.info` callout (explains the mode + what to do on step 1)
- Mode-appropriate progress tracker: Default = 4-step blue, Deep Guided = 7-step purple
- Sidebar: "under development" notice as `st.info` + mode-specific caption under the mode selector

**Deep Guided mode (`src/deep_guided/`):**

7-step flow:
1. **Goals** — True multi-turn chat with a goal advisor agent. User describes intent → agent asks clarifying questions → proposes 3–5 goals → user edits and accepts
2. **Config** — Static form: research model, search depth, evidence hierarchy, source domains, citation scoring weights (sliders)
3. **Codebook** — Agent generates scoring rubric + per-goal research directions. One-shot with edit: user edits inline or types a reclarification note to regenerate
4. **Sources** — Optional PDF upload. Agent can auto-annotate each study with context about how it should inform the research
5. **Review** — Summary of all goals, config, and codebook preview before launch
6. **Research** — Per-goal streaming UI (stub — parallel runner interface defined, ready to wire)
7. **Results** — Unified report + 3 downloads: Full Report (.docx), Audit Trail (.json), Codebook (.json) — codebook download available immediately

**Key `src/deep_guided/` components:**
- `config_schema.py` — `ResearchGoal`, `TechConfig`, `Codebook`, `SupplementaryStudy`, `DeepGuidedSession` dataclasses
- `goal_agent.py` — `GoalAgent` with `chat_turn()`, `parse_proposed_goals()`, `generate_codebook()`, `annotate_pdf()` — all use the same `_run(coro)` async bridge as `SyncResearchPipeline`
- `multi_goal_runner.py` — `build_goal_query()` fully implemented (composes goal + codebook + supplementary study context into one query string); `run_goals_parallel()` stubbed with implementation notes

---

## Pending / Next Steps

### Deep Guided — Wire Parallel Runner
- Implement `run_goals_parallel()` in `src/deep_guided/multi_goal_runner.py`
- Pattern: one `thread+queue` bridge per goal (same as `SyncResearchPipeline.stream_research`)
- Main loop polls all queues in round-robin, yields events tagged with `goal_id`
- Finalization: merge per-goal results into one unified report

### Strategic Canvas Mode
- Chat-first interface: user states a strategic intent
- Agent decomposes into research questions through back-and-forth
- Agent pressure-tests framing, surfaces evidence per question
- Output: conversational + exportable strategy document (goals → research translations → supporting evidence)
- Infrastructure pattern: same connector model as `src/deep_guided/`

---

## Key Technical Decisions

| Decision | Rationale |
|---|---|
| Single page (`research_agent.py`) for all modes | Avoids page reload on mode switch; shared header stays stable |
| `src/pipeline/` mode-agnostic | Deep research engine has no knowledge of modes; connectors wrap it |
| Thread + queue bridge for streaming | Streamlit is sync; LangGraph streaming is async — daemon thread + queue is the cleanest bridge |
| `st.empty()` + filler pattern for clean transitions | Streamlit delta rendering doesn't clear previous elements during blocking loops; pre-rendering blank placeholders fills all positions |
| Codebook injected into query content string | Simplest integration — no LangGraph API changes needed; codebook becomes part of the researcher's instruction prompt |
| `build_goal_query()` composes full context | Single function assembles goal + codebook directions + rubric + supplementary study annotations into one coherent query per goal |
