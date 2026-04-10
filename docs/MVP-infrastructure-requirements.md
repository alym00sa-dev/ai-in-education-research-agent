# EduAgent — Infrastructure Requirements

**Prepared for:** IT Infrastructure Team  
**Date:** April 2026

This document lists what is strictly required to deploy and run EduAgent. For full system context and architecture, see `all-design-requirements.md` and `architecture-diagrams.md`.

---

## 1. Services Required

| Service | Purpose |
|---|---|
| **Python backend** (LangGraph) | Runs Deep Research and Graph Traversal pipelines |
| **Next.js frontend** | User interface |
| **Postgres 14+** | LangGraph run checkpointing + paper ingest queue |
| **Redis 6+** (backend) | LangGraph SSE pub/sub — required for real-time streaming |
| **Redis 6+** (frontend) | Run history and graph session storage |
| **Neo4j 5+** | AI-in-education knowledge graph (read at runtime, written weekly) |
| **Scheduled/periodic job** | Weekly KG batch pipeline (Any day, ~2–4 hours) |

---

## 2. Compute Requirements

### Backend (Python / LangGraph)
| Resource | Minimum | Recommended |
|---|---|---|
| CPU | 2 vCPUs | 4 vCPUs |
| Memory | 4 GB | 16 GB |
| Runtime | Python 3.11, Docker | |

> Each Deep Research run launches 5 parallel researcher threads making concurrent external API calls. Memory scales with number of concurrent runs.

### Frontend (Next.js)
| Resource | Minimum |
|---|---|
| CPU | 1 vCPU |
| Memory | 1 GB |
| Runtime | Node.js 18+, Docker |

### Weekly Batch Job
| Resource | Notes |
|---|---|
| CPU / Memory | Same container image as backend |
| Trigger | Cron: `0 6 * * 1` (Monday 06:00 UTC) |
| Overlap | Must not run concurrently with itself (`prohibit_overlap = true`) |
| Runtime | 2–4 hours depending on queue depth |

---

## 3. Networking Requirements

| Connection | Protocol | Notes |
|---|---|---|
| Browser → Frontend | HTTPS | Standard |
| Frontend → Backend (thread init) | HTTPS POST | Short-lived (< 2s) |
| Browser → Backend (SSE stream) | HTTPS, long-lived | **Must not be buffered by proxies** — connections held open 20–35 min |
| Backend → Postgres | TCP 5432 | |
| Backend → Redis | TCP 6379 | |
| Backend → Neo4j | Bolt 7687 or HTTPS | |
| Backend → external APIs | HTTPS outbound | Semantic Scholar, OpenAlex, OpenAI, Anthropic, etc. |

> **Critical:** Any load balancer or proxy in front of the backend must support long-lived HTTP connections without buffering or timeout for SSE to work correctly.

---

## 4. Environment Variables Required

### Backend
| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Postgres connection string |
| `REDIS_URL` | Redis connection string |
| `NEO4J_URI` | Neo4j bolt URI |
| `NEO4J_USER` | Neo4j username (defaults to `"neo4j"`) |
| `NEO4J_PASSWORD` | Neo4j password |
| `NEO4J_DATABASE` | Neo4j database name (defaults to `"neo4j"` — may differ on Gates Enterprise instance) |
| `OPENAI_API_KEY` | GPT-5.4 for research + report generation |
| `ANTHROPIC_API_KEY` | Claude for QA audit |
| `SEMANTIC_SCHOLAR_API_KEY` | Academic search + citation graph traversal |
| `ELSEVIER_API_KEY` | Scopus academic search (institutional license — we have one) |
| `SERPAPI_API_KEY` | Google Scholar search via SerpAPI |
| `ASTA_TOOL_KEY` | Asta paper enrichment tool |
| `TAVILY_API_KEY` | Web search fallback |
| `LANGGRAPH_CORS_ALLOW_ORIGINS` | Frontend domain — required for browser SSE connection |
| `LANGGRAPH_MAX_CONCURRENCY` | Max simultaneous pipeline runs (recommended: 3–5) |
| `WEEKLY_BATCH_MODEL` | LLM model for weekly extraction (default: GPT-5.4 Mini) |

### Frontend
| Variable | Purpose |
|---|---|
| `NEXT_PUBLIC_RENDER_API_URL` | Backend URL — **public, browser-visible** — used for direct SSE stream |
| `RENDER_API_URL` | Backend URL — server-side only — used for thread init proxy call |
| `REDIS_URL` (or equivalent KV vars) | Run history + graph session storage |

---

## 5. Storage Requirements

| Store | Estimated Size | Growth |
|---|---|---|
| Postgres | 20 GB initial | ~2 GB/month |
| Neo4j | ~500 MB current corpus | ~50 MB/week |
| Redis (backend) | Low — in-memory event routing only | Minimal |
| Redis (frontend) | Low — run metadata + session history | ~100 MB/month |

---

## 6. Open Items Needing IT Input

| Item | Notes |
|---|---|
| **Neo4j** | Currently on a personal AuraDB instance — needs to move to Gates Enterprise Neo4j |
| **Auth / SSO** | No authentication layer exists yet — internal access control policy needed |
| **Secret management** | Needs a more secure option — currently plain env vars |
| **Redis KV (frontend)** | Currently using Vercel-proprietary KV — needs standard Redis |
| **Artifact retention** | No retention policy enforced yet — needs TTL or object storage with lifecycle rules |
| **Periodic job runner** | Weekly batch has no automated trigger yet — needs Nomad periodic job or equivalent |
