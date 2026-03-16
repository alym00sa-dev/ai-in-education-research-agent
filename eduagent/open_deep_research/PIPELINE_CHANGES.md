# Pipeline Improvement Log

Track of all architectural changes, decisions, and deferred items across the pipeline improvement project.

---

## Roadmap

| # | Feature | Status |
|---|---|---|
| 1 | New academic DB tools + fetch limit + query guidance | ✅ Done |
| 2 | Strategy evolution (adaptive multi-round search + web search wrappers) | ✅ Done |
| 3 | Researcher self-reflection node | ⏳ Pending |
| 4 | Education Discovery node | ⏳ Pending |
| 5 | Adversarial critique at supervisor level | ⏳ Pending |
| 6 | Multi-LLM pre-filter ensemble | ⏳ Pending |
| 7 | PDF extraction + citation list harvest | ⏳ Pending |
| 8 | Quality delta tracking per iteration | ⏳ Pending |
| 9 | Depth levels / synthesis iterations | ⏳ Pending |

---

## Phase 1 — DB Layer + Query Guidance ✅

### What changed

**`src/utils/academic_search.py`**
- Added `arxiv_search`: free API, no key, covers preprints and AI-in-education research (2022–present)
- Added `elsevier_search`: Scopus API, requires `ELSEVIER_API_KEY`, broad peer-reviewed journal coverage
- Added `scholar_search`: Google Scholar via SerpAPI, requires `SERPAPI_API_KEY`, returns citation counts — used strategically (limited budget)
- Raised all DB fetch limits from 15 → 20 results per call so the relevance filter has a larger candidate pool

**`src/utils/search.py`**
- Registered `arxiv_search`, `elsevier_search`, `scholar_search` in `get_all_tools()`

**`src/nodes/researcher.py`**
- Added `arxiv_search`, `elsevier_search`, `scholar_search` to `_ACADEMIC_DB_TOOLS` so they count toward academic source provenance tracking, not as Tavily web search calls

**`src/prompts.py`**
- Updated `research_system_prompt` Available Tools section to list all 5 DB tools correctly
- Added `<QueryConstruction>` block: quoted phrases, 2–3 query variations per round, academic signal words (RCT, meta-analysis, effect size), synonyms, targeted grey literature queries

### DB layer summary

| Tool | Source | Key needed | Notes |
|---|---|---|---|
| `eric_search` | ERIC / IES | No | US education literature |
| `openalex_search` | OpenAlex | No | Broadest open-access corpus |
| `arxiv_search` | arXiv | No | Preprints, AI-in-edu |
| `elsevier_search` | Scopus | `ELSEVIER_API_KEY` | Peer-reviewed journals |
| `scholar_search` | Google Scholar | `SERPAPI_API_KEY` | Citation counts, broad coverage — 2 calls/session cap enforced by supervisor in iteration 2 |
| `semantic_scholar_search` | Semantic Scholar | `SEMANTIC_SCHOLAR_API_KEY` | Commented out — waiting on new API key |

---

## Phase 2 — Strategy Evolution + Web Search Wrappers ✅

### Goal
Replace single-pass DB searching with explicit multi-round strategy. Researcher calls DBs in round 1, reflects on gaps via think_tool, generates follow-up queries targeting what's missing, runs round 2, and stops when novelty drops. Additionally, make two native web search tools always available to researchers regardless of which model the user has configured.

### What changed

**`src/configuration.py`**
- `max_react_tool_calls` default: 10 → 25, slider max: 30 → 50. LLM compute is not a cost concern; cap is purely a safety net against infinite loops. 25 gives room for ~3 genuine search rounds across 5 DBs.
- `search_api` default: `TAVILY` → `OPENAI`. Native web search is now the research basis; Tavily is a supervisor-unlocked deep-dive tool.

**`src/utils/search.py`**
- Added `anthropic_web_search`: wrapper tool that calls `claude-haiku-4-5-20251001` with Anthropic native web search (`web_search_20250305`) bound. Always available regardless of configured research model.
- Added `openai_web_search`: wrapper tool that calls `gpt-4.1-mini` with OpenAI native web search (`web_search_preview`) bound. Always available regardless of configured research model.
- Registered both wrappers in `get_all_tools()` alongside academic DBs.

**`src/prompts.py`**
- Rewrote `<Instructions>`: explicit Round 1 (all DBs) → think_tool → Round 2 (targeted follow-ups) → novelty check → Round 3+ only if novelty still high
- Rewrote `<Hard Limits>`: always complete minimum 2 rounds; stop when new rounds return no new relevant papers
- Updated Available Tools web search section: lists `anthropic_web_search` and `openai_web_search` as always-available; `tavily_search` noted as supervisor-unlocked only after iteration 1

### Design decisions
- **Minimum 2 rounds**: researcher must always complete at least 2 search rounds before finishing, even if round 1 looks complete. Ensures query variation.
- **Novelty-based stopping (LLM-based, v1)**: researcher is instructed via prompt to track how many papers in each round are genuinely new vs already seen. If novelty drops, stop and compress.
- **Round structure**: Round 1 = all 5 DBs with initial queries. Round 2 = 2–3 DBs with refined follow-up queries. Round 3+ = only if novelty still high.
- **Web search wrappers**: Anthropic and OpenAI native search are model-bound — they only work when the right model is active. Solution: wrapper `@tool` functions call cheap models internally (`haiku-4.5`, `gpt-4.1-mini`), making both always accessible to any researcher regardless of the user's configured research model.

### Full researcher toolkit (post Phase 2)

| Layer | Tools |
|---|---|
| Academic DBs | `eric_search`, `openalex_search`, `arxiv_search`, `elsevier_search`, `scholar_search` |
| Web search (always on) | `anthropic_web_search`, `openai_web_search` |
| Deep dive (supervisor-unlocked, iter 2+) | `tavily_search`, `scholar_search` (SerpAPI budget) |
| Planning | `think_tool`, `ResearchComplete` |

### Deferred
- Code-based novelty tracking (seen_papers set in ResearcherState, novelty_rate calculation) → Phase 8

---

## Phase 3 — Researcher Self-Reflection Node ⏳

### Goal
Add a lightweight self-reflection step at the researcher level — after the main search loop, before compression — where the researcher explicitly audits its own findings for gaps, missing populations, and methodological weaknesses. This is non-adversarial (no external search); it is gap identification only.

### Planned design
- New node `researcher_reflect` inserted between `researcher_tools` and `compress_research`
- Researcher reviews its own tool outputs and asks: "What evidence rungs am I missing? What populations are unrepresented? What methodological questions are unaddressed?"
- Produces a structured gap list → if material gaps exist, triggers one additional targeted search round before compressing
- Hard cap: 1 reflection cycle per researcher subgraph run

### Why this, not the existing critique_agent?
- Current `critique_agent` is adversarial and runs web searches externally. That logic will move to the supervisor level (Phase 5).
- Self-reflection is cheaper, faster, and catches DB coverage gaps earlier — before compression bakes in blind spots.

---

## Phase 4 — Education Discovery Node ⏳

### Goal
Add a pre-supervisor node that decomposes any research query into 9 always-on education research dimensions and 3–5 dynamic sub-areas specific to the query. Output is a structured JSON passed to the supervisor as framing context.

### Planned design
- New node `education_discovery` runs before the supervisor
- Always produces all 9 dimensions (below) as research coverage targets
- Also generates 3–5 query-specific sub-areas via LLM (e.g., "AI tutoring in rural districts", "implementation barriers for under-resourced schools")
- Sub-areas are passed to supervisor as optional framing — not hard-assigned to researchers. Supervisor uses them only if a dimension's findings are thin after round 1.

### 9 always-on dimensions

| # | Dimension | What it captures |
|---|---|---|
| 1 | Effect sizes & outcomes | Quantitative learning gains, d-values, RCT/quasi-exp results |
| 2 | Population & demographics | Age, grade, SES, geography, language, disability status |
| 3 | Intervention types & design | Structure, dosage, modality, human vs. AI delivery |
| 4 | Implementation fidelity | How faithfully the intervention was actually delivered |
| 5 | Methodological landscape | Study designs present, RCT vs. observational, meta-analysis coverage |
| 6 | Equity & differential effects | Whether effects vary across demographic subgroups |
| 7 | Longitudinal effects & sustainability | Do gains persist? What is the evidence past 6 months? |
| 8 | Comparative effectiveness | How does this intervention compare to alternatives? |
| 9 | Cost, scalability & resource requirements | Per-pupil cost, infrastructure needs, feasibility at scale |

---

## Phase 5 — Adversarial Critique at Supervisor Level ⏳

### Goal
Move the existing adversarial critique logic up from the researcher subgraph to the supervisor level. At this level, the critique agent challenges the full combined findings from all researchers — not just one dimension — and can allocate additional searches across the weakest dimensions.

### Planned design
- `critique_agent` node (currently in researcher subgraph) moves to supervisor graph
- Runs once after all researchers complete and findings are combined
- Produces counter-claims and gaps at the synthesis level, not per-dimension
- Supervisor can re-dispatch specific researchers for targeted follow-ups
- Hard cap: 1 adversarial critique cycle per full research run

---

## Phase 6 — Multi-LLM Pre-Filter Ensemble ⏳

### Goal
Before passing papers to the researcher for deep reading, run a lightweight ensemble filter: 3 cheap models each score the paper's relevance (0–3). Only papers averaging ≥ 2.25 pass through to full extraction. Reduces noise entering the compression step.

### Planned design
- 3 models run in parallel: `claude-haiku-4-5-20251001`, `gpt-4.1-mini`, and one additional (TBD)
- Each scores: relevance to topic (0–3), study quality signal (0–3), population match (0–3)
- Average ≥ 2.25 → passes. Below → discarded with a logged reason.
- Papers passing filter are the only ones eligible for PDF extraction (Phase 7)

### Risk
LLM bias in the filter — models may systematically favor certain study designs or writing styles. Mitigation: ensemble of diverse providers, not single-model filter.

---

## Phase 7 — PDF Extraction + Citation List Harvest ⏳

### Goal
For papers passing the Phase 6 filter, attempt full PDF extraction to recover: complete methodology, effect sizes, limitations, and reference DOI lists. Reference DOIs seed the citation chasing pipeline.

### Planned design
- Extraction attempted only for papers scoring ≥ 2.25 in multi-LLM filter
- Source-specific success rates:
  - arXiv: ~100% (fully open access, direct PDF URLs)
  - ERIC: mixed (some OA, some paywalled)
  - Scopus: rarely accessible
- Extract: key findings, methodology section, limitations, reference list as DOIs
- Reference DOIs → citation chasing pipeline (Phase 8)

---

## Phase 8 — Quality Delta Tracking Per Iteration ⏳

### Goal
Track how much each research iteration actually adds — both at the paper level (novelty rate) and at the synthesis level (quality delta). Use this signal to inform stopping decisions with code, not just LLM judgment.

### Planned design
- `seen_papers` set in `ResearcherState` — tracks DOIs/titles across rounds
- `novelty_rate` = new papers this round / total papers this round
- If novelty_rate < threshold (e.g., 0.2) for 2 consecutive rounds → stop
- Supervisor-level quality delta: compare compression outputs across iterations using embedding similarity or LLM scoring
- Replaces v1 LLM-based novelty stopping (Phase 2) with code-enforced signal

---

## Phase 9 — Depth Levels / Synthesis Iterations ⏳

### Goal
Expose a user-facing depth control that drives how many supervisor iterations run and how the final report is structured. Deeper runs = more iterations, more researchers, more synthesis passes.

### Planned design

| Depth | Supervisor iterations | Sub-researchers | Synthesis passes |
|---|---|---|---|
| Standard | 3 | Up to 5 | 1 |
| Deep | 5 | Up to 9 | 2 |
| Comprehensive | 7 | 9 (all dimensions) | 3 |

- Depth exposed as a UI slider or select in the Streamlit app
- Maps to `max_researcher_iterations` in `Configuration`
- Comprehensive depth triggers all 9 Education Discovery dimensions as mandatory coverage

---

## Key Architectural Decisions (Running Log)

**Education Discovery dimensions (9 always-on):**
See Phase 4 above.

**Dynamic sub-areas**: 3–5 generated per query by the Discovery node, passed to supervisor as optional framing — not assigned to researchers. Supervisor uses them only if a dimension's findings are thin after round 1.

**Tavily budget**: Supervisor-unlocked after iteration 1. Up to 1 call per researcher in iteration 2. When exhausted → fall back to `anthropic_web_search` / `openai_web_search`.

**SerpAPI budget**: 2 calls per session total. Allocated by supervisor after iteration 1 to the 2 dimensions with weakest coverage. Not available in iteration 1.

**Synthesis iterations by depth:**
| Label | Iterations |
|---|---|
| Standard | 3 |
| Deep | 5 |
| Comprehensive | 7 |

**Critique architecture:**
- Researcher level (Phase 3): self-reflection node — gap identification only, no adversarial search
- Supervisor level (Phase 5): adversarial critique — challenges full combined findings, can trigger re-searches

**PDF extraction (Phase 7):**
- Only attempt PDFs for papers passing multi-LLM pre-filter (≥2.25 avg score)
- arXiv = high success rate (100% OA), ERIC = mixed, Scopus = rarely accessible
- Extract: key findings, methodology, limitations, reference list as DOIs
- Reference DOIs feed into citation chasing pipeline

**Citation chasing (Phase 7/8):**
- Paper to review before finalizing design: https://arxiv.org/pdf/2501.15552
- KG: `(Paper)-[:CITES {depth}]->(Paper)` relationships in Neo4j
- OpenAlex `referenced_works` field as primary citation source (structured, free)

**Novelty stopping signal:**
- v1 (Phase 2, active): LLM-instructed, prompt-based
- v2 (Phase 8): code-based `seen_papers` set in ResearcherState, `novelty_rate` per round
