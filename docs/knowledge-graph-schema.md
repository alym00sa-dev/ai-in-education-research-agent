# AI in Education Knowledge Graph — Schema

---

## Nodes

### Paper

| Property                  | Type         | Notes                                                              |
|---------------------------|--------------|--------------------------------------------------------------------|
| paper_id                  | string       | DOI when available, otherwise hash of title + year                 |
| title                     | string       |                                                                    |
| doi                       | string       |                                                                    |
| year                      | int          |                                                                    |
| venue                     | string       |                                                                    |
| url                       | string       |                                                                    |
| source_db                 | string       | e.g. openalex, eric, arxiv, crossref, semantic_scholar             |
| population                | string       | e.g. Elementary, Undergraduate                                     |
| user_type                 | string       | Student, Educator, Administrator, Parent, School, Community        |
| study_design              | string       | RCT, Meta-Analysis, Quasi-Experimental, etc.                       |
| extended_summary          | string       | 2–3 paragraph narrative                                            |
| quality_tier              | string       | blue / green / yellow / red (K-12 Evidence Framework)              |
| impact_tier               | string       | blue / green / yellow / red                                        |
| extraction_status         | string       | full_text or legacy                                                |
| session_id                | string       | which pipeline run wrote it                                        |
| added_date                | ISO datetime |                                                                    |
| limitations               | string[]     | controlled vocab array — see Limitations Vocabulary below          |
| duration_weeks            | string       | int or "not_reported"                                              |
| setting                   | string       | classroom / lab / online / blended / not_reported                  |
| teacher_training          | string       | yes / no / not_reported                                            |
| implementation_fidelity   | string       | high / medium / low / not_reported             on                    |
| study_country             | string       | country where study was conducted                                  |
| study_region              | string       | UN geoscheme region — see Geographic Vocabulary below              |
| eta                       | float        | CCM fitness score — PageRank proxy for citation influence          |
| cluster_id                | int          | K-means cluster assignment from fastRP embedding (k=15)            |
| field_momentum            | float        | fraction of in-edges from 2024+ papers in this paper's cluster    |
| sb_coef                   | float        | Ke et al. (2015) sleeping beauty coefficient                       |
| is_sleeping_beauty        | boolean      | true if sb_coef ≥ 1.0 (late-recognition pattern)                  |
| ccm_run_date              | ISO datetime | date CCM trainer last computed scores for this paper               |

---

### Intervention

Pre-seeded stable taxonomy — never created by the pipeline, only mapped to. Covers the full spectrum from AI-powered to technology-enabled interventions.

| Property        | Type    | Notes                                               |
|-----------------|---------|-----------------------------------------------------|
| intervention_id | string  | slugified tag, e.g. "intelligent_tutoring_system"   |
| name            | string  | canonical label                                     |
| description     | string  | short definition for coding consistency             |
| is_ai_powered   | boolean | true = AI-powered; false = technology-enabled only  |

**Seed list:**

| Name | is_ai_powered | Description |
|---|---|---|
| Intelligent Tutoring System (ITS) | true | Classical rule/model-based systems that adapt instruction through student modelling (e.g. ASSISTments, Cognitive Tutor) |
| LLM-based Tutoring / Conversational AI | true | Modern GenAI tutors, chatbots, AI course assistants (post-2022) |
| Adaptive Learning Platform | true | Systems that personalise content sequencing and pacing without dialogue-based tutoring |
| Automated Feedback System | true | AI that evaluates and comments on student work (essays, code, math) without acting as a tutor |
| AI Writing / Language Tool | true | Specifically targets writing production and language fluency — EFL assistants, grammar AI, speech tools |
| Robot / Embodied Tutor | true | Physical or avatar-based robotic tutoring systems |
| Predictive Analytics / Early Warning | true | AI that analyses student behaviour/performance data to flag risk and trigger intervention |
| Computer-Assisted Instruction (CAI) | false | Software-delivered instruction, minimally adaptive or non-adaptive — captures pre-AI evidence base |
| Educational Game / Simulation | false | Game-based learning and simulations with a technology component |
| Mobile / Microlearning App | false | App-based, bite-sized delivery |
| Other | false | Catch-all — flagged for periodic review; if 5+ papers accumulate, consider new node |

---

### EmpiricalFinding

Optional for papers with `study_design = Framework / Theoretical`. Required for all empirical and review papers.

| Property            | Type   | Notes                                      |
|---------------------|--------|--------------------------------------------|
| finding_id          | string | hash of title + outcome                    |
| direction           | string | Positive / Negative / No Effect / Mixed    |
| finding_summary     | string | 2–3 sentence narrative with effect sizes   |
| measure             | string | what was measured                          |
| study_size          | string | e.g. n=312                                 |
| effect_size         | string | e.g. d=0.42                                |
| confidence_interval | string |                                            |
| std_deviation       | string |                                            |

---

### Outcome

Pre-seeded. 9 fixed categories.

| Property   | Type   | Notes                          |
|------------|--------|--------------------------------|
| outcome_id | string | slugified name                 |
| name       | string | one of 9 fixed outcome categories |

**Values:**
- Academic — Literacy (reading and writing)
- Academic — Language Fluency (speaking and listening)
- Academic — Mathematical Numeracy
- Academic — Scientific Reasoning
- Academic — Other
- Social-Emotional Skills (motivation, engagement, self-regulation, persistence)
- Durable Skills (critical thinking, metacognition, collaboration, time management)
- Operational Efficiency (productivity, task efficiency, teacher workload)
- Systemic / Institutional Impact

---

## Relationships

### The Chain: Paper → Intervention → EmpiricalFinding → Outcome

| Relationship     | From             | To               | Properties                                        | Notes                                                          |
|------------------|------------------|------------------|---------------------------------------------------|----------------------------------------------------------------|
| EVALUATES        | Paper            | Intervention     | role (primary/secondary), confidence, use_case    | use_case is free-text: HOW this paper applies the intervention |
| PRODUCES_FINDING | Intervention     | EmpiricalFinding |                                                   | routes to assignment-specific intervention for comparison papers; falls back to primary |
| TARGETS_OUTCOME  | EmpiricalFinding | Outcome          |                                                   | what outcome area the finding measures                         |

### Failsafe Direct Links from Paper

| Relationship       | From  | To               | Properties | Notes                      |
|--------------------|-------|------------------|------------|----------------------------|
| REPORTS_FINDING    | Paper | EmpiricalFinding |            | direct paper→finding link  |
| FOCUSES_ON_OUTCOME | Paper | Outcome          | confidence | direct paper→outcome link  |

### Notes on finding_id uniqueness

`finding_id` is a hash of `title + outcome + intervention + index`. Including `intervention` and `index` prevents collisions in comparison papers where the same paper reports findings for the same outcome from two different interventions (e.g. ITS d=0.42 vs LLM d=0.18 for math).

### Cross-Paper

| Relationship | From  | To    | Properties | Notes            |
|--------------|-------|-------|------------|------------------|
| CITES        | Paper | Paper | citation_level, citation_context | Corpus-to-corpus only — both source and target must be Paper nodes in Neo4j (OPTIONAL MATCH; no stub nodes created for non-corpus papers) |

#### CITES Properties

| Property        | Type   | Notes                                                                                   |
|-----------------|--------|-----------------------------------------------------------------------------------------|
| citation_level  | string | L1 = referential (passing mention); L2 = grounded (key theory/methodology); L3 = foundational (direct extension/replication) |
| citation_context| string | Verbatim or paraphrased sentence explaining how source cites target                     |

#### Typing Rules
- **L1** — cited in passing; provides background or context only
- **L2** — cited as key theoretical, philosophical, or methodological grounding in the lit review
- **L3** — directly extended: replication, same methodology, direct iteration of the cited work

> **Implementation note:** CITES edges are written only when BOTH the citing paper (`s`) and the cited paper (`t`) are already corpus Paper nodes in Neo4j. Non-corpus references (pre-2023, off-topic, or otherwise not ingested) are silently skipped — no stubs are created.

---

## Controlled Vocabularies

### Limitations

Used as a string array on `Paper.limitations`. Tag any that apply:

- `small_sample` — fewer than ~100 participants
- `short_duration` — intervention lasted less than 4 weeks
- `single_site` — conducted at one school or institution only
- `no_control_group` — no comparison condition
- `self_reported_measures` — outcomes rely on self-report rather than objective assessment
- `non_representative_population` — sample unlikely to generalise (highly selective, single demographic)
- `high_attrition` — significant dropout affecting validity
- `implementation_fidelity_not_reported` — no information on how the intervention was delivered
- `no_long_term_followup` — outcomes measured immediately, no delayed retention data

### Study Region (UN Geoscheme)

Used in `Paper.study_region`:

- North America
- Latin America & Caribbean
- Europe
- Sub-Saharan Africa
- East Asia & Pacific
- South Asia
- Middle East & North Africa
- Central Asia
- not_reported

---

---

## Community Citation Model (CCM)

CCM scores are computed offline (weekly batch) by `citation-kg-testing/ccm_trainer.py` and written back to Paper nodes in Neo4j. Based on Kojaku et al. (2025) — *Community Citation Model*, arXiv:2501.15552.

### What each score means

| Property | Source | Interpretation |
|---|---|---|
| `eta` | Weighted PageRank on the CITES graph | Citation fitness — how influential a paper is as a citation target within the corpus |
| `cluster_id` | K-means (k=15) on fastRP out-embeddings (K=128) | Topical community — papers that cite similar work land in the same cluster |
| `field_momentum` | Fraction of a cluster's in-edges from 2024+ papers | How actively the cluster is being cited by recent work — proxy for whether the subfield is growing |
| `sb_coef` | Ke et al. (2015) sleeping beauty formula | Late-recognition score — high values = paper was ignored then suddenly cited heavily |
| `is_sleeping_beauty` | `sb_coef ≥ 1.0` | Boolean flag for papers showing a sleeping beauty awakening pattern |

### Implementation details

- **Embeddings**: fastRP algorithm from the CCM paper authors' own repo (`community_citation_model`). `edge_direction=True` → separate out-embedding (what a paper cites = topical territory) used for clustering.
- **Fitness (η)**: Full NCE training requires per-citation timestamps unavailable in this corpus; PageRank on the CITES graph is the faithful proxy.
- **Sleeping beauty**: Formula from Ke et al. (2015), ported from Kojaku et al.'s `utils.py`. Most sleeping beauties in the current corpus are pre-1900 foundational works; 2023–2026 corpus papers typically score near 0.
- **Scope**: Only papers present as Paper nodes in Neo4j receive scores (234/244 in first run; 10 excluded for red quality / framework_only designation).
- **Run artifacts**: Each CCM run saves `_ccm_scores.json` and `_ccm_embeddings.json` locally in `citation-kg-testing/` in addition to writing to Neo4j.

### How the Citation Connector Agent uses CCM

The Citation Connector Agent (`src/nodes/citation_connector.py`) reads CCM scores from Neo4j at the start of each research run and surfaces hypotheses when:
- A paper has high `eta` (≥ 0.50) but is underexplored in the run's source pool → *high-influence gap*
- A cluster has high `field_momentum` but no RCT-level evidence → *momentum gap* (active subfield lacking rigorous studies)
- A paper has `is_sleeping_beauty = true` → flags potential rediscovery pattern

---

## Open Decisions (Resolved)

| Decision | Resolution |
|---|---|
| AIMethod node management | Option C — renamed to `Intervention`, pre-seeded stable taxonomy, mapped via LLM same as Outcome; controlled growth via `Other` catch-all |
| Intervention assignment | `InterventionAssignment` model with `intervention`, `confidence` (≥0.5 threshold), `role` (primary/secondary), `use_case` (free-text HOW) |
| Intervention use_case tagging | Free-text only — no separate tag field. Use_case enables gap detection queries; can be vector-clustered later. No redundant tag. |
| Limitations tracking | Option B — structured array on Paper with controlled vocabulary |
| Implementation context | Option C — structured properties on Paper (`duration_weeks`, `setting`, `teacher_training`, `implementation_fidelity`) |
| Geographic context | Option B — `study_country` + `study_region` (UN geoscheme) as properties on Paper |
| Non-empirical papers | `study_design = Framework / Theoretical` signals no findings required — no separate paper_type needed |
| AI vs non-AI methods | `is_ai_powered` boolean on `Intervention` node — enables AI-only filtering without losing non-AI tech papers |
| Comparison paper findings | `OutcomeAssignment.intervention` (Optional) — specifies which intervention produced which finding. `finding_id` hashes title+outcome+intervention+index to guarantee uniqueness. |
