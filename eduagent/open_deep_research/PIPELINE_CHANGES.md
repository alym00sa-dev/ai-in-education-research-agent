# Pipeline Improvement Log

Track of all architectural changes, decisions, and deferred items across the pipeline improvement project.

---

## Roadmap

| # | Feature | Status |
|---|---|---|
| 1 | New academic DB tools + fetch limit + query guidance | ✅ Done |
| 2 | Strategy evolution (adaptive multi-round search + web search wrappers) | ✅ Done |
| 3 | Education Discovery node — simplified supervisor-driven decomposition | ✅ Done |
| 4 | Researcher self-reflection node | ✅ Done |
| 5 | Adversarial critique at supervisor level | ✅ Done |
| 6 | Multi-LLM pre-filter ensemble — updated to 0–7 scale, avg > 2.5 | ✅ Done |
| 7 | PDF extraction + KG-aligned PaperProfile + quality/impact tiers | ✅ Done |
| 8 | KG schema redesign + migration (9-outcome schema, ImplementationObjective removed) | ✅ Done |
| 9 | New UI (edu_discovery_platform — Next.js) — build + UX pass | ✅ Done |
| 10 | Report restructure — Executive Summary + Research Report + Bibliography | ✅ Done |
| 11 | End-to-end test on new UI | 🔄 In Progress |
| 12 | KG write trigger post-run, mass re-extraction of 359 legacy papers | ⏳ Pending |
| 13 | Citation chaser + CCM model integration | ⏳ Later |
| 14 | Quality delta tracking per iteration | ⏳ Later |

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

## Phase 3b — Asta (Allen AI) MCP Tools ✅

### What changed

**`src/utils/search.py`**
- Added `load_asta_tools()`: connects to `https://asta-tools.allen.ai/mcp/v1` with `x-api-key` header via `langchain_mcp_adapters.client.MultiServerMCPClient`
- Registered in `get_all_tools()` alongside other academic DBs
- Loads 8 tools: `get_paper`, `get_paper_batch`, `get_citations`, `search_authors_by_name`, `get_author_papers`, `search_papers_by_relevance`, `search_paper_by_title`, `snippet_search`

**`src/nodes/researcher.py`**
- Added all 7 Asta tool names to `_ACADEMIC_DB_TOOLS` (excludes `get_paper_batch` as it's a batch variant of `get_paper`)

**`src/prompts.py`**
- Removed `{mcp_prompt}` placeholder and surrounding text from `research_system_prompt` to free token budget
- Added Asta tool descriptions to the `<Available Tools>` section

### Asta tools

| Tool | Purpose |
|---|---|
| `search_papers_by_relevance` | Semantic search across Semantic Scholar corpus |
| `snippet_search` | Returns relevant text snippets from papers |
| `get_paper` | Full paper metadata by ID |
| `get_paper_batch` | Batch paper metadata |
| `get_citations` | Papers citing a given paper |
| `search_paper_by_title` | Find paper by exact or near title |
| `search_authors_by_name` | Find authors by name |
| `get_author_papers` | All papers by a given author |

---

## Phase 4 — Researcher Self-Reflection Node ✅

### What shipped

**`src/state.py`**
- `ResearcherState`: added `reflection_cycles: int = 0`
- `AgentState`: added `critique_cycles: int = 0` (used by Phase 5 supervisor critique)

**`src/prompts.py`**
- Added `researcher_reflect_prompt`: instructs Haiku to audit coverage on 4 axes (evidence quality, population coverage, core outcomes, methodological diversity); PASS/NEEDS_WORK with specific gap list and search directive

**`src/nodes/researcher.py`**
- Removed `CritiqueDecision` and `critique_agent` (moved to supervisor level — see Phase 5)
- Added `ReflectionDecision` Pydantic model
- Added `researcher_reflect` node: uses `claude-haiku-4-5-20251001`, structured output, hard cap of 1 cycle
- `researcher_tools` now routes to `researcher_reflect` when done (instead of `critique_agent`)

### Researcher subgraph flow (post Phase 4)

```
researcher → researcher_tools → [loop] → researcher_reflect → compress_research
                                                │ NEEDS_WORK (cycle 0 only)
                                                ↓
                                         researcher (gap directive injected, tool_call_iterations=0)
                                                │
                                         researcher_tools → researcher_reflect (cycle=1, always PASS)
```

---

## Phase 3 — Education Discovery Node ✅

### Final design (simplified from original EVT+RST plan)

The EVT+RST pre-planning architecture was explored and validated (prompts worked, 5/5 test pass) but ultimately replaced with a simpler supervisor-driven approach. Reason: the supervisor LLM is capable of decomposing queries into focused sub-questions in-context — pre-planning added latency and complexity without sufficient benefit at this stage.

### What shipped

**`src/nodes/education_discovery.py`** — simplified to a single LLM call: transforms user messages into a structured research brief (`ResearchQuestion`), initialises supervisor context. No EVT/RST generation.

**`src/state.py`** — removed `EvidenceTarget`, `ResearchTrack`, `EducationDiscovery` models. `ConductResearch` tool now has two fields:
- `research_topic: str` — focused sub-question (1-2 sentences, not a paragraph)
- `keywords: list[str]` — 3-5 search terms to guide DB queries

**`src/nodes/supervisor.py`** — added `_build_researcher_brief()` helper that appends keywords to the sub-question when dispatching each researcher.

**`src/prompts.py`** — three key changes:
- **Supervisor `<Show Your Thinking>`**: plan + dispatch in same response (think_tool alongside ConductResearch calls); sub-questions must be 1-2 sentences
- **Researcher `<EvidencePriority>`**: explicit block — RCTs and peer-reviewed sources first, always
- **Researcher `<EducationEvidenceDimensions>`**: 9 dimensions sent to each researcher as a soft evidence guide (not a checklist; capture what you encounter naturally)

### 9 dimensions (researcher guide — not dispatch units)

| # | Dimension | What it captures |
|---|---|---|
| 1 | Effect sizes & outcomes | Cohen's d, test score gains, grade improvements vs. control or baseline |
| 2 | Population & demographics | Age, grade, SES, geography, language, disability; generalizability across groups |
| 3 | Intervention types & design | Instructional model, modality, dosage, duration, delivery channel, who delivers |
| 4 | Implementation fidelity | Real-world delivery vs. intended design; adoption barriers, delivery quality vs. outcomes |
| 5 | Methodological landscape & study quality | RCTs, quasi-exp, observational, meta-analyses; sample sizes, replication, risk of bias |
| 6 | Equity & differential effects | Impact differences across SES, race/ethnicity, language learners, students with disabilities |
| 7 | Longitudinal effects & sustainability | Persistence of gains over 6 months, 1 year, multiple years |
| 8 | Comparative effectiveness | Head-to-head comparisons with alternative approaches; relative impact sizes |
| 9 | Cost, scalability & resource requirements | Per-student cost, staffing, infrastructure, feasibility to scale |

### Test

`tests/test_pipeline.py` — decomposition-only (researchers mocked). Runs 4 queries, saves one JSON per query to `tests/output/`. Shows research brief, supervisor think reflections, sub-questions dispatched, keywords per sub-question. Traces to Phoenix `discovery-test`.

### Pipeline flow (post Phase 3)

```
User query
  ↓
education_discovery   → research brief (1 LLM call)
  ↓
supervisor            → think + dispatch 4-6 sub-questions in one step
                         each sub-question gets keywords
  ↓
researchers × N       → sub-question + keywords + 9 dimensions as guide
                         RCTs and peer-reviewed evidence first
  ↓
compress → qa_review → final_report
```

---

## Phase 5 — Adversarial Critique at Supervisor Level ✅

### What shipped

**`src/deep_researcher.py`**
- Added `CritiqueDecision` Pydantic model (counter_claims, gaps, search_directive)
- Added `supervisor_critique` node: same two-phase logic as old researcher-level critique, but now runs on the full combined synthesis (`AgentState.notes`) against the `research_brief`
- Phase 1: `claude-sonnet-4-6` with Anthropic native web search finds counter-evidence
- Phase 2: `claude-sonnet-4-6` structured output produces `CritiqueDecision`
- PASS → `qa_review` · NEEDS_WORK → inject gap directive into `supervisor_messages`, goto `research_supervisor` for targeted re-dispatch

**`src/prompts.py`**
- Updated `critique_agent_prompt` and `critique_agent_search_prompt`: renamed `<OverallResearchQuery>` → `<ResearchBrief>` to reflect synthesis-level scope

### Main graph flow (post Phase 5)

```
education_discovery → research_supervisor → supervisor_critique → qa_review → final_report
                                                    │ NEEDS_WORK (cycle 0 only)
                                                    ↓
                                             research_supervisor (gap directive in supervisor_messages)
                                                    │
                                             targeted researchers dispatched
                                                    │
                                             supervisor_critique (critique_cycles=1, always PASS now)
```

---

## Phase 6 — Multi-LLM Pre-Filter Ensemble ✅

### What shipped

**Simplified from original 3-model / 4-dimension design to a 2-model / 1–5 scale ensemble:**
- 2 models in parallel: `claude-haiku-4-5-20251001` + `gpt-4.1-mini`
- Each model scores on a **1–5 scale** (lenient — broad pass, only obvious noise rejected)
- Average score > 1.5 → passes through to researcher context + PDF extraction eligibility
- Pre-filtering step (`_filter_and_rank` in `academic_search.py`) removed — redundant with ensemble

**`src/utils/academic_search.py`**
- Removed `_filter_and_rank()` helper — all tools now return raw results[:20] directly
- No pre-filtering; full candidate pool handed to ensemble

**`src/nodes/researcher.py`**
- Ensemble filter runs on each tool call's results before appending to researcher context
- `paper_filter_prompt` instructs models to "be lenient — only filter clear noise"

**`src/prompts.py`**
- `paper_filter_prompt`: 1–5 scale, lenient framing

---

## Phase 7 — PDF Extraction + KG-Aligned PaperProfile ✅

### What shipped

**`src/state.py`**
- New Pydantic models: `EmpiricalFindingExtract`, `OutcomeAssignment`, `PaperProfile`
- `PaperProfile` fields: `title`, `doi`, `year`, `venue`, `url`, `source_db`, `population`, `user_type`, `study_design`, `extended_summary`, `quality_tier`, `impact_tier`, `outcome_assignments`, `extraction_status`, `extraction_note`
- `quality_tier` + `impact_tier` scored at extraction time by Haiku using K-12 Evidence Framework (blue/green/yellow/red)
- `paper_profiles: Annotated[list[PaperProfile], operator.add]` added to `AgentState`, `ResearcherState`, `ResearcherOutputState`

**`src/utils/pdf_extractor.py`** — NEW
- Full pipeline: URL parsing → HTTP fetch → PyMuPDF text extraction → Haiku structured output → `PaperProfile`
- `PDF_EXTRACTABLE_TOOLS` set: `eric_search`, `openalex_search`, `arxiv_search`, `elsevier_search`, `semantic_scholar_search`, `search_papers_by_relevance`, `get_paper`
- `enrich_tool_output(tool_name, tool_output, research_topic) → tuple[str, list[PaperProfile]]`: runs extractions in parallel, injects `[FULL TEXT EXTRACTED]` / `[ABSTRACT ONLY — reason]` tags into researcher context
- Always produces a PaperProfile (graceful fallback to abstract-only mode)

**`src/nodes/researcher.py`**
- After ensemble filter: if `configurable.enable_pdf_extraction` and tool is in `PDF_EXTRACTABLE_TOOLS`, calls `enrich_tool_output` in parallel via `asyncio.gather`
- Both `compress_research` return paths include `"paper_profiles": all_paper_profiles`

**`src/nodes/supervisor.py`**
- Aggregates `paper_profiles` from all researcher `tool_results` before building `update_payload`

**`src/configuration.py`**
- Added `enable_pdf_extraction: bool = True`

**`src/prompts.py`**
- `pdf_extraction_prompt`: full K-12 Evidence Framework quality + impact tier rubric with criteria (blue/green/yellow/red for each dimension)
- Final report changed from 4-section → 3-section structure: Section 1 Synthesis, Section 2 Sources, Section 3 Data Extraction Table (Swanson causality diagram section removed)

### K-12 Evidence Framework Tiers (scored at extraction time)

| Tier | Quality criteria | Impact criteria |
|---|---|---|
| 🔵 Blue | RCT / strong quasi-exp, n ≥ 200, high credibility, K-12 direct | Large effect (d ≥ 0.4) or cost-effective, priority population focus |
| 🟢 Green | Quasi-exp / pre-post with control, n 50–199, clear methods | Moderate effect (d 0.2–0.4) or promising with strong mechanism |
| 🟡 Yellow | Observational / case study / mixed, n < 50 or indirect, partial methods | Small / unclear effect, mixed evidence |
| 🔴 Red | Anecdotal / no methodology, not peer-reviewed, non-K-12 irrelevant | Negative / null / contradictory / harmful |

### `OUTCOME_CONFIDENCE_THRESHOLD`
- LLM returns scores ≥ 0.5 for outcome assignments
- Code filters to ≥ 0.7 before KG write (`kg_writer.py`)

---

## Phase 8 — KG Schema Redesign + Migration ✅

### What shipped

**Migration ran successfully (2026-03-18):**
- 9 Outcome nodes, 0 old outcomes, 0 ImplementationObjective nodes
- 416 findings all have `finding_summary`, 0 have legacy `results_summary`
- 359 papers all have new fields (`quality_tier=""`, `impact_tier=""`, `extraction_status="legacy"`)
- All paper→outcome links preserved (no orphaned findings)

**`scripts/migrate_kg_v2.py`** — NEW (7-phase, idempotent, `--dry-run` flag)
- Phase 1: ONE_TO_ONE renames — 4 Cognitive → Academic nodes (properties updated, existing rels survive automatically)
- Phase 2: MANY_TO_ONE merges — 8 old nodes → 3 new nodes; retarget all `FOCUSES_ON_OUTCOME` + `HAS_FINDING` rels, delete old nodes
- Phase 3: Create 2 new nodes (Academic — Other, Systemic / Institutional Impact)
- Phase 4: DETACH DELETE all ImplementationObjective nodes
- Phase 5: Copy `results_summary` → `finding_summary` on all EmpiricalFinding nodes
- Phase 6: REMOVE 20 old fields from EmpiricalFinding nodes
- Phase 7: Add `quality_tier=""`, `impact_tier=""`, `extraction_status="legacy"` defaults to all Paper nodes

**`src/neo4j_config.py`**
- `OUTCOMES` updated to 9 new values
- Removed `IMPLEMENTATION_OBJECTIVES`
- `initialize_taxonomies()`: uses `MERGE (o:Outcome {name: $name})`, removed ImplementationObjective creation
- Indexes updated: added `(p:Paper) ON (p.doi)`, changed Outcome index to `name`, removed ImplementationObjective index

**`src/kg_agent/queries.py`**
- `get_papers_by_taxonomy`: removed `objectives` param + ImplementationObjective join; `out.id` → `out.name`, `results_summary` → `finding_summary`
- Removed `get_objective_coverage()`
- `query_by_empirical_findings`: removed ImplementationObjective join, `results_summary` → `finding_summary`

**`src/kg_agent/agent.py`**
- Removed `IMPLEMENTATION_OBJECTIVES`, `get_objective_coverage`, `objectives` from `TaxonomyMapping`, `objective_counts` from `KGCoverage`
- Updated `_TAXONOMY_MAPPING_PROMPT`, `_map_to_taxonomy`, `query_coverage`

**`src/kg_agent/question_explorer.py`**
- Removed `IMPLEMENTATION_OBJECTIVES` from import + tool response; `query_by_objectives` returns empty list

**`src/session_manager.py`**
- `get_session_papers`: removed `HAS_IMPLEMENTATION_OBJECTIVE` join, `f.results_summary` → `f.finding_summary`, `out.id` → `out.name`, removed `objective` from result dict

**`src/pipeline/orchestrator.py`**
- `results_summary` → `finding_summary` in graph node construction and `structured_papers_dicts`
- Removed `"objective": p.implementation_objective` from paper dict

**`src/kg_writer.py`** — NEW (in `research_assistant_agent/`)
- `KGWriter.write_paper_profiles(profiles, session_id) → int`
- Skips `abstract_only` profiles; MERGE Paper on DOI (title fallback)
- Writes all new fields: `quality_tier`, `impact_tier`, `extended_summary`, `extraction_status`, `source_db`
- Per OutcomeAssignment (confidence ≥ 0.7): MERGE `FOCUSES_ON_OUTCOME` rel, MERGE EmpiricalFinding (7 fields), link to paper + outcome
- `_get()` helper works for both Pydantic models and dicts

### New 9-outcome schema

| New name | Replaces |
|---|---|
| Academic — Literacy | Cognitive — Literacy |
| Academic — Language Fluency | Cognitive — Language Fluency |
| Academic — Mathematical Numeracy | Cognitive — Mathematical Numeracy |
| Academic — Scientific Reasoning | Cognitive — Scientific Reasoning |
| Academic — Other | _(new)_ |
| Social-Emotional Skills | Social-Emotional Development + Social-Emotional Skills |
| Durable Skills | Executive Function + Durable Skills + Metacognitive Skills |
| Operational Efficiency | Operational Efficiency |
| Systemic / Institutional Impact | _(new)_ |

### Deferred
- `KGWriter` built but not wired — needs call trigger in Render server post-run
- Session write to Neo4j (old Streamlit orchestrator handled this) needs new trigger
- 359 legacy papers need mass re-extraction to get proper `quality_tier`, `impact_tier`, and new outcome assignments

---

## Swanson ABC — Removed from Graph (code preserved)

**`src/deep_researcher.py`**
- Removed `from nodes.swanson import swanson_abc` import
- Removed `add_node("swanson_abc", swanson_abc)`
- `qa_review` now routes directly to `final_report_generation` (was → `swanson_abc` → `final_report`)
- Comment added: `# swanson_abc preserved for future use — not wired into graph`
- Graph docstring updated

**Code preserved:** `src/nodes/swanson.py` + `swanson_abc_prompt` in `prompts.py` + `swanson_hypotheses` / `causality_diagram` fields in `state.py` (kept as no-ops)

---

## Phase 9 — New UI (edu_discovery_platform) — Initial Review ✅

### What shipped

**`edu_discovery_platform/`** — Next.js frontend (replaces Streamlit)
- Reviewed full UI structure: `app/page.tsx`, `components/agent/`, `components/canvas/`, `components/layout/`
- `JobRow.tsx`: removed hardcoded 40% progress bar shimmer (running jobs no longer show progress bar)
- `Navbar.tsx`: removed "A" avatar div from right section; replaced with `<div className="w-7" />` spacer

### Deferred (from UI review)
- **Strategic Canvas** (`CanvasShell.tsx`): placeholder, deferred
- **Task Type** (`QueryBar.tsx`): select exists, no options yet, deferred
- **Deep Guided mode**: no longer a priority
- **Streamlit → Next.js migration**: pertinent Python files (pipeline, exports, KG agent) to be moved; no rush

---

## Phase 8b — Quality Delta Tracking Per Iteration ⏳

### Goal
Track how much each research iteration actually adds — both at the paper level (novelty rate) and at the synthesis level (quality delta). Use this signal to inform stopping decisions with code, not just LLM judgment.

### Planned design
- `seen_papers` set in `ResearcherState` — tracks DOIs/titles across rounds
- `novelty_rate` = new papers this round / total papers this round
- If novelty_rate < threshold (e.g., 0.2) for 2 consecutive rounds → stop
- Supervisor-level quality delta: compare compression outputs across iterations using embedding similarity or LLM scoring
- Replaces v1 LLM-based novelty stopping (Phase 2) with code-enforced signal

---

## Phase 5b — Iteration Count + Credit Budget Control ✅

### What shipped

**`src/configuration.py`**
- Added `research_iterations: int = 2` — number of full supervisor dispatch rounds per query; `critique_cycles = research_iterations - 1`
- Added `tavily_budget: int = 10` — total Tavily calls per query, shared across all researchers and iterations
- Added `serpapi_budget: int = 3` — total SerpAPI (Google Scholar) calls per query, shared

**`src/nodes/education_discovery.py`**
- Builds `credit_budget` string from config and injects into supervisor system prompt via `{credit_budget}` placeholder
- Instructs supervisor: no Tavily in iteration 1; reserve SerpAPI for 1-2 researchers with weakest coverage after iteration 1; LLM web search is always free

**`src/prompts.py`**
- Added `{credit_budget}` placeholder inside `<Hard Limits>` block in `lead_researcher_prompt`

**`src/deep_researcher.py`** (`supervisor_critique`)
- Hard cap changed from `critique_cycles >= 1` → `critique_cycles >= configurable.research_iterations - 1`
- Gap message now includes current remaining credits (Tavily, SerpAPI) so the supervisor knows what's left when re-dispatching

### Credit + iteration model

```
research_iterations=2 (default) → 1 critique cycle
research_iterations=3           → 2 critique cycles
research_iterations=N           → N-1 critique cycles

Credit pool per query (shared):
  Tavily:  10 calls  (reserved for iteration 2+, targeted gap-filling)
  SerpAPI:  3 calls  (allocated by supervisor to weakest-coverage researchers)
  LLM web search: unlimited (no credit cost)
```

---

## Phase 9 — Depth Levels / Synthesis Iterations ⏳

### Goal
Expose a user-facing depth control that drives how many supervisor iterations run and how the final report is structured. Deeper runs = more iterations, more researchers, more synthesis passes.

### Planned design

| Depth | research_iterations | Critique cycles | Notes |
|---|---|---|---|
| Standard | 2 | 1 | Default |
| Deep | 3 | 2 | |
| Comprehensive | 4–5 | 3–4 | Consider credit impact |

- Depth exposed as a UI slider in the Streamlit app (maps directly to `research_iterations`)
- Novelty/information delta tracking (Phase 8) will eventually replace fixed iteration count with a code-enforced stopping signal
- Higher iterations consume more Tavily/SerpAPI credits — users should increase budgets accordingly

---

## Phase 9 — New UI Full UX Pass (edu_discovery_platform) ✅

### What shipped

**`edu_discovery_platform/lib/types.ts`**
- Removed `citations: boolean` from `ResearchConfig`
- Added `keywords?: string` and `agentVersion?: string` fields
- `TaskType` typed as `"research-basic" | ""`
- Replaced `TASK_TYPE_LABELS` with `TASK_TYPE_OPTIONS = [{ value: "research-basic", label: "Research — Basic" }]`
- `DEPTH_OPTIONS` trimmed to Standard only (description: "2 iterations")
- `MODEL_OPTIONS` expanded to 10 models matching Streamlit `AVAILABLE_MODELS`:
  - OpenAI: GPT-5.2 (default), GPT-5.4, GPT-5 Mini, GPT-4.1, GPT-4o
  - Anthropic: Claude Sonnet 4.6, Claude Opus 4.6, Claude Sonnet 4.5, Claude Opus 4.5, Claude Haiku 4.5

**`edu_discovery_platform/components/agent/QueryBar.tsx`**
- Removed citations toggle and its `Divider`
- Added keywords input row (between textarea and filters row): comma-separated terms to guide search
- Renamed "Depth" label → "Search Rigor"
- Renamed "Sources" label → "Top-K"
- Default `maxSources`: 20 → 30; default `model`: `"gpt-4.1"` → `"gpt-5.2"`
- Added `agentVersion: "v2"` to `DEFAULT_CONFIG`
- Task type dropdown populated from `TASK_TYPE_OPTIONS`

**`edu_discovery_platform/components/agent/JobRow.tsx`**
- Full rewrite: removed FileText icon, progress bar, model/depth/paperCount badges
- Session ID (first 8 chars, monospace) in icon slot
- Full query shown (no truncation)
- `formatDate(job.createdAt)` instead of relative "N days ago"
- Only two badges: `taskType` and `agentVersion`
- Derived: `taskType = job.config.taskType || "streamlit-research"`, `agentVersion = job.config.agentVersion || "v1"`

**`edu_discovery_platform/hooks/useSessions.ts`**
- `taskType: "streamlit-research"`, `agentVersion: "v1"` for all Neo4j (Streamlit) sessions
- Removed `citations: true`, `maxSources` 20 → 30

**`edu_discovery_platform/app/agent/page.tsx`**
- Removed hero title/subtitle div; reduced top padding from `pt-10` → `pt-6`
- Removed `selectedJob` state; replaced with `runningJob` (drawer only while job is running)
- Added `useRouter`: completed/failed jobs navigate to `/agent/${job.id}` (full page); running jobs keep drawer
- `ReportDrawer` only renders when `runningJob?.status === "running"`

**`edu_discovery_platform/app/agent/[id]/page.tsx`** — NEW
- Dynamic route: loads job from localStorage first, falls back to `/api/sessions`
- Sticky header with back button + query title
- Collapsible "Session details" expander: Model, Search Rigor, Top-K, Task Type, Agent Version, Date, Keywords (no paper count)
- 4 tabs: Report, Evidence Log, Agent Thoughts, Downloads
- `DownloadsTab`: 3 client-side blob download buttons — `report.md`, `evidence_log.csv`, `thoughts.json`
- Full-width report rendering with improved prose styles

**`edu_discovery_platform/components/layout/Navbar.tsx`**
- Removed "A" avatar div from right section; replaced with `<div className="w-7" />` spacer

**`edu_discovery_platform/app/api/research/stream/route.ts`**
- Expanded `MODEL_MAP` to all 10 models with full provider-prefixed IDs
- Added `search_api` auto-detection: `mappedModel.startsWith("anthropic:") ? "anthropic" : "openai"`
- Keywords appended to message content: `"${query}\nKeywords: ${keywords}"` if present
- Default `max_sources`: 20 → 30

**`open_deep_research/server.py`**
- Added `from dotenv import load_dotenv` + `load_dotenv()` so `.env` is auto-loaded on startup

**`open_deep_research/.env`** — NEW
- Copied from `research_assistant_agent/.env` (all API keys + Neo4j credentials for local dev)

### Where the chosen model is used in the pipeline

| Slot | Model | Fixed or user-chosen |
|---|---|---|
| Research supervisor + researchers | `research_model` config (user-chosen) | User-chosen |
| Researcher reflect | `claude-haiku-4-5-20251001` | Fixed |
| Supervisor critique (search + decision) | `claude-sonnet-4-6` | Fixed |
| PDF extraction + paper tier scoring | `claude-haiku-4-5-20251001` | Fixed |
| Paper filter ensemble | `claude-haiku-4-5-20251001` + `gpt-4.1-mini` | Fixed |
| Final report generation | `research_model` (user-chosen) | User-chosen |

### Session routing model

- **Running jobs**: keep in right-side drawer — navigating away would kill the active stream
- **Completed / failed jobs**: navigate to full-page `/agent/[id]` route
- **Streamlit legacy sessions**: loaded from `/api/sessions` (Neo4j), shown in sidebar with `agentVersion: "v1"` and `taskType: "streamlit-research"`

---

## Phase 10 — Report Restructure ✅

### What shipped

**`open_deep_research/src/prompts.py`**
- Removed `<Quality Assessment>` block and `{qa_assessment}` placeholder from `final_report_generation_prompt`
- Full report restructure to 3-section format:
  1. **Executive Summary** — one focused paragraph: thesis/main argument, overall confidence level, one caveat; always cites real sources
  2. **Research Report** — 5 required subsections: Intervention Types, Evidence on Effectiveness, Demographic Moderators, Limitations, Recommendations; each subsection must include specific effect sizes (d=X, n=X, RCT), inline citations, precise language
  3. **Bibliography** — pre-scored tiers from `{paper_tier_reference}`, K-12 rubric fallback if tier missing, Body of Evidence Maturity assessment
- Added `<HallucinationGuard>` block with 6 explicit rules:
  1. Never invent or paraphrase citations not in the provided sources
  2. Never blend stats from two papers into one claim
  3. Never fill gaps with training-knowledge background claims
  4. Write "not reported" for missing numbers; never estimate or infer them
  5. Every number in the body must have an inline citation pointing to a Bibliography entry
  6. No orphan citations — if a source provides nothing for a claim, don't cite it
- Added one sentence to `critique_agent_prompt` about logical integrity: *"In addition to checking for gaps, briefly check the findings themselves for logical integrity: flag any claims that appear fabricated, internally contradictory, or that overstate what the cited evidence actually supports."*

**`open_deep_research/src/nodes/report.py`**
- Removed `qa_assessment` / `extraction_table` from state reads and format call
- Added `paper_tier_reference` builder: iterates `state.get("paper_profiles", [])`, maps `quality_tier` / `impact_tier` → emoji label, formats as pre-scored lookup block for LLM to use directly in Bibliography
- Added `paper_tier_reference=paper_tier_reference` to `format()` call

**`open_deep_research/src/deep_researcher.py`**
- Removed `from nodes.qa import qa_review` import
- Changed `supervisor_critique` return type to `Command[Literal["research_supervisor", "final_report_generation"]]`
- All `goto="qa_review"` → `goto="final_report_generation"`
- Removed `add_node("qa_review", qa_review)` and `add_edge("qa_review", "final_report_generation")`
- Comment added: `# swanson_abc and qa_review preserved for future use — not wired into graph`
- Graph docstring: `education_discovery → research_supervisor → supervisor_critique → final_report_generation`

### QA node removal rationale

The QA node was a secondary review pass that ran after synthesis but before report generation. With `supervisor_critique` already doing adversarial gap-finding + logical integrity checks on the full combined synthesis, and `researcher_reflect` catching DB coverage gaps at the researcher level, the QA node was redundant overhead. Removed to reduce latency and simplify the graph. Code preserved in `src/nodes/qa.py` for future use.

### Updated main graph flow

```
education_discovery → research_supervisor → supervisor_critique → final_report_generation
                                                   │ NEEDS_WORK (up to research_iterations - 1 cycles)
                                                   ↓
                                            research_supervisor (gap directive in supervisor_messages)
```

---

## Key Architectural Decisions (Running Log)

**Education Discovery — simplified (Phase 3):**
EVT+RST pre-planning was prototyped and validated but not shipped. Final design: supervisor decomposes queries into 4-6 focused sub-questions (1-2 sentences each) + keywords per researcher, all in one response. The 9 dimensions are sent to researchers as a soft evidence guide only. If a future phase requires structured coverage tracking across iterations, EVTs can be reintroduced at the supervisor level.

**Tavily budget**: Supervisor-unlocked after iteration 1. Up to 1 call per researcher in iteration 2. When exhausted → fall back to `anthropic_web_search` / `openai_web_search`.

**SerpAPI budget**: 2 calls per session total. Allocated by supervisor after iteration 1 to the 2 dimensions with weakest coverage. Not available in iteration 1.

**Synthesis iterations by depth:**
| Label | Iterations |
|---|---|
| Standard | 3 |
| Deep | 5 |
| Comprehensive | 7 |

**Critique architecture (Phases 4 + 5):**
- Researcher level: `researcher_reflect` — cheap Haiku gap audit, no web search, 1-cycle cap. Catches DB coverage gaps before compression.
- Supervisor level: `supervisor_critique` — Sonnet adversarial critique with web search on full combined synthesis, 1-cycle cap. Challenges conclusions at synthesis level, can re-dispatch targeted researchers.

**PDF extraction (Phase 7, active):**
- Only attempt PDFs for papers in `PDF_EXTRACTABLE_TOOLS` set (7 tools)
- arXiv = high success rate (100% OA), ERIC = mixed, Scopus = rarely accessible
- Always produces PaperProfile; falls back to abstract-only mode gracefully
- Quality/impact tier scored at extraction time by Haiku — not re-derived at report time

**KG write trigger (deferred):**
- `KGWriter` built; needs call in Render server after run completes
- Session write to Neo4j also needs new trigger (was handled by old Streamlit orchestrator)

**Citation chasing (Phase 11, later):**
- KG: `(Paper)-[:CITES {depth}]->(Paper)` relationships in Neo4j
- OpenAlex `referenced_works` field as primary citation source (structured, free)

**Swanson ABC:**
- Code preserved in `nodes/swanson.py` + `swanson_abc_prompt` in `prompts.py`
- Not wired into graph; fields in state.py kept as no-ops
- Re-wiring deferred until use case is clearer

**Novelty stopping signal:**
- v1 (Phase 2, active): LLM-instructed, prompt-based
- v2 (Phase 8b, later): code-based `seen_papers` set in ResearcherState, `novelty_rate` per round

---

## Bug Fixes — End-to-End Testing (Session 9/10)

### Root Cause: Researchers Not Completing

During end-to-end testing, all researchers returned "Error synthesizing research report: Maximum retries exceeded" after taking 282 minutes. Two separate bugs caused this:

**Bug 1 — `or True` in supervisor exception handler (`src/nodes/supervisor.py`)**

```python
# BEFORE (broken): always exited early on ANY exception, killing all researchers
if is_token_limit_exceeded(e, configurable.research_model) or True:
    return Command(goto=END, ...)

# AFTER: only exits on token limit, logs + re-raises other exceptions
logging.error(f"[supervisor_tools] exception: {type(e).__name__}: {e}\n{traceback.format_exc()}")
if is_token_limit_exceeded(e, configurable.research_model):
    return Command(goto=END, ...)
raise
```

**Bug 2 — `compress_research` sending structured tool_call content to OpenAI (`src/nodes/researcher.py`)**

gpt-4.1 researcher messages contain AIMessage objects with structured content blocks (`type: "function_call"`) from tool calling. Passing these directly to the compression model caused a 400 error:

```
BadRequestError: Invalid value: 'function_call'. Supported values are: 'text', 'image_url', ...
```

Fix: flatten all researcher_messages to plain text before building the compression payload:

```python
def _msg_to_text(msg) -> str:
    content = msg.content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                if block.get("type") == "text":
                    parts.append(block.get("text", ""))
                elif block.get("type") in ("function_call", "tool_use"):
                    name = block.get("name", "tool")
                    args = block.get("arguments") or block.get("input", "")
                    parts.append(f"[called {name}: {str(args)[:300]}]")
        content = "\n".join(parts)
    return str(content)

context_text = "\n\n".join(f"[{msg.__class__.__name__}]: {_msg_to_text(msg)}" for msg in researcher_messages)
messages = [SystemMessage(content=compression_prompt), HumanMessage(content=f"{context_text}\n\n---\n\n{compress_research_simple_human_message}")]
```

Also fixed: `compress_research` was checking `configurable.research_model` (wrong) for token limit; now checks `configurable.compression_model` (correct).

### Other Fixes Applied

**`src/utils/paper_filter.py`**
- `max_tokens`: 1024 → 2048 (prevented Pydantic parse failures)
- Added null byte / control char sanitization + 8000 char cap on papers_text before sending to models
- Scoring scale updated: 1–5 → 0–7; pass threshold: >1.5 → >2.5
  - 0 = irrelevant, 1-2 = tangential, 3 = indirect, 4-5 = relevant, 6-7 = direct hit

**`src/utils/pdf_extractor.py`**
- `max_tokens`: 2048 → 8192 (Haiku max)
- Input text cap: `text[:15000]` → `text[:60000]`

**`src/state.py`**
- Added `coerce_year` field_validator on `PaperProfile.year` — LLM sometimes returns "not_reported" string for int field; validator coerces to None

**`server.py`**
- Added `load_dotenv()` at startup
- Added `recursion_limit: 200` to both `astream` calls (default 25 causes GraphRecursionError in parallel researcher loops)
- Added `tool_calls: getattr(obj, "tool_calls", [])` to `serialize_value` for BaseMessage

**`edu_discovery_platform/app/api/research/stream/route.ts`**
- Added `export const maxDuration = 300` — Next.js route timeout was cutting connections after ~10s

### Result After Fixes
- Pipeline: 282 minutes → 3 minutes
- All researchers completing and returning real research notes
- 15K char report with actual citations generated
- `recursion_limit: 200` required in all run configs

---

## Phase 11 — Web Search Philosophy, SupervisorState Fix, Round 2 Deduplication (2026-03-18)

### Web Search Philosophy Flip (`src/prompts.py`, `src/utils/search.py`)

Previous behavior: `anthropic_web_search` / `openai_web_search` were described as targeted/specific retrieval; Tavily was used freely. This was backwards.

**New philosophy:**
- `anthropic_web_search` / `openai_web_search` — use freely for broad academic coverage. Find studies, evidence, and literature on the topic even without a specific paper in mind. Good starting point alongside academic DBs.
- `tavily_search` — use ONLY for targeted retrieval when you have a specific named study, paper, or policy doc you know exists but couldn't retrieve from another source. Before using Tavily, ask: "Is there a specific document I know exists that I need to retrieve?" If no → use anthropic/openai web search instead.

Updated in prompts.py: Available Tools section, QueryConstruction point 5, Round 1 mandatory sweep.
Updated in utils/search.py: `anthropic_web_search` and `openai_web_search` descriptions + `TAVILY_SEARCH_DESCRIPTION`.

### Mandatory Round 1 Sweep Updated (`src/prompts.py`)

`search_papers_by_relevance` (Asta) added to the mandatory 7-source Round 1 sweep:
1. `eric_search` ×1-2
2. `openalex_search` ×1-2
3. `arxiv_search` ×1
4. `elsevier_search` ×1
5. `scholar_search` ×1
6. `search_papers_by_relevance` ×2 (Asta — different embedding model, finds orthogonal papers)
7. `anthropic_web_search` or `openai_web_search` ×1-2

Round 2 updated: "Keep querying the academic DBs freely — eric, openalex, arxiv, elsevier, scholar_search, and Asta have no call limit."

### Paper Filter Threshold Lowered (`src/utils/paper_filter.py`)

```python
_PASS_THRESHOLD = 2.0  # was 2.5
```

Reason: openalex results were triggering the safety fallback (all papers dropped → pass all through) every time at 2.5. Lowered to 2.0 to allow more papers through while still filtering clearly irrelevant ones.

### SupervisorState paper_profiles Fix (`src/state.py`, `src/nodes/supervisor.py`)

**Root cause:** `SupervisorState` had no `paper_profiles` field. When `supervisor_tools` did `update_payload["paper_profiles"] = all_profiles`, LangGraph silently ignored the key (not in TypedDict). When the supervisor subgraph exited, the exit `Command` didn't include paper_profiles, so zero profiles propagated to parent `AgentState`.

**Fix — `src/state.py`:**
```python
class SupervisorState(TypedDict):
    supervisor_messages: Annotated[list[MessageLikeRepresentation], override_reducer]
    research_brief: str
    notes: Annotated[list[str], override_reducer] = []
    research_iterations: int = 0
    raw_notes: Annotated[list[str], override_reducer] = []
    thought_log: Annotated[list[dict], operator.add]
    source_counts: Annotated[dict, merge_source_counts]
    paper_profiles: Annotated[list[PaperProfile], operator.add]  # ADDED
```

**Fix — `src/nodes/supervisor.py`:** Added `paper_profiles` to both exit Commands:
```python
return Command(
    goto=END,
    update={
        "notes": get_notes_from_tool_calls(supervisor_messages),
        "research_brief": state.get("research_brief", ""),
        "paper_profiles": state.get("paper_profiles", []),  # ADDED
    }
)
```
Both the normal exit and the token-limit-exceeded exit updated.

### Round 2 Duplicate Sub-Questions Fix (`src/deep_researcher.py`)

**Root cause:** Supervisor in Round 2 was re-decomposing the research brief from scratch, then dispatching all original 5-6 researchers again PLUS the 4-5 new depth angles = ~10 researchers total (2× budget).

**Fix:** `supervisor_critique` now builds an explicit `⚠️ CRITICAL` depth directive:
```
DEPTH DIRECTIVE (cycle N/M)

⚠️ CRITICAL: Do NOT re-decompose the research brief. Do NOT re-dispatch researchers
on sub-questions similar to those already investigated. The previous round produced
{notes_count} research notes covering the initial sub-questions. That work is
complete and stored — do not re-run it.

Research brief: {research_brief}

**NEW angles to dispatch researchers on (ONLY these — no others):**
{directives_text}
...
```

The supervisor_messages for each critique round are reset to `[SystemMessage, HumanMessage(depth_directive)]` via `override_reducer`, which also prevents orphaned-tool-call corruption from the previous round's `ResearchComplete` AIMessage.

### `run_pipeline.py` Improvements

- `max_react_tool_calls`: 25 → 40 (allow researchers to use more diverse tools before hitting limit)
- Removed 4000-char truncation on final report (now prints full report)
- Added `sys.stdout.reconfigure(line_buffering=True)` at top — fixes buffering when stdout redirected to file on macOS (where `stdbuf` is unavailable)
- Added `flush=True` to `hr()`, `section()`, `subsection()` and key milestone prints (researcher done, paper_profiles count)
- Recommended run command: `python run_pipeline.py > /tmp/pipeline_test1.txt 2>/tmp/pipeline_test1_err.txt`

### Test Results (2-iteration run, 2026-03-18)

- Round 1 complete at +15m47s: 7 notes, 2,192 paper profiles (PDF extractor now working correctly)
- `supervisor_critique` fired at +17m13s
- Round 2 researchers dispatched and running

**Known issue — Tool diversity:** Despite the mandatory Round 1 sweep prompt, researchers consistently use only ERIC, OpenAlex, arXiv. `scholar_search`, Asta (`search_papers_by_relevance`), and Elsevier do not appear in notes. Likely cause: researchers hitting `ResearchComplete` voluntarily well before the 40-call limit. Root fix needed: stronger mandatory language, enforcement mechanism, or investigate early completion behavior.
