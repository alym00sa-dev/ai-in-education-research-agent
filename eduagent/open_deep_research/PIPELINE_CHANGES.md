# Pipeline Improvement Log

Track of all architectural changes, decisions, and deferred items across the pipeline improvement project.

---

## Roadmap

| # | Feature | Status |
|---|---|---|
| 1 | New academic DB tools + fetch limit + query guidance | ✅ Done |
| 2 | Strategy evolution (adaptive multi-round researcher search) | 🔄 In progress |
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
- Raised all DB fetch limits from 15 → 20 results per call so the relevance filter has a larger candidate pool to work from

**`src/utils/search.py`**
- Registered `arxiv_search`, `elsevier_search`, `scholar_search` in `get_all_tools()`

**`src/nodes/researcher.py`**
- Added `arxiv_search`, `elsevier_search`, `scholar_search` to `_ACADEMIC_DB_TOOLS` so they count toward academic source provenance tracking, not as Tavily web search calls

**`src/prompts.py`**
- Updated `research_system_prompt` Available Tools section to list all 5 DB tools correctly (was still referencing old 3-tool set)
- Added `<QueryConstruction>` block teaching the researcher to use quoted phrases, 2–3 query variations per round, academic signal words (RCT, meta-analysis, effect size), synonyms, and targeted grey literature queries for web search

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

## Phase 2 — Strategy Evolution (Adaptive Multi-Round Search) 🔄

### Goal
Replace single-pass DB searching with explicit multi-round strategy. Researcher calls DBs in round 1, reflects on gaps via think_tool, generates follow-up queries targeting what's missing, runs round 2, and stops when novelty drops.

### Design decisions
- **`max_react_tool_calls` raised**: 10 → 25. LLM compute is not a cost concern; the cap is purely a safety net against infinite loops. 25 gives room for ~3 genuine search rounds across 5 DBs.
- **Minimum 2 rounds**: researcher must always complete at least 2 search rounds before finishing, even if round 1 looks complete. Ensures query variation.
- **Novelty-based stopping (LLM-based, v1)**: researcher is instructed in the prompt to track how many papers in each round are genuinely new vs already seen. If novelty drops (few new relevant papers), stop and compress. Code-based novelty tracking (option 2) deferred to Phase 8 (quality delta tracking).
- **Round structure**: Round 1 = all 5 DBs with initial queries. Round 2 = 2–3 DBs with refined follow-up queries. Round 3+ = only if novelty still high.

### What changed
- `src/configuration.py` — `max_react_tool_calls` default: 10 → 25
- `src/prompts.py` — `research_system_prompt` `<Instructions>` and `<Hard Limits>` rewritten for multi-round adaptive search with novelty-based stopping

### Deferred
- Code-based novelty tracking (seen_papers set in ResearcherState, novelty_rate calculation) → Phase 8

---

## Key Architectural Decisions (Running Log)

**Education Discovery dimensions (9 always-on):**
1. Effect sizes & outcomes
2. Population & demographics
3. Intervention types & design
4. Implementation fidelity
5. Methodological landscape & study quality
6. Equity & differential effects
7. Longitudinal effects & sustainability
8. Comparative effectiveness
9. Cost, scalability & resource requirements

**Dynamic sub-areas**: 3–5 generated per query by the Discovery node, passed to supervisor as optional framing — not assigned to researchers. Supervisor uses them only if a dimension's findings are thin after round 1.

**Tavily budget**: 1 call per researcher max in iteration 1 (≤9 total). 1 call reserved for iteration 2 targeted follow-ups. When exhausted → fall back to LLM native web search (Anthropic `web_search_20250305`).

**SerpAPI budget**: 2 calls per session total. Allocated by supervisor after iteration 1 to the 2 dimensions with weakest coverage. Not available in iteration 1.

**Synthesis iterations by depth:**
| Label | Iterations |
|---|---|
| Standard | 3 |
| Deep | 5 |
| Comprehensive | 7 |

**Critique architecture (planned):**
- Researcher level: self-reflection node (gap identification, not adversarial) — replaces current adversarial critique_agent
- Supervisor level: adversarial critique agent (challenges full combined findings) — current critique_agent logic moves here

**PDF extraction (planned Phase 7):**
- Only attempt PDFs for papers passing multi-LLM pre-filter (≥2.25 avg score)
- arXiv = high success rate (100% OA), ERIC = mixed, Scopus = rarely accessible
- Extract: key findings, methodology, limitations, reference list as DOIs
- Reference DOIs feed into citation chasing pipeline (Phase 5, pending paper review)

**Citation chasing (planned Phase 5):**
- Paper: https://arxiv.org/pdf/2501.15552 — to be read before design decisions
- KG: `(Paper)-[:CITES {depth}]->(Paper)` relationships in Neo4j
- OpenAlex `referenced_works` field as primary citation source (structured, free)

**Novelty stopping signal (deferred to Phase 8):**
- v1 (Phase 2): LLM-instructed, prompt-based
- v2 (Phase 8): code-based seen_papers set in ResearcherState, novelty_rate per round
