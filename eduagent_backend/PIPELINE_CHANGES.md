# Pipeline Changes — EduAgent Backend

Track of all architectural decisions, shipped features, and the roadmap for the v2 pipeline.

---

## Repository Layout

| Folder | Purpose |
|--------|---------|
| `deep-research-src/` | Track A — LangGraph research pipeline (runtime) |
| `KG-src/` | Track B — KG corpus pipeline (offline weekly batch) |
| `output/` | Deep Research Run artifacts — one sub-folder per session (`output/<session_id>/`) |

---

## Two Parallel Tracks

This project has two tracks that eventually converge:

**Track A — Research Pipeline** (`deep-research-src/`)
The LangGraph pipeline that runs deep research on a query and produces a report. During a run it reads from Neo4j (KG lookup + CCM scores) but **never writes to Neo4j**. Papers discovered during a run are queued to `KG-src/ingested_papers/queue/` for the next weekly batch.

**Track B — KG Corpus Pipeline** (`KG-src/`)
Offline weekly ingestion: queue → pdf_extractor_kg → citation_chaser → CCM retrain → neo4j_writer (--skip-wipe). This is the only path that writes to Neo4j. Builds and maintains the curated AI-in-education corpus with typed citations and CCM scores.

They converge when: the research pipeline performs a KG-first lookup (Track B corpus) before dispatching researchers, and when the Citation Connector Agent uses the Run Graph to surface chains and gaps.

---

## Roadmap

### Track A — Research Pipeline

| # | Feature | Status |
|---|---|---|
| A1 | Core pipeline architecture (v2 rebuild) | ✅ Done |
| A2 | Two-pass report generation + Sonnet report model | ✅ Done |
| A3 | Report prompt tuning (design labels, concision, citation density) | ✅ Done |
| A4 | QA audit node (Opus judge) + benchmark infrastructure | ✅ Done |
| A5 | Queue write — papers found during run saved to `KG-src/ingested_papers/queue/` for next weekly ingest (no live Neo4j writes) | ✅ Done |
| A6 | KG backfill — process 358 legacy papers from old Streamlit pipeline | ✅ Done |
| A7 | KG-first lookup — queries KG corpus before dispatching researchers; KG papers added to source pool | ✅ Done |
| A8 | Citation Connector Agent — KG coverage check, gap analysis, feeds report prompt | ✅ Done |

### Track B — KG Corpus Pipeline

| # | Feature | Status |
|---|---|---|
| B1 | `pdf_extractor_kg.py` — 3-call extraction: metadata + KG taxonomy + citations | ✅ Done |
| B2 | `ingest_papers.py` — 35 queries (batch 1) × 4 DBs, relevance filter, typed output | ✅ Done |
| B2b | `ingest_papers.py` batch 2 — 75 additional queries (LLM families + broad AI×edu) | ✅ Done (71/75 run, 59 papers total) |
| B3 | `ingest_scale.py` — SCALE Stanford scraper (1,155 papers), empirical filter, same extraction | ✅ Done (163 papers, relevance ≥5/7) |
| B4 | Citation depth taxonomy — `citation_level` (L1/L2/L3) + `citation_context` in CitationRef | ✅ Done |
| B5 | `citation_chaser.py` — 1.5-hop traversal on L2+L3, multi-dir, fetch-refs mode for legacy | ✅ Done (242 seeds → 4,333 nodes, 5,165 edges, 993 ingest candidates) |
| B5b | `build_network.py` — JSON corpus → sparse adjacency matrix (paper × paper, L-weighted) | ✅ Done (2006 nodes, 2116 edges on 59-paper corpus) |
| B6 | Legacy paper conversion — kg_curator_v4 (30 papers) → corpus JSON format | ✅ Done (`convert_legacy.py`, output: `ingested_papers/legacy/`) |
| B7 | `neo4j_writer.py` — wipe + write Paper + Intervention + Finding + corpus-to-corpus CITES | ✅ Done (234 papers, 21 interventions, 204 findings; corpus-to-corpus CITES edges from 5,165-edge chase network) |
| B8 | CCM batch pipeline — build network → train CCM → write scores to Neo4j | ✅ Done (234 corpus papers scored; η, cluster_id, field_momentum, sb_coef live in Neo4j) |
| B9 | Weekly cron — ingest → chase → CCM → Neo4j update | ✅ Done |

---

## Current Architecture (Track A)

### Graph flow

```
education_discovery
  → research_supervisor (supervisor subgraph × research_iterations)
    → executive_summary
    → critique (iterations - 1 cycles, back to research_supervisor)
  → final_report_generation (two-pass: Pass 1 content, Pass 2 citation resolution)
  → qa_audit  ┐
  → kg_write  ┘  (parallel fan-out → END)
```

### Node summary

| Node | Model | Purpose |
|------|-------|---------|
| `education_discovery` | `model` | Transforms user query into `ResearchBrief` + 4-tier `tiered_question_map`; resets tool budgets |
| `research_supervisor` | `model` | Dispatches researchers across tiered sub-questions; aggregates notes + paper_profiles |
| `executive_summary` | `model` | Synthesizes all notes into a running executive summary (updated each iteration) |
| `critique` | `model` | Adversarial gap audit on executive summary; produces `next_iteration_brief` |
| `final_report_generation` | `report_model` | Pass 1: writes report with `<<Author, Year>>` tags. Pass 2: resolves to `[N]` |
| `qa_audit` | Claude Opus 4.6 | Scores report across 5 dimensions (0–100); saves run output to `output/final-test/<session_id>/` |
| `kg_write` | — | Saves full_text PaperProfiles to `KG-src/ingested_papers/queue/{session_id}/` for weekly batch |

### Researcher subgraph flow

```
researcher → researcher_reflect → [NEEDS_WORK: new keyword sweep]
                                 [PASS: compress_research]
```

Each researcher:
1. Generates `KeywordSet` (primary, variation, web queries) — 1 LLM call
2. Runs programmatic sweep: eric × 2 + openalex × 2 + arxiv × 1 + elsevier × 1 + web × 1 + asta × 2
3. Runs paper filter ensemble (Haiku + gpt-mini, 0–7 scale, threshold 2.0)
4. Attempts PDF extraction → `PaperProfile` (full_text or abstract_only)
5. Reflects on coverage gaps — if NEEDS_WORK, runs up to `max_sweep_cycles` additional sweeps

### Key configuration (production benchmark)

```python
CONFIG = {
    "configurable": {
        "model": "openai:gpt-5.4-mini-2026-03-17",
        "report_model": "openai:gpt-5.4-2026-03-05",
        "research_iterations": 3,        # always 3 (frontend + CLI)
        "max_concurrent_researchers": 5,
        "max_sweep_cycles": 2,
        "tavily_budget": 8,
        "serp_budget": 2,
        "enable_pdf_extraction": True,
        "max_sources": 30,
        "session_id": "",                # set by frontend; enables background persistence
    },
    "recursion_limit": 200,
}
```

---

## KG Corpus Architecture (Track B)

### The Two Graphs

**Graph 1 — The KG (Neo4j, persistent)**
- 2023+ AI/EdTech/LLM intervention papers only — fully extracted (`PaperProfileV2`)
- CITES edges only between corpus papers (corpus-to-corpus only — no stubs for non-corpus papers)
- CCM scores on Paper nodes: fitness η, cluster_id, field_momentum (written by weekly batch)
- **Never written to during a research run** — read-only at run time
- Pre-2023 papers are NEVER in the KG under any circumstances

**Graph 2 — The Run Graph (ephemeral, per research run)**
- Built live during a research run by the Citation Connector Agent (A8)
- Contains everything found in that run:
  - Corpus papers (in KG) → pulled from Neo4j with full data including CCM scores
  - New 2023+ papers found live → lightweight S2 metadata only; queued for next weekly ingest
  - Pre-2023 papers appearing as L2/L3 citations → S2 fast lookup (title, year, abstract, citation count)
- This is where gap surfacing and hypothesis generation happen — NOT in Neo4j
- Saved as a run artifact (`_run_graph.json`) alongside the report
- **Never written to the KG**

### Separation of Work

| | KG (Neo4j) | Run Graph |
|---|---|---|
| Paper scope | 2023+ corpus papers only | Everything found in this run |
| Pre-2023 papers | Never | Yes, as lightweight S2 nodes |
| CITES edges | Corpus-to-corpus only | Full traversal including pre-2023 |
| CCM | Trained offline weekly on full `_chase_network.json` | Reads pre-computed scores from KG |
| Writes during run | Never (read-only) | Built live by A8 |
| Lifetime | Permanent, growing weekly | One run → saved as artifact |
| Purpose | "What does the field know, with what quality?" | "How is this question built? Where are the gaps?" |

### How CCM and Gap Surfacing Work Together

**Offline (weekly batch):**
1. `citation_chaser.py` builds `_chase_network.json` — the full citation graph including pre-2023 ancestors and non-corpus papers
2. CCM trains on `_chase_network.json` (L3-weighted adjacency matrix) — this is where pre-2023 ancestry is captured
3. CCM writes per-paper scores (`η`, `cluster_id`, `field_momentum`) back to Neo4j **corpus Paper nodes only**
4. Non-corpus and pre-2023 papers never get Neo4j nodes — their influence is captured in the scores of corpus papers

**Live (during a research run, via A8):**
1. Papers found during the run → A8 checks KG for each: if in corpus, pulls full node including CCM scores
2. A8 builds Run Graph: corpus papers (with η scores) + new papers + pre-2023 ancestors (all via live S2 lookups)
3. Gap analysis runs on the Run Graph structure:
   - High-η corpus papers with no 2023+ extensions for a given population → gap
   - L3 ancestor cited by many corpus papers but with thin experimental extension → hypothesis surface
   - Cluster with high field_momentum but no RCT evidence → priority research slot
4. Output fed into final report prompt: intellectual lineage, gaps, field anchors, hypothesis surfaces
5. New papers found during the run → saved to `KG-src/ingested_papers/queue/` for next weekly ingest

### Citation Depth Taxonomy

Every CITES edge in the KG (and Run Graph) carries a depth level:

| Level | Name | Definition |
|---|---|---|
| L1 | Referential | Mentioned in passing — "as noted by Smith et al." No intellectual dependency |
| L2 | Grounded | Used to build the theoretical foundation, lit review, or methodology |
| L3 | Foundational | Directly extends: same methodology, same experiment design, direct replication or iteration |

Extracted in Call 3 of `pdf_extractor_kg.py`. Each `CitationRef` has:
- `citation_level: Literal[1, 2, 3]`
- `citation_context: str` — brief phrase showing why it's cited

L1 citations are noise for traversal purposes. Citation chaser and Citation Connector Agent only traverse L2+L3.

### KG Corpus Pipeline flow

```
── Corpus Assembly (3 sources) ──────────────────────────────────────────

  [Source 1] ingest_papers.py  (B2 + B2b: 110 queries × 4 DBs → 59 papers)        ✅
  [Source 2] ingest_scale.py   (B3: SCALE Stanford, 163 papers, ≥5/7 relevance)   ✅
  [Source 3] convert_legacy.py (B6: 30 kg_curator_v4 papers → ingested_papers/legacy/) ✅
             Total corpus: 252 papers (242 after dedup)

  Each source → Relevance filter (≥3/7), year ≥ 2023, verdict filter
             → pdf_extractor_kg.py (Sources 1 & 2; Source 3 already extracted)
               Call 1: Metadata (study design, population, geography, limitations)
               Call 2: KG Taxonomy (tool ID, findings, verdict, quality/impact tiers)
               Call 3: Citations (CitationRef list with citation_level + citation_context)
             → Output: ingested_papers/{source}/
                 {doi_slug}.json   — PaperProfileV2 per paper
                 _summary.json     — index: title, tool, verdict, quality tier
                 _citations.json   — flat deduplicated cited works
                 _query_stats.json — per-query yield

── Citation Chase ────────────────────────────────────────────────────────

  citation_chaser.py — unified run across all 3 sources
    Hop 1:   Resolve L2+L3 citations via Semantic Scholar (3s rate limit, anonymous)
    Hop 1.5: For 2023+ hop-1 papers, fetch their references from S2
    Note:    Legacy papers (Source 3) have no citations in JSON →
             treated as "fetch-refs" seeds: S2 reference list fetched directly
    Output:  _chase_network.json + _ingest_queue.json

── Network Build ────────────────────────────────────────────────────────

  build_network.py — JSON → sparse adjacency matrix (paper × paper)
    L1 edges weight=1, L2 weight=2, L3 weight=3
    Output: _network_matrix.npz + _network_nodes.json + _network_stats.json

── Initial Neo4j Full Rebuild (one-time) ───────────────────────────────

  Step 0: WIPE — MATCH (n) DETACH DELETE n  (clean slate — one time only)

  neo4j_writer.py — writes from all sources:
    Paper nodes        — from all ingested JSONs (full PaperProfileV2 profile)
    Intervention nodes — from tools_final (21 tool files)
    EVALUATES edges    — paper → intervention (from tools_final evidence)
    EmpiricalFinding   — from tools_final findings per paper
    CITES edges        — corpus-to-corpus only (MATCH, not MERGE — no stubs)
                         Source: _chase_network.json, filtered to edges where
                         BOTH source AND target are already corpus Paper nodes

── CCM Training (offline, on full network) ──────────────────────────────

  Reads: _chase_network.json (full graph — corpus + pre-2023 ancestors)
  Trains: L3-weighted adjacency → η (fitness), cluster_id, field_momentum per paper
  Writes: scores back to Neo4j corpus Paper nodes only
  Note: CCM sees the full ancestry via the JSON file — pre-2023 ancestors
        inform scores even though they have no Neo4j nodes

── Weekly Incremental Update (no wipe after initial rebuild) ────────────

  1. pdf_extractor_kg on KG-src/ingested_papers/queue/ (papers queued during research runs)
  2. citation_chaser.py --incremental: new papers only → merge into _chase_network.json
  3. CCM retrain on full updated _chase_network.json → SET η/cluster/momentum on all Paper nodes
  4. neo4j_writer.py --skip-wipe: MERGE new Paper nodes + new corpus-to-corpus CITES edges
  5. Archive KG-src/ingested_papers/queue/ with date stamp
```

### Citation Connector Agent (Track A × Track B convergence)

Runs as a LangGraph node after all researchers complete. Builds the Run Graph, surfaces gaps and hypotheses, feeds structured analysis into the final report prompt.

**Input:** All papers collected during the run (`paper_profiles` from researcher nodes)

**Step 1 — KG lookup for each paper:**
- Check Neo4j: is this paper in the corpus?
- If yes → pull full node including pre-computed CCM scores (η, cluster_id, field_momentum)
- If no → mark as new, save to `KG-src/ingested_papers/queue/` for next weekly ingest

**Step 2 — Build Run Graph via live S2 traversal:**
- For each paper (corpus or new), fetch its L2+L3 citations from S2
- For each cited paper:
  - 2023+ AND in corpus → pull from KG (has CCM scores)
  - 2023+ NOT in corpus → lightweight S2 node (no scores yet)
  - Pre-2023 → lightweight S2 node (never in KG — foundational context only)
- Run Graph grows to include the full ancestry of papers found this run

**Step 3 — Gap and hypothesis analysis on the Run Graph:**
- **Field anchors**: pre-2023 papers L3-cited by many run papers → load-bearing foundations
- **Chain termination gaps**: high-η corpus papers with no extension for a given population, methodology, or outcome → explicit research gaps
- **Thin chains**: L3 ancestor with only 1-2 corpus extensions → underexplored
- **Momentum gaps**: high field_momentum cluster (from CCM) with no RCT evidence → priority experimental slot
- **Sleeping beauties**: paper with high η but sparse neighborhood at time of publication → recently rediscovered influence

**Step 4 — Output fed into final report prompt:**
```json
{
  "intellectual_lineage": "AI writing feedback research builds on a 2016 SRL framework (L3-cited by 6 of 8 papers found this run)",
  "gaps": [
    "No RCT extending the SRL framework to K-12 populations",
    "No long-term follow-up studies for ITS math interventions"
  ],
  "field_anchors": ["Smith 2016 SRL framework — L3 ancestor of 6 corpus papers, η=0.87"],
  "sleeping_beauties": ["Jones 2020 — published in sparse niche, now L3-cited by 4 recent studies"],
  "hypothesis_surfaces": ["SRL framework × K-12 math × RCT design is an open experimental slot"],
  "new_papers_queued": 3
}
```

**Key design point:** Gap surfacing happens on the Run Graph, not on Neo4j. Neo4j provides the CCM scores that tell you *which* papers are important. The Run Graph provides the ancestry structure that tells you *where* the gaps are. Pre-2023 ancestors are critical to gap analysis — they only ever appear in the Run Graph, never in Neo4j.

---

## KG Rebuild Plan (Session 11 — 2026-04-01)

Full wipe and rebuild of Neo4j from three combined corpus sources. This supersedes the incremental approach previously used by A5/A6 (kg_writer.py writes during pipeline runs). The KG is now built exclusively by the offline corpus pipeline (Track B).

### Corpus sources

| Source | Script | Papers | Status |
|--------|--------|--------|--------|
| Query ingest (batch 1+2) | `ingest_papers.py` | 59 papers | ✅ Done |
| SCALE Stanford repo | `ingest_scale.py` | ~400 expected | 🔄 Running |
| Legacy kg_curator_v4 | conversion script | 30 papers | ✅ Done |

### Execution order

```
Phase 0  ✅ Kick off SCALE ingest — 163 papers (relevance ≥5/7), 5,706 citations
Phase 1  ✅ Legacy conversion — convert_legacy.py → ingested_papers/legacy/ (30 papers)
Phase 2  ✅ citation_chaser.py enhanced:
           - Multi-dir: --papers-dir accepts multiple paths
           - fetch-refs mode: seeds with empty citations[] → S2 reference fetch (pre-hop)
           - --output-dir flag for merged output
           - CrossRef title→DOI resolution (avoids S2 /paper/search endpoint entirely)
           - asyncio.Semaphore(5) on CrossRef, Semaphore(1) on S2 (serialized)
           - 429 storm detector: ≥3 consecutive → 5-min cooldown
           - --skip-prehop flag: bypass legacy seed pre-hop
           - Progress logging: every 50 hop-1 resolutions
           - S2 API key support (2s/req with key, 8s anonymous)
Phase 3  ✅ Full citation chase completed (2026-04-03)
           242 seeds → 465 hop-1 → 3,626 hop-1.5
           4,333 total nodes, 5,165 edges, 993 ingest candidates
           77.7% DOI coverage, 0 dangling edges
Phase 4  ✅ Network matrix rebuilt (build_network.py on merged output)
Phase 5  ✅ neo4j_writer.py --skip-wipe: corpus-to-corpus CITES edges pushed to Neo4j
           (only edges where BOTH nodes are corpus Paper nodes; full network stays in _chase_network.json)
Phase 6  ✅ Citation Connector Agent (A8) — built
Phase 7  ✅ CCM training + score write-back (B8) — 234 papers, 15 clusters, η/cluster_id/field_momentum/sb_coef in Neo4j
Phase 8  ✅ Weekly batch script (B9) — scripts/run_weekly_batch.py
```

### Key decisions

**Why wipe Neo4j:** The existing graph was written incrementally by the research pipeline (A5) using old field schemas (`population: str`, no citation edges, no quality tiers on all papers). Starting clean avoids merging two different extraction schemas.

**Why legacy papers have no citations in JSON:** The kg_curator_v4 extractions predate the CitationRef schema. Rather than re-extracting from PDFs, the citation_chaser "fetch-refs" mode will pull their reference lists from S2 directly — faster and sufficient for building the citation network.

**S2 API key:** Active (`xeY7y6MY4J9YP6ID4EPDr7v8v2vNQEdk8Ojew2RV`). Throttle: 2s/req. `x-api-key` header enabled in `citation_chaser.py` config block.

---

## Phase-by-Phase Details

### A1 — Core Pipeline Architecture ✅

**What changed from v1**

*Sweep-based researchers (not tool-calling loop)*
- v1: Researcher runs an open-ended ReAct loop; often exhausted max_react_tool_calls before hitting all DBs
- v2: 1 LLM call generates `KeywordSet` → programmatic `asyncio.gather` sweep. All DBs always hit.

*Tiered question map*
- v1: Flat sub-questions
- v2: 4-tier map (Tier 1 = foundational framing, Tier 2 = baseline/comparators, Tier 3 = mechanisms, Tier 4 = effect sizes). Ensures full evidence coverage.

*Executive summary loop*
- v1: Single critique pass
- v2: `executive_summary` synthesizes notes after each round. `critique` audits the synthesis for gaps (not raw notes). Drives `next_iteration_brief`.

*Two-pass report + source pool*
- v2: Ranked source pool from `paper_profiles`. Pass 1 writes `<<Author, Year>>` tags. Pass 2 resolves to `[N]`.

*QA audit*
- v2: Claude Opus 4.6 as judge, 5-dimension scoring.

---

### A2 — Two-Pass Report Generation ✅

`deep-research-src/nodes/report.py`:
- Pass 1: `report_model` writes full report with `<<Author, Year>>` tags
- Pass 2: resolves all tags to `[N]` against numbered source pool
- `_post_process_report`: programmatic cleanup; builds bibliography

`deep-research-src/configuration.py`: `report_model` field (falls back to `model` if empty).

**Why Sonnet for report generation:** `gpt-5.4-mini` hard-capped at ~10 unique citations. Sonnet 4.6 consistently produces 17–36.

---

### A3 — Report Prompt Tuning ✅

Three targeted rules in `deep-research-src/prompts/report.py`:
- Design label accuracy: use exact "Design:" field from SourcePool, never infer or upgrade
- Concision + completeness: direct evidence, no filler, every sub-question covered
- Citation density: every claim carries its citation at the point of the claim

---

### A4 — QA Audit Node ✅

`deep-research-src/nodes/qa.py` — Claude Opus 4.6 as judge:
- Structured `QAScores` output first (reliable), then prose `qa_report`
- Scores: citation linkage (20) + statistic provenance (25) + study design accuracy (15) + sub-question coverage (20) + URL integrity (20) = 100

`benchmark.py` — sequential 4-query runner with TSV logging
`benchmark_model_compare.py` — research once → 4 report models in parallel

---

### A5 — Queue Write ✅

No live Neo4j writes. `deep-research-src/nodes/kg_write.py` saves full_text PaperProfiles to `KG-src/ingested_papers/queue/{session_id}/` as individual JSONs. Node still wired as fan-out after `final_report_generation` — behaviour change is internal only.

Weekly batch treats `KG-src/ingested_papers/queue/` as a fourth corpus source → citation_chaser --incremental → CCM retrain → neo4j_writer --skip-wipe.
- `deep-research-src/graph.py` → node rename from `kg_write` to `queue_write` (wiring unchanged)

---

### A6 — KG Backfill ✅

358 legacy papers from old Streamlit pipeline re-extracted and written to Neo4j. Backfill complete — all Paper nodes now have full `quality_tier`, `impact_tier`, `outcome_assignments`, and `extended_summary` fields.

---

### A7 — KG-First Lookup ✅

Before dispatching researchers, `education_discovery` queries Neo4j for papers already in the KG relevant to the research brief. Injected into supervisor context as a starting evidence base. Researchers fill gaps the KG doesn't cover.

`deep-research-src/utils/kg_retriever.py` — NEW: `query_kg_for_topic(research_brief, tiered_question_map, top_k=30)`

---

### A8 — Citation Connector Agent ✅

New LangGraph node built in Session 12. Builds the Run Graph, traverses L2+L3 citations, analyzes chains and gaps, outputs genealogy + hypothesis surface into the final report prompt.

Full design: see "Citation Connector Agent" section above.

**Status:** Built. Pending live end-to-end test with CCM scores in Neo4j (requires B8).

---

### B1 — pdf_extractor_kg.py ✅

`deep-research-src/utils/pdf_extractor_kg.py` — 3 parallel LLM calls per paper (KG schema, used by weekly batch only):
- Call 1: `PaperMetadataExtract` — study design, population, geography, limitations, extended_summary
- Call 2: `PaperKGExtract` — `IdentifiedTool` list (name, specificity, category_key, findings), verdict, quality/impact tiers
- Call 3: `PaperCitationExtract` — `CitationRef` list (title, doi, year, venue)

PDF fetch chain: explicit URL → arXiv derivation → Unpaywall (DOI) → Semantic Scholar title search → abstract-only shell

---

### B2 — ingest_papers.py ✅

`scripts/archive/ingest_papers.py` (archived — B2 corpus fully assembled):
- 51 queries across 5 groups: tool-specific, topic/outcome, framework/emerging, named tools, GenAI × population
- 4 DBs: ERIC, OpenAlex, arXiv, Semantic Scholar
- Thresholds: RELEVANCE_THRESHOLD=3/7, ARXIV_THRESHOLD=2/7, MIN_YEAR=2023
- Post-extraction drop rules: no_tool; framework_only + (red OR Qualitative)
- Per-query performance tracking → `_query_stats.json`
- Output: `ingested_papers/YYYY-MM-DD/`

---

### B3 — ingest_scale.py ✅

`KG-src/ingest_scale.py`:
- Scrapes SCALE Stanford AI Repository (1,155 curated papers, 39 pages)
- Study design pre-filter: keeps Impact (RCT, Quasi-Experimental), Systematic Review, Quantitative
- Relevance filter **≥5/7** (raised from 3 — tighter focus on intervention studies), MIN_YEAR=2023
- arXiv PDF URL extracted from detail pages
- Same output format as ingest_papers.py
- `--dry-run` flag for testing (page 1 only)

**Run result (2026-04-02):** 418 candidates at ≥3 → 196 at ≥5 → **163 papers extracted**
- 5,706 citations, avg 35/paper
- Verdicts: 139 named_tool_found, 16 genai_general, 6 archetype_only, 2 framework_only
- Quality: 34 green, 125 yellow, 1 blue, 3 red
- Top tools: ChatGPT (92), GenAI General (41), Gemini (20), Claude (10), LLaMA (10)
- Output: `ingested_papers/scale_2026-04-01/`

---

### B4 — Citation Depth Taxonomy ✅

`CitationRef` in `pdf_extractor_kg.py`:

```python
class CitationRef(BaseModel):
    title: str
    doi: Optional[str] = None
    year: Optional[int] = None
    venue: Optional[str] = None
    citation_level: Literal[1, 2, 3]       # L1=referential, L2=grounded, L3=foundational
    citation_context: Optional[str] = None  # brief phrase showing why cited
```

Call 3 prompt uses a "removal test" to classify each citation. All 59 ingested papers have `citation_level` and `citation_context` on every CitationRef.

Also updated: `populations: list[str]` and `user_types: list[str]` (previously single strings) with explicit enum values — allows multi-group papers to list all groups rather than collapsing to "Mixed".

---

### B5 — Citation Chaser ✅

`KG-src/citation_chaser.py` — 1.5-hop traversal on L2+L3 citations:

**Hop 1:** S2 lookup (by DOI → CrossRef title→DOI → S2) for every L2/L3 citation from seed papers
**Hop 1.5:** For 2023+ hop-1 papers, fetch their own reference list from S2 (`/paper/{id}/references`)

**Rate limiting:** `asyncio.Semaphore(1)` on S2 (serialized) + 2s sleep with key / 8s anonymous. `asyncio.Semaphore(5)` on CrossRef. Retries 3× on 429 with exponential backoff.

**S2 API key:** Active (`x-api-key` header in config block). Throttle: 2s/req.

**CrossRef integration (Session 12):**
- `_crossref_resolve_doi(title)` — queries CrossRef `api.crossref.org/works` with title; validates result via Jaccard similarity ≥ 0.5; returns DOI or None
- `lookup_by_title` now routes through CrossRef→DOI→S2 `/paper/DOI:{doi}` — avoids the throttled `/paper/search` S2 endpoint entirely
- `_cr_sem = asyncio.Semaphore(5)` prevents httpx pool exhaustion from concurrent CrossRef calls

**429 storm detector:**
- Global `_s2_consecutive_429s` counter; if ≥ 3 consecutive → 5-min cooldown + counter reset
- On any S2 success → counter resets to 0

**Other enhancements (Sessions 11–12):**
- **fetch-refs mode** — seeds with empty `citations[]` (legacy papers) → pre-hop fetches full reference list from S2
- **Multi-dir support** — `--papers-dir` accepts multiple paths; deduplicates by DOI then title
- **`--output-dir`** — separate output path for merged `_chase_network.json` and `_ingest_queue.json`
- **`--skip-prehop`** — bypasses legacy seed pre-hop (avoids burning API quota at start of Hop 1)
- **Progress logging** — every 50 hop-1 resolutions logs `[hop1] N/total resolved...`

**Full run result (2026-04-03, with API key):**
```
242 seeds → 465 hop-1 papers → 3,626 hop-1.5 papers
4,333 total nodes, 5,165 edges
77.7% DOI coverage, 993 ingest candidates, 0 dangling edges
```

**Run command:**
```
python3.13 citation_chaser.py \
  --papers-dir ingested_papers/2026-04-01 ingested_papers/scale_2026-04-01 ingested_papers/legacy \
  --output-dir ingested_papers/merged \
  --skip-prehop
```

---

### B5b — Network Builder ✅

`KG-src/build_network.py`:
- Reads all paper JSONs from corpus directory
- Builds node index (seed papers + all cited works)
- COO adjacency data with `citation_level` as edge weight (L3=3, L2=2, L1=1)
- Outputs: `_network_nodes.json`, `_network_adj.json`, `_network_matrix.npz`, `_network_stats.json`

Result on 59-paper corpus: 2006 nodes, 2116 unique edges (L1=1643, L2=309, L3=171). Top hub: "chain-of-thought prompting" (6×).

---

### B6 — Legacy Paper Conversion ✅

`KG-src/convert_legacy.py` — converts 30 `kg_curator_v4` papers matched to `tools_final` source papers:

- Field remapping: `population` → `populations: list[str]`, `user_type` → `user_types: list[str]` with intelligent multi-group parsing
- `ai_methods` → `identified_tools` (field rename; `is_named_product: True` added)
- `citations: []` (empty — citation_chaser fetch-refs mode will populate from S2)
- `extraction_status: "full_text"`, `_legacy_source: "kg_curator_v4"`
- Output: `ingested_papers/legacy/` (30 files + `_summary.json`)
- 15 of 45 kg_curator_v4 files skipped (not referenced in tools_final)

---

### B7 — Neo4j Full Rebuild ✅ (built + dry-run validated)

`KG-src/neo4j_writer.py`:

**Step 0:** `MATCH (n) DETACH DELETE n` — wipe all existing nodes and relationships (`--skip-wipe` to upsert instead).

**Writes:**
- `Paper` nodes — from all ingested JSONs across all 3 corpus sources (MERGE on DOI, title fallback); skips `red` quality and `framework_only` verdict papers
- `Intervention` nodes — from `KG-src/tools_final/*.json` (21 tool files) with `intervention_id`, `specificity`, `category_key`
- `EVALUATES` edges — `(Paper)-[:EVALUATES {use_case, study_design, original_name}]->(Intervention)`
- `EmpiricalFinding` nodes — from tools_final evidence → findings per paper, linked via `REPORTS_FINDING` and `PRODUCES_FINDING`
- `CITES` edges — corpus-to-corpus only: `(Paper)-[:CITES {hop, citation_level, context}]->(Paper)`
  Both source AND target must exist as corpus Paper nodes — no lightweight stubs for non-corpus papers.
  Fix pending: `write_cites_edges` must use `MATCH` (not `MERGE`) for target nodes.

**Full run result (2026-04-03, `--skip-wipe` after Phase 3):**
- 234 Paper nodes, 21 Interventions, 204 EmpiricalFindings
- CITES edges: corpus-to-corpus only — `OPTIONAL MATCH` on both source and target, skips edge if either node is not already a corpus Paper node (no stubs for non-corpus/pre-2023 papers)
- Full 5,165-edge network lives in `_chase_network.json`; CCM trains on that file (not Neo4j)

**Run:** `python3.13 neo4j_writer.py --skip-wipe` (after citation_chaser full run)

---

### B8 — CCM Batch Pipeline ✅

`KG-src/ccm_trainer.py` — trains our adapted version of the Community Citation Model (CCM) on the full chase network (`_chase_network.json`, 4,333 nodes, 5,165 edges) and writes per-paper scores to Neo4j.

#### The original CCM (Kojaku et al. 2025, arXiv:2501.15552)

CCM models how knowledge communities collectively cite existing publications. Each paper is embedded as a unit vector on a K-dimensional hypersphere. Citation probability depends on three factors:

```
P_CCM(j | i) ∝ (c_j(t_i) + c_0) · η_j · exp(-κ · d(u_i, u_j))
```

- `c_j(t_i)`: citation count of paper j at the moment paper i was published (preferential attachment)
- `η_j`: intrinsic fitness — how much a paper is cited beyond what its count and position alone would predict
- `exp(-κ · d(u_i, u_j))`: cosine proximity in embedding space (topical relevance)
- Trained jointly via Noise Contrastive Estimation (NCE). `cluster_id` is not a native output — CCM embeds papers into continuous space and community structure is read off post-hoc via k-means on `u_j`.

#### Our implementation

We use the paper authors' own code where available and approximate only where the full model's data requirements can't be met (temporal citation timestamps per event):

| Output | CCM original | Our approach | Source |
|--------|-------------|--------------|--------|
| `u_j` (K=128 embedding) | Learned jointly via NCE on citation events | **fastRP** on L-weighted directed graph | Kojaku et al.'s own `fastRP.py` from the CCM repo — ported directly |
| `cluster_id` | K-means on `u_j` post-hoc | **K-means on fastRP `u_j`** | Identical to CCM's prescribed step |
| `η` (fitness) | Learned via NCE jointly with `u_j` | **Weighted PageRank** (L-weighted, α=0.85) | NCE requires `c_j(t_i)` — citation count of j at exact moment i was published. We only have publication years, not per-citation timestamps. PageRank is the best available proxy: same "cited by important papers" signal |
| `SB_coef` / `is_sleeping_beauty` | Explained naturally by CCM's community drift | **Ke et al. (2015) SB coefficient** | Kojaku et al.'s own `calc_SB_coefficient` from `utils.py` — ported directly |
| `field_momentum` | Not in CCM — our metric | Fraction of in-edges to cluster from 2024+ source papers | Measures whether a sub-field is actively building on the cluster's work |

#### fastRP (embeddings)

fastRP (Fast Random Projection, Chen & Tian 2019) propagates random projections through the graph using a transition matrix and degree normalisation. It captures k-hop neighbourhood structure without random walks — much faster than Node2Vec for our network size.

```python
EMBEDDING_DIM = 128   # K — confirmed in CCM paper
WINDOW_SIZE   = 5     # propagation steps (captures 5-hop neighbourhood)
BETA          = -1    # degree normalisation (strongest — normalises by in-degree)
```

`edge_direction=True` gives separate out-embedding (what a paper cites) and in-embedding (who cites it). We use the out-embedding as `u_j` — it captures what intellectual territory a paper draws from, matching CCM's citation-space positioning.

#### SB coefficient (sleeping beauties)

Exact Ke et al. (2015) formula: for each cited paper j, the SB coefficient measures how long it was "sleeping" (low citation count) before "awakening" (sudden surge). A high `SB_coef` = ignored at publication, later widely rediscovered.

```
B = Σ_{t=0}^{t_m} (m·t + c_0 - c_t) / max(1, c_t)
```
where `t_m` is the year of peak citation count, `c_0` is citations in year 0, `m` is the slope from `c_0` to the peak, and `c_t` is citations in year t.

For a 2023-2026 corpus the citation lag is naturally short. Raw `sb_coef` is stored on all papers; `is_sleeping_beauty = True` is flagged at threshold ≥ 1.0 (tunable via `--sb-threshold`).

#### Configuration

```python
N_CLUSTERS    = 15    # k-means k (tunable)
EMBEDDING_DIM = 128   # K — matches CCM paper
WINDOW_SIZE   = 5     # fastRP propagation steps
SB_THRESHOLD  = 1.0   # min SB_coef to flag is_sleeping_beauty
```

#### Outputs

Written to Neo4j corpus Paper nodes (MATCH by DOI, title fallback):
```
p.eta                 — fitness score in [0, 1] (normalised PageRank)
p.cluster_id          — integer community ID from k-means on fastRP embeddings
p.field_momentum      — [0, 1] fraction of cluster's in-edges from 2024+ papers
p.is_sleeping_beauty  — boolean: SB_coef >= threshold
p.sb_coef             — raw Ke et al. sleeping beauty coefficient (float)
p.ccm_run_date        — ISO date of training run
```

Saved locally (always, even in dry-run):
```
ingested_papers/merged/_ccm_scores.json     — per corpus paper: all scores + in/out degree
ingested_papers/merged/_ccm_embeddings.json — 128-dim u_j per corpus paper (for A8 similarity search)
```

#### Run

```
python3.13 KG-src/ccm_trainer.py           # train + write to Neo4j
python3.13 KG-src/ccm_trainer.py --dry-run  # train only, skip Neo4j
python3.13 KG-src/ccm_trainer.py --n-clusters 20 --num-walks 15
```

---

### B9 — Weekly Incremental Cron ✅

No full wipe after the initial rebuild. Incremental only:

```
Weekly batch:
  1. pdf_extractor_kg on KG-src/ingested_papers/queue/ — extract papers queued during research runs
  2. citation_chaser.py --incremental — chase only new papers, merge into _chase_network.json
  3. CCM retrain on full updated _chase_network.json → SET η/cluster/momentum on all Paper nodes
  4. neo4j_writer.py --skip-wipe — MERGE new Paper nodes + corpus-to-corpus CITES edges only
  5. Archive KG-src/ingested_papers/queue/ with date stamp
  Optional: ingest_papers.py / ingest_scale.py for new DB queries (monthly, not weekly)
```

`KG-src/run_weekly_batch.py` — orchestrates all steps end-to-end:
```
python KG-src/run_weekly_batch.py            # full run
python KG-src/run_weekly_batch.py --dry-run  # log actions only
python KG-src/run_weekly_batch.py --skip-extraction  # skip re-extraction, use existing dated dir
```

**`--incremental` mode** (built): loads existing `_chase_network.json` → identifies already-processed seed keys → chases only new seeds → merges new nodes+edges into the existing network (deduplicates by DOI/title key). The weekly batch always runs with `--incremental`.

---

## Key Architectural Decisions (Running Log)

**Why 2023 as the KG cutoff:**
2023 is when the field exploded post-ChatGPT. Papers from 2022 are sparse and methodologically thin (most are early reaction pieces). 2023+ gives a denser, more useful corpus. Pre-2023 papers appear in the Run Graph as ancestry context but are never stored in the KG.

**Why pre-2023 papers are NOT in the KG:**
The KG is the curated intervention space — what AI tools do, with what evidence, at what quality. Pre-2023 papers are foundational context, not interventions. Mixing them in would blur the KG's purpose. They're handled ephemerally by the Citation Connector Agent during a run.

**Why the Run Graph is ephemeral:**
Building a permanent cross-era citation network (2023+ interventions + pre-2023 ancestors) would require managing two very different extraction depths in the same graph. The Run Graph solves this cleanly: it's built fresh each run from whatever is found, using KG data where available and fast lookups where not.

**Why CCM on a typed graph (L3-weighted):**
Plain citation count treats a passing mention the same as a direct methodological extension. L3 edges are genuine intellectual dependencies. Weighting them higher in CCM training means fitness η reflects actual influence in the field, not just how often a paper appears in reference lists.

**Why citation chaser traverses L2+L3 only:**
L1 citations are noise — a paper mentioning 50 tangential works shouldn't expand the corpus 50x. L2+L3 are substantive intellectual connections. Restricting to these keeps the corpus focused and reduces cost.

**Why v2 was rebuilt from scratch (not evolved from v1):**
v1's ReAct tool-calling loop had a fundamental budget problem — researchers exhausted calls before hitting all academic DBs. The sweep architecture fixes this programmatically: all DBs are always hit in parallel, no LLM budget to exhaust.

**Why critique sees executive summary, not raw notes:**
Raw notes across 5 researchers and 3 iterations can be 50K+ tokens. The executive summary condenses this into a tractable artifact. Critiquing the synthesis claim (not the raw data) is the right abstraction level.

**Why CCM is deferred until B7:**
CCM needs a real citation network. Training on 50 isolated paper nodes produces meaningless scores. The corpus (B2/B3), citation depth taxonomy (B4), chaser (B5), and Neo4j writer (B6) must all be complete first.

**Why CCM runs offline, not live during a research run:**
A8 does build a citation network (the Run Graph) during a run — so technically CCM could run on it. But offline CCM produces better scores for three reasons: (1) η is a field-relative measure — "how central is this paper relative to the whole field" requires the full 2,000+ node network, not the 100-300 nodes in one run's graph; "central to this run" is not the same signal. (2) Scores would be unstable across runs — slightly different papers found → different Run Graph → different η for the same paper. Pre-computed scores are stable. (3) Pre-2023 ancestors dominate the Run Graph but should never be permanently scored; the offline batch trains only on the corpus + their ancestry, keeping the score space well-defined. The right split: A8 uses lightweight graph metrics on the Run Graph (L3 in-degree, chain termination detection) for run-local analysis, and overlays pre-computed offline η scores from Neo4j to tell it which chains are in high-momentum territory worth prioritizing.

**Why no Neo4j writes during research runs:**
Writing to Neo4j mid-run creates a sync problem: Neo4j has papers that aren't in `_chase_network.json`, so CCM scores on those papers are stale or missing. The cleaner model is Neo4j is read-only during runs — papers found during a run go to `KG-src/ingested_papers/queue/` and enter the KG in the next weekly batch, fully scored.

**Why CITES edges are corpus-to-corpus only in Neo4j:**
Pre-2023 papers and non-corpus papers are never in Neo4j. If neo4j_writer created stub nodes for them, Neo4j would contain two classes of Paper node with fundamentally different completeness levels, blurring queries. The pre-2023 ancestry that CCM needs is captured in `_chase_network.json` — it never needs to live in Neo4j.

**Why the KG full rebuild is one-time only:**
The initial rebuild wipes the schema-mismatched data written by the old A5 incremental writer. After that, all writes use `MERGE` and `--skip-wipe`. A weekly wipe-rebuild would be wasteful and would destroy CCM scores set since the last ingest.

**Why gap surfacing uses the Run Graph, not Neo4j:**
Neo4j holds the curated intervention space (2023+ corpus). Gap surfacing requires tracing intellectual lineage through pre-2023 ancestors, which are never in Neo4j. The Run Graph, built live by A8 via S2, includes those ancestors. CCM scores from Neo4j corpus papers are overlaid on the Run Graph to weight which chains are most important — the two systems complement each other.

---

## Session Log

### Session 13 — KG Corpus Complete + UI Polish

All Track B KG corpus phases (B1–B8) completed. UI frontend overhauled.

**Track B completed:**
- B8 CCM training done (234 papers, 15 clusters, η/cluster_id/field_momentum/sb_coef in Neo4j)
- B9 weekly batch script (`KG-src/run_weekly_batch.py`) built

**UI changes (eduagent_frontend):**
- Removed Research/Strategic Canvas mode buttons and "beta" pill from Navbar
- Added Agent + About nav links with active-state underline
- Added Deep Research / Graph Traversal tab bar on agent page
- Graph Traversal tab: hides query box, keeps past sessions table visible
- QueryBar: removed task-type dropdown and bottom filters row; added Fast/Slow speed toggle
- JobsFeed: replaced card layout with clean table (Query | Model | Date | Status); running jobs show as compact banner above table
- Archived `research_assistant_agent/` (no pertinent v2 code)

---

### Session 14 — Frontend ↔ Backend Integration + Repo Cleanup

**Frontend ↔ Backend wiring:**
- Stream route (`app/api/research/stream/route.ts`) rewritten with full v2 config keys
- `SPEED_MODEL_MAP`: fast → `openai:gpt-5.4-mini-2026-03-17`, slow → `openai:gpt-5.4-2026-03-05`
- `REPORT_MODEL = "openai:gpt-5.4-2026-03-05"` always (even on fast runs)
- `research_iterations = 3` always (not speed-dependent)
- Full config matches `run_pipeline.py`: `max_concurrent_researchers=5`, `max_sweep_cycles=2`, `tavily_budget=8`, `serp_budget=2`, `max_sources=30`, `recursion_limit=200`
- `jobId` passed as `session_id` in config — enables background persistence
- `useResearch.ts`: updated `NODE_LABELS` to match v2 graph nodes; added `metadata` event handling for live node status
- Removed `useSessions` (Neo4j session fetching from old system) from agent page
- `useLocalRuns`: 30-second polling; completed disk runs override "running" localStorage entries
- `JobsFeed`: removed mode filter pills; kept status filter + search
- `QueryBar`: Fast/Slow tooltip added (Info icon with hover card)
- About page (`app/about/page.tsx`) — "Coming Soon"

**Backend changes:**
- `deep-research-src/configuration.py`: added `session_id` and `serp_budget` fields; `tavily_budget` default 10 → 8
- `deep-research-src/utils/output_saver.py` (NEW): saves `final_report_*.md`, `qa_report_*.md`, `state_snapshot_*.json` to `output/<session_id>/` when `session_id` is set
- `deep-research-src/nodes/qa.py`: calls `save_run_output` after QA completes (background persistence trigger)
- `deep-research-src/nodes/education_discovery.py`: `reset_budget(tavily_limit, serp_limit)` called at run start — enforces budgets for both frontend and CLI runs
- `run_pipeline.py`: removed manual `reset_budget()` call (now handled in education_discovery); added `openai:` prefix to model names
- PDF extractor rename: `pdf_extractor.py` → `pdf_extractor_report.py` (v1, runtime, for reports); `pdf_extractor_v2.py` → `pdf_extractor_kg.py` (v2, weekly batch, for Neo4j)

**Repo restructure:**
- `open_deep_research_v2/` → `eduagent_backend/`
- `edu_discovery_platform/` → `eduagent_frontend/`
- `src/` → `deep-research-src/`
- `scripts/` → `KG-src/`
- `citation-kg-testing/` merged into `KG-src/` (scripts moved, `ingested_papers/` moved)
- One-time scripts archived to `eduagent/archive/eduagent_testing/old_scripts/`: `ingest_papers.py`, `ingest_scale.py`, `seed_kg_nodes.py`, `PLAN.md`
- Run output path: `output/<session_id>/` — one subfolder per pipeline run (populated by `output_saver.py` when `session_id` is set)

---

### Session 15 — PDF Extractor Consolidation + Citation Connector Fixes + Frontend Downloads

#### Citation Connector bug fixes (`deep-research-src/nodes/citation_connector.py`)

**Root cause of missing architecture section in run `f2d6b4e6`:** `_analyze_run_graph` crashed with `AttributeError: 'NoneType' object has no attribute 'lower'` because `dict.get("title", "")` returns `None` when the key exists with an explicit `null` value — the S2 API returns `"title": null` on some papers.

Three fixes:
1. Added `import re` (used in `_write_architecture_section` for regex but was never imported — would crash on first successful Step 4)
2. `cited.get("title", "")` → `cited.get("title") or ""` (same fix for DOI field)
3. Wrapped `_analyze_run_graph` in try/except so Step 4 (architecture write) always runs even if gap analysis fails:
   ```python
   try:
       analysis = _analyze_run_graph(run_graph, kg_scores, top_papers)
   except Exception as e:
       run_logger.log(f"[citation_connector] Gap analysis failed: {e}", sid)
       analysis = {"anchors": [], "lineage": "", "lineage_chains": [], "gaps": [], "hypotheses": [], "high_eta": []}
   ```

#### PDF Extractor consolidation (researcher pipeline → `pdf_extractor_kg.py`)

Previously `nodes/researcher.py` used `pdf_extractor_report.py` (Call 1 only). Now it uses `pdf_extractor_kg.py` (Calls 1+2, skipping Call 3). `pdf_extractor_report.py` kept untouched for reference.

**`deep-research-src/state.py`:**
- Removed old taxonomy classes: `EmpiricalFindingExtract`, `InterventionAssignment`, `OutcomeAssignment`, `PaperTaxonomyExtract`
- Added `KGFinding` and `IdentifiedTool` dataclasses (moved from `pdf_extractor_kg.py`)
- Kept `INTERVENTION_OPTIONS`, `OUTCOME_OPTIONS`, `OUTCOME_CONFIDENCE_THRESHOLD` constants
- `PaperProfile` schema updated:
  - Removed: `interventions: list[InterventionAssignment]`, `outcome_assignments: list[OutcomeAssignment]`
  - Added: `identified_tools: list[IdentifiedTool]`, `verdict: str`

**`deep-research-src/utils/pdf_extractor_kg.py`:**
- `KGFinding` and `IdentifiedTool` class definitions **commented out** (kept for reference, import now from `state`)
- Added `extract_citations: bool = False` param to `enrich_tool_output_v2`, `extract_paper_profile_v2`, `_extract_profile_v2`
- Research pipeline calls with `extract_citations=False` → skips Call 3, runs only Calls 1+2 in parallel
- Weekly batch calls with `extract_citations=True` → all 3 calls (full KG extraction)

**`deep-research-src/nodes/researcher.py`:**
- Import switched from `pdf_extractor_report` to:
  ```python
  from utils.pdf_extractor_kg import enrich_tool_output_v2 as enrich_tool_output, PDF_EXTRACTABLE_TOOLS
  ```

**`deep-research-src/nodes/report.py`:**
- Stats block updated from `outcome_assignments` to `identified_tools[].findings[]` schema
- Field name changes: `outcome_category` (was `outcome`), `sample_size` (was `study_size`), added `tool_name` label

**`deep-research-src/utils/kg_writer.py`:**
- Replaced `interventions` loop with `identified_tools` loop (tool-first schema)
- Findings now from `tool.findings[]` using `KGFinding` fields (`outcome_category`, `sample_size`, `finding_type`)
- Removed `std_deviation`; added `finding_type` field

**`deep-research-src/utils/kg_retriever.py`:**
- `_row_to_paper` returns `identified_tools` format (with `findings` nested under each tool)

#### Frontend fixes (`eduagent_frontend/`)

**Report shown before QA complete (`hooks/useResearch.ts`):**
- `status: "complete"` moved from step 8 (final_report event) to step 9 (qa_report event)
- Fallback added: if stream ends with report present but no QA, marks complete anyway

**Download API — NEW (`app/api/download/[id]/route.ts`):**
- Serves disk files from `output/<session_id>/`: `final_report_*.md`, `qa_report_*.md`, `run.log`, `state_snapshot_*.json`
- Searches both `output/` and `output/final-test/` directories
- Query param `?file=report|qa|log|snapshot`

**DownloadsPanel (`app/agent/[id]/page.tsx`):**
- `isLocalRun` detection via UUID regex `/^[0-9a-f-]{36}$/`
- Local runs use `downloadFromDisk()` → `/api/download/${job.id}?file=...`
- Non-local (API-backed) sessions fall back to in-memory data
