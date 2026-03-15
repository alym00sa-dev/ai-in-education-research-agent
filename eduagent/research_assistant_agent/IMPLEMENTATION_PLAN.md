cam# Research Assistant — Implementation Plan
_Last updated: 2026-03-12_

---

## Workstream 1 — LangGraph Graph Changes

### 1a. Citations Slider ✅ IN PROGRESS
- Range: 10–30, default 20
- Add `max_sources: int = 20` to `Configuration` in `open_deep_research/src/configuration.py`
- Pass through `_build_payload` in `src/pipeline/langgraph_client.py` as `configurable["max_sources"]`
- Replace hardcoded `[:18]` cap in `_extract_sources` with `[:max_sources]`
- Add slider to Default mode UI (`pages/research_agent.py`) and Strategic Canvas (`src/strategic_canvas/ui.py`)

### 1b. Sub-Researcher Critique Node
- New `critique_research` node in `open_deep_research/src/nodes/researcher.py`
- Runs after `compress_research`, before returning to supervisor
- Max 5 cycles tracked via `critique_iterations` field in `ResearcherState`
- Structured JSON output per round:
  ```json
  {
    "approved": false,
    "round": 2,
    "gaps_identified": ["No RCT-level evidence on X", "Missing low-income population coverage"],
    "instructions_for_researcher": "Search specifically for..."
  }
  ```
- All rounds stored in state for Quality Assessment tab
- Flow: `compress_research → critique_research → researcher (if gaps + cycles < 5) | END (if approved or cycles = 5)`
- Add `max_critique_iterations: int = 5` to `Configuration`

### 1c. Supervisor Prompt Decomposition Tuning
- Modify `lead_researcher_prompt` scaling rules in `open_deep_research/src/prompts.py`
- Any topic with multiple populations, intervention types, outcome dimensions, or geographies must be decomposed into parallel sub-topics
- Remove "bias towards single agent" default — replace with "bias towards comprehensive decomposition for complex topics"

### 1d. Supervisor QA Node
- New `qa_review` node in `open_deep_research/src/nodes/qa.py`
- Runs after `supervisor_subgraph`, before `final_report_generation`
- One-pass, no cycle
- Two jobs:
  1. **Coverage QA**: reviews all compressed notes vs. research brief, identifies well-evidenced vs. thin areas, injects as context into final report prompt
  2. **Format enforcement**: verifies final report will contain all four required sections (synthesis, causality diagram, scored sources, data extraction table); generates data extraction table using user-defined column schema
- Wire into outer graph in `open_deep_research/src/deep_researcher.py`

### 1e. User-Defined Extraction Table Schema
- At report construction stage, user specifies columns for the data extraction table
- Defaults: Title, Year, Study Design, Population, Outcome, Finding Direction, Effect Size
- User can add custom columns (e.g., "Implementation Cost", "Setting", "Technology Used")
- Schema passed through payload as `configurable["extraction_table_schema"]`
- QA node uses schema to enforce and populate the table in the final report

---

## Workstream 2 — Quality Assessment Tab

### 2a. Updated `compress_research_system_prompt`
Add required structured output blocks at the end of every compressed output:

```
### SOURCES USED
[url] - [title] - Reason: directly addresses tutoring outcomes for Grade 3

### SOURCES EXCLUDED
[url] - Reason: abstract only, insufficient content
[url] - Reason: product marketing page, no empirical data

### MECHANISMS
[A: intervention] → [B: mechanism] — context/source: ...
[B: mechanism] → [C: outcome/population] — context/source: ...
```

### 2b. Critique Rounds Capture
- Each critique round's structured JSON stored in `ResearcherState` under `critique_log`
- Exposed in Quality Assessment tab: "Researcher 2 — 3 critique rounds: Round 1 gap: X → Round 2 gap: Y → Approved round 3"

### 2c. GRADE Table Per Sub-Researcher
- Generated after critique approval, before returning to supervisor
- One table per sub-researcher per topic
- Domains: Risk of Bias, Inconsistency, Indirectness, Imprecision, Publication Bias, Large Effect, Dose-Response, Plausible Confounding
- Format:

| Domain | Rating | Key Papers | Assessment |
|---|---|---|---|
| Risk of Bias | Serious (-1) | [paper] | Narrative justification |
| Inconsistency | No concern | — | ... |

### 2d. Quality Assessment Tab UI
New middle tab between Report and Thought Log containing:
- GRADE table per topic (expandable per sub-researcher)
- Source inclusion/exclusion log per sub-researcher
- Critique rounds summary (collapsible per researcher)
- Aggregate breakdown: study design distribution, population coverage, finding direction mix (from structured papers)

---

## Workstream 3 — Enhanced Downloads

### `.docx`
Four sections in one document:
1. Research Synthesis (report body)
2. Causality Diagram (Mermaid rendered as image)
3. Sources (scored with 🔵🟢🟡🔴 quality/impact ratings + body of evidence maturity)
4. Data Extraction Table (user-defined columns)
5. Quality Assessment appendix (GRADE tables + source justification logs)

### `.json` (human-readable audit log)
```json
{
  "query": "...",
  "session_id": "...",
  "timestamp": "...",
  "extraction_table_schema": ["Title", "Year", "Study Design", ...],
  "supervisor_plan": {
    "topics_assigned": [...],
    "iterations": 2
  },
  "sub_researchers": [
    {
      "topic": "...",
      "critique_rounds": [...],
      "sources_used": [...],
      "sources_excluded": [...],
      "mechanisms": [{"A": "...", "B": "...", "C": "..."}],
      "grade_assessment": {...},
      "compressed_findings": "..."
    }
  ],
  "swanson_hypotheses": [...],
  "qa_review": {
    "coverage_assessment": "...",
    "format_verified": true
  },
  "final_report": "...",
  "data_extraction_table": [...],
  "structured_papers": [...]
}
```

---

## Workstream 4 — Session Persistence

- Write `sessions/{session_id}.json` at finalization time containing the full audit object
- On sidebar click, load from file and restore all tabs and download buttons
- No Neo4j schema changes needed
- Location: `research_assistant_agent/sessions/`

---

## Workstream 5 — Academic Database Integration

Integration point: `open_deep_research/src/utils/search.py` (`get_all_tools`)

Candidate databases for education research (to be confirmed by user):
- **ERIC** — gold standard for education research, free API
- **Semantic Scholar** — strong empirical coverage, citation graphs, free
- **OpenAlex** — broad coverage, good metadata, free
- **PubMed** — learning science, cognitive research, free

Each database added as a named tool (`eric_search`, `semantic_scholar_search`, etc.) so sub-researchers can call them explicitly and source logs show which database each paper came from.

---

## Workstream 6 — Report Structure

Every generated report has four sections in this order:

### Section 1 — Research Synthesis
Main findings narrative.

### Section 2 — Causality Diagram
Mermaid graph with:
- **Solid edges** = empirically supported connections (citation label on edge)
- **Dashed edges** = Swanson-derived novel hypotheses (bridging B-concept + confidence label)
- Node colors: blue = intervention, green = mechanism, orange = outcome, purple = population

**Swanson ABC Node** (new, runs after all sub-researchers finish):
- Consumes `### MECHANISMS` blocks from all compressed research outputs
- Extracts A→B and B→C pairs with their source citations from each leg
- Chains into novel A→C hypotheses carrying citations from both legs
- Structured output per hypothesis:
  ```json
  {
    "A": "AI tutoring",
    "B": "spaced retrieval practice",
    "C": "long-term retention in low-income students",
    "A_to_B_citations": ["Smith 2022 - URL", "Jones 2023 - URL"],
    "B_to_C_citations": ["Lee 2021 - URL"],
    "confidence": "Moderate",
    "rationale": "One sentence on why the chain holds"
  }
  ```
- **Confidence levels (Option A — categorical with rubric):**
  - **Strong** — both legs have ≥2 papers, at least one experimental or quasi-experimental
  - **Moderate** — both legs supported but primarily correlational or small-N
  - **Speculative** — one leg is thin (1 paper, observational) or B concept loosely defined

### Section 3 — Sources (Scored)
Quality/impact rating system (🔵🟢🟡🔴) per source + body of evidence maturity assessment.

### Section 4 — Data Extraction Table
User-defined column schema, populated by QA node from compressed research and structured paper extraction.

---

## Build Order

| # | Item | Status | Dependency |
|---|---|---|---|
| 1 | Citations slider (10–30, default 20) | 🔄 In Progress | None |
| 2 | User-defined extraction table schema in UI | ⬜ Todo | None |
| 3 | Updated compress prompt (sources used/excluded + mechanisms block) | ⬜ Todo | None |
| 4 | Critique node in researcher subgraph (max 5 cycles) | ⬜ Todo | Compress prompt |
| 5 | GRADE node in researcher subgraph | ⬜ Todo | Critique node |
| 6 | Supervisor prompt decomposition tuning | ⬜ Todo | None |
| 7 | Supervisor QA node (coverage + format + extraction table) | ⬜ Todo | User schema (#2), GRADE data (#5) |
| 8 | Swanson ABC node + causality diagram (Mermaid) | ⬜ Todo | Mechanisms block (#3) |
| 9 | Session audit JSON writer | ⬜ Todo | All graph changes |
| 10 | Quality Assessment tab UI | ⬜ Todo | Audit JSON (#9) |
| 11 | Enhanced .docx + .json downloads | ⬜ Todo | Full dataset (#9) |
| 12 | Session persistence (sidebar restore) | ⬜ Todo | Audit JSON (#9) |
| 13 | Academic database tools | ⬜ Todo | User confirms DB list |
