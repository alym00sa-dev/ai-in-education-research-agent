# Knowledge Graph Pipeline

The KG corpus pipeline ingests research papers into Neo4j and maintains the structured knowledge graph that powers Graph Traversal mode. It runs offline and is entirely separate from the user-facing request path.

---

## Graph Structure

The KG has exactly 4 node types:

```
Paper ──EVALUATES──> Intervention ──PRODUCES_FINDING──> EmpiricalFinding ──TARGETS_OUTCOME──> Outcome
  |                                                            ^
  └──REPORTS_FINDING (direct, failsafe) ──────────────────────┘
  └──FOCUSES_ON_OUTCOME (direct, failsafe) ──────────────────────────────────────────────────> Outcome
  └──CITES──> Paper (corpus-to-corpus only)
```

### Paper
One node per research paper. Merge key: DOI (preferred) or title. Key properties: `title`, `doi`, `year`, `venue`, `url`, `source_db`, `populations` (array), `study_design`, `extended_summary`, `quality_tier`, `impact_tier`, `limitations` (array), `setting`, `study_country`, `study_region`, CCM scores (`eta`, `cluster_id`, `field_momentum`, `sb_coef`).

Red-tier papers and `framework_only` verdicts are **skipped** — not written to Neo4j.

### Intervention
Pre-seeded stable taxonomy — 11 fixed nodes, never created dynamically by the pipeline. Covers the full spectrum from AI-powered (ITS, LLM tutors, adaptive platforms, automated feedback, AI writing tools, robots, predictive analytics) to technology-enabled (CAI, educational games, mobile apps, Other). Key property: `is_ai_powered` boolean.

### EmpiricalFinding
One node per measured outcome from a paper. Properties: `finding_id` (deterministic sha256 hash), `direction` (Positive/Negative/No Effect/Mixed), `finding_summary`, `measure`, `effect_size`, `sample_size`, `outcome_category`.

### Outcome
Pre-seeded — 9 fixed categories. Created on MERGE if not already present; stale Outcome nodes with no `TARGETS_OUTCOME` edges are deleted at the end of each write run.

Values: Academic — Literacy, Academic — Language Fluency, Academic — Mathematical Numeracy, Academic — Scientific Reasoning, Academic — Other, Social-Emotional Skills, Durable Skills, Operational Efficiency, Systemic / Institutional Impact.

---

## Data Sources

The writer reads from three pre-existing sources — it does not fetch or scrape anything:

| Source | Location | Contains |
|---|---|---|
| Paper JSONs | `KG-src/ingested_papers/2026-04-01/`, `scale_2026-04-01/`, `legacy/` | Paper node data (title, DOI, metadata, extended_summary, quality tier) |
| Tools final | `KG-src/tools_final/*.json` | Intervention nodes + EVALUATES edges + EmpiricalFinding nodes |
| Chase network | `KG-src/ingested_papers/merged/_chase_network.json` | CITES edges (corpus-to-corpus only) |

---

## Running the Pipeline

### Full rebuild (wipe + write)

```bash
cd eduagent_backend
python KG-src/neo4j_writer.py
```

This wipes the entire graph (`MATCH (n) DETACH DELETE n`) then writes all nodes fresh. It's idempotent — re-running produces the same graph.

### Upsert only (no wipe)

```bash
python KG-src/neo4j_writer.py --skip-wipe
```

Merges into the existing graph. Safe for adding new papers without losing other data.

### Dry run (no Neo4j changes)

```bash
python KG-src/neo4j_writer.py --dry-run
```

Prints what would be written without touching the database.

### Custom corpus directories

```bash
python KG-src/neo4j_writer.py \
    --papers-dirs KG-src/ingested_papers/2026-04-01 KG-src/ingested_papers/scale_2026-04-01 \
    --chase-network KG-src/ingested_papers/merged/_chase_network.json
```

---

## Adding New Papers

Papers are written from JSON files in `KG-src/ingested_papers/`. A new paper JSON needs these fields at minimum:

```json
{
  "title": "Paper title",
  "doi": "10.xxxx/xxxxx",
  "year": 2024,
  "url": "https://...",
  "source_db": "openalex",
  "populations": ["Undergraduate"],
  "study_design": "RCT",
  "extended_summary": "2-3 paragraph narrative...",
  "quality_tier": "green",
  "impact_tier": "green",
  "verdict": ""
}
```

Files starting with `_` are ignored (used for metadata files like `_chase_network.json`). Deduplication is by DOI first, then by title prefix (first 80 chars). Papers with `verdict = "framework_only"` or `quality_tier = "red"` are skipped.

After adding JSONs, run `neo4j_writer.py --skip-wipe` to merge them in without wiping existing data.

---

## Citation Chasing

The `citation_chaser.py` script builds the `_chase_network.json` from the corpus. Run it before a full rebuild if you have new papers:

```bash
python KG-src/citation_chaser.py
```

This traverses citations 1.5 hops deep (L1: directly cited, L2: cited by L1, L1.5: co-cited by multiple papers) and outputs the chase network to `KG-src/ingested_papers/merged/_chase_network.json`.

CITES edges are only written when **both** source and target are corpus Paper nodes in Neo4j. Non-corpus references are skipped — no stub nodes are created.

---

## CCM Scoring

`ccm_trainer.py` computes bibliometric scores and writes them back to Paper nodes:

- `eta` — citation fitness (PageRank proxy on the CITES graph)
- `cluster_id` — topical community (K-means on fastRP embeddings, k=15)
- `field_momentum` — fraction of cluster's in-edges from 2024+ papers (is this subfield growing?)
- `sb_coef` / `is_sleeping_beauty` — late-recognition pattern (Ke et al. 2015)

```bash
python KG-src/ccm_trainer.py
```

Run after `neo4j_writer.py`. Scores are read by the Citation Connector Agent during research runs to surface high-influence gaps and momentum gaps.

---

## Checking the Graph

Open Neo4j Browser at `http://localhost:7474` (local) or the Aura Console.

Useful queries:

```cypher
-- Count all nodes by type
MATCH (n) RETURN labels(n)[0] AS type, count(n) AS count ORDER BY count DESC;

-- Papers per intervention
MATCH (p:Paper)-[:EVALUATES]->(i:Intervention)
RETURN i.name, count(p) AS paper_count ORDER BY paper_count DESC;

-- Papers with findings targeting a specific outcome
MATCH (p:Paper)-[:REPORTS_FINDING]->(f:EmpiricalFinding)-[:TARGETS_OUTCOME]->(o:Outcome)
WHERE o.name CONTAINS 'Literacy'
RETURN p.title, f.direction, f.finding_summary LIMIT 20;

-- Check for duplicate findings (should be 0)
MATCH (f:EmpiricalFinding)
WITH f.finding_id AS id, count(f) AS cnt WHERE cnt > 1
RETURN id, cnt;
```

---

## Troubleshooting

**Duplicate EmpiricalFinding nodes after re-run:**
`finding_id` must use `hashlib.sha256`, not Python's built-in `hash()`. Python 3.3+ uses a random seed per process, so `hash()` is non-deterministic across runs. Check `neo4j_writer.py` line where `finding_id` is computed.

**Neo4j connection refused:**
Confirm `.env` has the correct `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`. For Aura, use `neo4j+s://` not `bolt://`.

**Graph traversal returns 0 results:**
Run the Cypher query directly in Neo4j Browser to debug. Common mistake: the LLM adds a `populations` filter for K-12 when the question only mentions K-12 as context (e.g. "ChatGPT in K-12") — the corpus labels these papers as Undergraduate/Adult.

**tools_final not found:**
The writer looks for `KG-src/tools_final/`. If missing, it falls back to the archive path. Copy the tools_final directory into `KG-src/` if running outside the archive context.
