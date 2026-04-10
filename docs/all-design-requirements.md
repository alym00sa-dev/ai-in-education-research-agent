# EduAgent — Design Requirements

**Version:** 1.0  
**Date:** April 2026

> For the actionable infrastructure checklist, see `MVP-infrastructure-requirements.md`.  
> For system diagrams, see `architecture-diagrams.md`.

---

## Overview

EduAgent is an internal AI research tool with three subsystems:

1. **Deep Research** — takes a natural language research question and produces a structured, cited evidence report by searching academic databases, extracting PDFs, and synthesizing findings with LLMs
2. **Graph Traversal** — a conversational interface over a curated Neo4j knowledge graph of AI-in-education research
3. **Weekly KG Batch** — an automated pipeline that processes papers discovered during research runs and updates the knowledge graph

---

## General Requirements

These apply across all three subsystems.

### Functional

| ID | Requirement | Why |
|----|-------------|-----|
| G-01 | All services shall run as Docker containers | Portability across Render, Nomad, or any container platform |
| G-02 | All API keys and secrets shall be injected via environment variables from a secrets manager — never hardcoded | Security; prevents credential exposure in source control |
| G-03 | The system shall support internal-only network access — no public internet exposure required for backend, Postgres, or Redis | Internal tool; reduces attack surface |
| G-04 | Authentication is not yet implemented — access control policy is an open item for IT | See Open Items |

### Non-Functional

| ID | Requirement | Why |
|----|-------------|-----|
| G-05 | Backend service uptime shall be 99%+ during business hours | Research runs are long — a crash mid-run loses 20+ minutes of work |
| G-06 | All services shall emit structured logs for key events and errors | Observability; needed for debugging production issues |
| G-07 | Secrets shall never appear in logs or error messages | Security |

---

## 1. Deep Research

A user submits a research question. The backend spawns a multi-step LangGraph pipeline: it searches academic databases in parallel, extracts PDF full text, synthesizes findings into a cited markdown report, and runs a QA audit. The full run takes 20–35 minutes. Progress is streamed live to the browser via SSE.

### Functional

| ID | Requirement | Why |
|----|-------------|-----|
| DR-01 | The system shall accept a natural language research query and optional keyword hints | Core input to the pipeline |
| DR-02 | The pipeline shall search concurrently across: Semantic Scholar, OpenAlex, ERIC, arXiv, Elsevier/Scopus, Google Scholar (SerpAPI), and Tavily web search | Broad coverage across academic and web sources |
| DR-03 | The pipeline shall extract full-text content from PDF sources where available | Full text yields higher quality synthesis than abstracts alone |
| DR-04 | The pipeline shall synthesize retrieved evidence into a structured, cited markdown report | Primary deliverable |
| DR-05 | The pipeline shall run a QA audit on the generated report before delivery | Catches hallucinations and citation errors |
| DR-06 | The pipeline shall stream real-time progress logs to the browser via SSE throughout execution | Users need visibility into a 20–35 min process |
| DR-07 | The system shall support multiple concurrent research runs simultaneously | Multiple team members may run queries at the same time |
| DR-08 | Completed run artifacts (report, QA report, run log) shall be persisted and retrievable across sessions and devices | Runs are expensive — results must not be lost |
| DR-09 | Each run shall write extracted paper profiles to a durable ingest queue (Postgres `kg_queue` table) for downstream KG processing | Papers discovered during research feed the weekly KG update |

### Non-Functional

| ID | Requirement | Why |
|----|-------------|-----|
| DR-10 | A typical run shall complete within 20–35 minutes under normal load | Sets expectation for infrastructure timeouts and user experience |
| DR-11 | The system shall support a minimum of 3 concurrent runs without degradation | Each run uses 5 parallel researcher threads — 3 runs = 15 concurrent threads |
| DR-12 | SSE progress events shall reach the browser within 2 seconds of emission | Stale logs make it hard to know if the run is still alive |
| DR-13 | The SSE stream connects directly from the browser to the backend — any proxy or load balancer in front of the backend **must not buffer or timeout long-lived HTTP connections** | Proxies that buffer responses will hold the entire stream until the run completes, which breaks live streaming |
| DR-14 | LangGraph run state (checkpoints) shall be persisted to Postgres | Allows interrupted runs to be inspected; required by LangGraph runtime |
| DR-15 | Run artifacts shall be retrievable for a minimum of 90 days | Retention policy not yet enforced — see Open Items |
| DR-16 | The LangGraph worker concurrency limit shall be configurable via `LANGGRAPH_MAX_CONCURRENCY` | Allows tuning for available compute without code changes |

### Infrastructure Needed

| Component | Requirement |
|---|---|
| Backend compute | 4 vCPUs / 16 GB RAM recommended for 3 concurrent runs |
| Postgres | LangGraph checkpointing + `kg_queue` table |
| Redis (backend) | LangGraph SSE pub/sub — required for real-time event routing |
| Redis (frontend) | Run metadata and report storage, accessible cross-device |
| Long-lived HTTP | Proxy/LB must allow connections open 20–35 min without buffering |

---

## 2. Graph Traversal

A user asks a natural language question about the knowledge graph. The backend translates it into Cypher queries, executes them against Neo4j, and synthesizes a conversational response. Multi-turn conversation history is maintained within a session.

### Functional

| ID | Requirement | Why |
|----|-------------|-----|
| GT-01 | The system shall provide a conversational interface for querying the knowledge graph | Core use case for Graph Traversal mode |
| GT-02 | The pipeline shall retrieve the current intervention taxonomy from Neo4j at query time before generating Cypher | Grounds LLM query generation in what actually exists in the graph; prevents queries that match nothing |
| GT-03 | The pipeline shall generate three Cypher query variants per question: specific (exact names), medium (broader patterns), and broad (full-text search on `extended_summary`) | Single queries often return no results; cascading from specific → broad maximises recall |
| GT-04 | Results from all three queries shall be deduplicated and merged before synthesis | Prevents duplicate papers appearing in the response |
| GT-05 | The pipeline shall maintain multi-turn conversation history within a session | Users ask follow-up questions that reference prior answers |
| GT-06 | Conversation sessions shall be persisted and retrievable across page loads | Users return to prior conversations |

### Non-Functional

| ID | Requirement | Why |
|----|-------------|-----|
| GT-07 | A synthesized response shall be returned within a reasonable time | Conversational interface — longer waits break the interaction pattern |
| GT-08 | Neo4j must be readable at runtime from the backend service | Every Graph Traversal query hits Neo4j — read access is required at all times |
| GT-09 | The intervention taxonomy cache shall refresh at most once per hour | Avoids a Neo4j round-trip on every single query while staying reasonably current |

### Infrastructure Needed

| Component | Requirement |
|---|---|
| Neo4j | Read access required at runtime (Bolt port 7687) |
| Redis (frontend) | Graph session history storage |

---

## 3. Weekly KG Batch

At the end of each Deep Research run, extracted paper profiles are written to a queue (`kg_queue` in Postgres). Once a week, a batch job processes the queue: re-extracts papers with full LLM extraction, chases citations through Semantic Scholar, retrains graph analytics (CCM), and writes updated nodes and relationships to Neo4j.

### Functional

| ID | Requirement | Why |
|----|-------------|-----|
| KB-01 | The batch pipeline shall run on a weekly automated schedule | Manual runs are error-prone and easy to forget |
| KB-02 | The pipeline shall read queued papers from `kg_queue` (Postgres) where `status = 'queued'` | Postgres queue is durable across container restarts; replaces old file-based queue |
| KB-03 | The pipeline shall re-extract each paper using a 3-call LLM process: metadata, tool taxonomy, and citations | Full structured extraction is needed for Neo4j node creation |
| KB-04 | The pipeline shall traverse Semantic Scholar's citation graph for new related papers (L1/L2/L3 edges) | Expands the corpus beyond what research runs directly find |
| KB-05 | The pipeline shall retrain CCM graph analytics: fastRP embeddings (K=128), K-means clusters (k=15), PageRank fitness scores, and sleeping beauty coefficients | Keeps relevance scoring and clustering current as the corpus grows |
| KB-06 | The pipeline shall write Paper, Intervention, EmpiricalFinding, and Outcome nodes to Neo4j in upsert-only mode — no destructive writes | Safe incremental updates; cannot corrupt existing graph data |
| KB-07 | The pipeline shall update processed queue entries to `status = 'done'` with timestamp and batch date | Provides an audit trail; replaces old archive-to-disk approach |
| KB-08 | Individual paper failures shall not abort the full batch — errors are logged and the entry is marked `status = 'failed'` | One bad PDF should not block 200 other papers |
| KB-09 | The pipeline shall support `--dry-run` mode that logs actions without executing writes | Safe testing and validation before production runs |

### Non-Functional

| ID | Requirement | Why |
|----|-------------|-----|
| KB-10 | The batch job shall complete within a 4-hour maintenance window | Sets expectation for scheduling and monitoring |
| KB-11 | The batch job shall not run overlapping instances | Two concurrent batches would duplicate Neo4j writes and corrupt CCM retraining |
| KB-12 | The `kg_queue` table shall be in the same Postgres instance used by LangGraph | Both the research pipeline (writer) and the batch job (reader) must reach the same database |
| KB-13 | Neo4j write access is required only during the weekly batch — the backend has read-only access at all other times | Principle of least privilege; reduces risk of accidental writes during research runs |

### Infrastructure Needed

| Component | Requirement |
|---|---|
| Periodic job runner | Cron `0 6 * * 1` — must support `prohibit_overlap` |
| Postgres | Read/write access to `kg_queue` table |
| Neo4j | Read/write access during batch window |
| Semantic Scholar API | Citation graph traversal |
| LLM access (OpenAI) | 3-call extraction per paper; configurable via `WEEKLY_BATCH_MODEL` |

---

## 4. External API Dependencies

| Service | Used By | Notes |
|---|---|---|
| OpenAI / GPT-5.4 | Deep Research, Graph Traversal, Weekly Batch | Primary LLM — highest cost driver |
| Anthropic / Claude | Deep Research (QA audit) | Secondary LLM |
| Semantic Scholar | Deep Research (search), Weekly Batch (citations) | Free tier has rate limits |
| OpenAlex | Deep Research | No key required; low rate limit risk |
| ERIC | Deep Research | Education-specific database |
| arXiv | Deep Research | Preprint search |
| Elsevier / Scopus | Deep Research | Requires institutional API key — Gates Foundation has one |
| SerpAPI | Deep Research (Google Scholar) | Paid API key required |
| Asta | Deep Research (paper enrichment) | Separate API key (`ASTA_TOOL_KEY`) |
| Tavily | Deep Research (web search fallback) | Paid API key required |

---

## 5. Open Items for IT

| Item | Detail |
|---|---|
| **Neo4j migration** | Currently on a personal AuraDB instance — must move to Gates Enterprise Neo4j |
| **Secret management** | Currently plain env vars on Render |
| **Redis KV (frontend)** | Currently Vercel-proprietary KV — must be replaced |
| **`kg_queue` Postgres migration** | Queue is currently file-based on local disk (not durable) — Postgres migration designed and documented in `kg-queue-postgres-migration.md`, not yet implemented |
| **Periodic job runner** | Weekly batch has no automated trigger — needs Nomad periodic job or equivalent cron setup |
