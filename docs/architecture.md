# Architecture

EduAgent has three independent subsystems that share a Neo4j knowledge graph as common infrastructure.

---

## Subsystems at a Glance

```
User (browser)
     |
     | HTTP / SSE
     v
eduagent_frontend/         Next.js 14 (Vercel)
  app/api/                 API routes — proxy to backend, read local files
  hooks/                   React hooks — SSE streaming, session state
  components/              UI — QueryBar, JobsFeed, ReportDrawer, ChatBubble
     |
     | HTTP / SSE (RENDER_URL env var)
     v
eduagent_backend/          LangGraph Platform (Render)
  deep-research-src/       "agent" graph — 45-min deep research pipeline
  graph-traversal-src/     "graph_traversal" graph — instant KG chat
     |
     | Bolt (NEO4J_URI env var)
     v
Neo4j (Aura)               Knowledge graph — 234 papers, 5000+ relationships
     ^
     |
  KG-src/                  Offline batch ingestion pipeline (runs locally / cron)
```

---

## 1. Deep Research Pipeline

**Entry:** User submits a query from the frontend. The frontend calls `POST /api/research/stream` (Next.js route) which opens an SSE connection to the LangGraph backend.

**Graph:** `deep-research-src/graph.py` defines the StateGraph with these nodes:

```
education_discovery
        |
        v
research_supervisor  <----> researcher (1-3 iterations)
        |                    researcher_reflect
        v
supervisor_critique (optional, controlled by research_iterations config)
        |
        v
executive_summary
        |
        v
citation_connector (KG gap analysis)
        |
        v
final_report_generation
        |
        v
qa_scoring
        |
        v
kg_write (queues new papers for batch ingestion)
```

**State:** `deep-research-src/state.py` — `AgentState` carries everything: messages, research brief, notes, paper profiles, final report, QA score.

**Key config** (`configuration.py`):
- `research_model`: which LLM the researcher nodes use (default `openai:gpt-4.1`)
- `research_iterations`: number of critique cycles (1 = one critique pass)
- `max_sources`: top-k sources cited in final report
- `recursion_limit`: must be 200+ — the default of 25 kills mid-run

**Output:** Streamed events arrive at the frontend in real time. On completion, `output_saver.py` writes `final_report_*.md`, `qa_report_*.md`, and `state_snapshot_*.json` to `deep-research-output/<session_id>/`.

---

## 2. Graph Traversal Pipeline

**Entry:** User sends a chat message from the graph traversal tab. Frontend calls `POST /api/graph/chat` which forwards the request to the LangGraph backend.

**Graph:** `graph-traversal-src/graph_traversal.py` — single file, two LLM calls per turn:

```
user message
     |
     v
Cypher generation (gpt-4.1, temperature=0, structured output → CypherQuery)
     |
     v
Neo4j query (async, run in thread executor to avoid blocking event loop)
     |
     v
Synthesis (gpt-4.1-mini) → streamed response to frontend
```

**Thread management:** Each chat session maps to a LangGraph thread (identified by `session_id`). The frontend creates the thread via `POST /threads` on first message and reuses it for follow-ups.

**Session storage:** Chat history is saved as JSON files in `graph-traversal-output/<session_id>.json` by the Next.js API route (`app/api/graph/sessions/route.ts`). These are local-disk files — in production you'd need a persistent store.

---

## 3. KG Corpus Pipeline

**Purpose:** Offline batch process that ingests research papers into Neo4j. Runs manually or on a cron schedule. Not part of the user-facing request path.

**Flow:**

```
ingested_papers/*.json  (paper metadata + full text)
          |
          v
pdf_extractor_kg.py   (3 LLM calls: metadata extraction, taxonomy tagging, abstract distillation)
          |
          v
neo4j_writer.py       (MERGE Paper, Intervention, EmpiricalFinding nodes + CITES relationships)
          |
          v
citation_chaser.py    (1.5-hop citation traversal → L1/L2/L3 depth taxonomy)
          |
          v
ccm_trainer.py        (scores papers: η, cluster_id, field_momentum, sb_coef)
          |
          v
run_weekly_batch.py   (orchestrates the full sequence above)
```

**Entry point:** `python KG-src/run_weekly_batch.py`

**Adding papers:** Place new paper JSON files in `KG-src/ingested_papers/` then run the batch. See [kg-pipeline.md](kg-pipeline.md) for format details.

---

## 4. Frontend Architecture

The Next.js frontend is primarily a thin proxy with streaming support.

**Routing:**
- `/` — landing page
- `/agent` — main interface (Deep Research tab + Graph Traversal tab)
- `/agent/[id]` — research session detail (report, sources, thought log)
- `/agent/graph/[id]` — graph traversal chat session

**Data flow for deep research:**
1. `QueryBar` → `useResearch` hook → `fetch('/api/research/stream')`
2. Next.js route opens SSE to `RENDER_URL/runs/stream`
3. Events arrive: `on_node_start`, `on_llm_chunk`, `on_node_end`, final state
4. `useResearch` updates job state → `JobsFeed` + `ReportDrawer` re-render
5. On completion, job saved to localStorage by `useJobs`

**Data flow for graph traversal:**
1. User types in chat input → `useGraphChat.sendMessage`
2. `POST /api/graph/chat` → LangGraph backend → SSE tokens back
3. Tokens stream into the AI message bubble
4. On completion, `handleMessageComplete` saves full conversation to disk via `POST /api/graph/sessions`

---

## Environment Variables

See `.env.example` (backend) and `.env.local.example` (frontend) for the full list. The critical ones:

| Variable | Where | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | backend | All LLM calls |
| `TAVILY_API_KEY` | backend | Web search |
| `NEO4J_URI` | backend | KG queries |
| `RENDER_URL` | frontend | Points frontend API routes to the LangGraph backend |

---

## Adding a New Node to the Research Pipeline

1. Create `deep-research-src/nodes/my_node.py` with a function `async def my_node(state: AgentState, config: RunnableConfig) -> dict`
2. Add the prompt to `deep-research-src/prompts/my_node.py`
3. Register in `graph.py`: `workflow.add_node("my_node", my_node)` and add the appropriate edge
4. Add any new state fields to `state.py` with a default value
5. Test locally with `python run_pipeline.py`
