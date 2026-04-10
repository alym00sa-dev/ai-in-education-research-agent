# EduAgent — Architecture Diagrams

---

## Diagram 1: High-Level System Overview

```mermaid
graph TD
    Browser["Browser (User)"]

    subgraph Vercel ["Vercel — Next.js Frontend"]
        UI["UI Pages\n/agent, /agent/[id],\n/agent/graph/[id]"]
        API_Init["/api/research/stream\n(thread init only)"]
        API_Runs["/api/runs\n(run history)"]
        API_Graph["/api/graph/chat\n/api/graph/sessions"]
        RedisKV["Redis KV\n(run metadata +\ngraph sessions)"]
    end

    subgraph Render ["Render — LangGraph Backend (Python)"]
        LG["LangGraph Server"]
        DeepResearch["agent graph\n(Deep Research)"]
        GraphTraversal["graph_traversal graph\n(Graph Traversal)"]
        Postgres["Postgres\n(thread checkpoints)"]
        Redis["Redis\n(SSE pub/sub)"]
    end

    subgraph Neo4j ["Neo4j Aura / Enterprise"]
        KG["Knowledge Graph\nPaper · Intervention\nEmpiricalFinding · Outcome"]
    end

    Browser -->|"HTTPS POST (init)"| API_Init
    Browser -->|"SSE stream (direct, long-lived)"| LG
    Browser -->|"HTTPS"| API_Runs
    Browser -->|"HTTPS"| API_Graph

    API_Init -->|"POST /threads"| LG
    API_Runs <-->|read/write| RedisKV
    API_Graph -->|"POST /threads/.../runs/stream"| LG

    LG --> DeepResearch
    LG --> GraphTraversal
    LG <--> Postgres
    LG <--> Redis

    DeepResearch -->|"read papers at query time"| KG
    GraphTraversal -->|"read interventions + Cypher"| KG
```

---

## Diagram 2: Deep Research Run — Request Flow

```mermaid
sequenceDiagram
    actor User
    participant Vercel as Vercel\n(/api/research/stream)
    participant Render as Render\n(LangGraph)
    participant DBs as Academic DBs\n(SS · OpenAlex · ERIC · arXiv...)
    participant Neo4j as Neo4j
    participant Postgres as Postgres

    User->>Vercel: POST /api/research/stream\n{query, config, jobId}
    Vercel->>Render: POST /threads (create thread)
    Render-->>Vercel: {thread_id}
    Vercel-->>User: {thread_id, streamPayload}

    User->>Render: POST /threads/{id}/runs/stream\n(direct SSE connection)
    Note over User,Render: Long-lived SSE connection (20–35 min)

    Render->>Postgres: checkpoint initial state

    Render-->>User: SSE: [education_discovery] Analyzing question...
    Render->>Neo4j: retrieve relevant KG papers

    Render-->>User: SSE: [supervisor] Dispatching 5 researchers...
    par 5 parallel researcher threads
        Render->>DBs: semantic_scholar_search
        Render->>DBs: openalex_search
        Render->>DBs: eric_search
        Render->>DBs: arxiv_search
        Render->>DBs: snippet_search + tavily
    end
    Render->>Postgres: checkpoint after each node

    Render-->>User: SSE: [researcher] N threads complete...
    Render-->>User: SSE: [critique] Iteration N...
    Render-->>User: SSE: [final_report] Generating report...
    Render-->>User: SSE: [qa_audit] QA complete.

    User->>Vercel: POST /api/runs (save completed run)
    Vercel->>+RedisKV: store run metadata + report
```

---

## Diagram 3: Graph Traversal — Request Flow

```mermaid
sequenceDiagram
    actor User
    participant Vercel as Vercel\n(/api/graph/chat)
    participant Render as Render\n(graph_traversal graph)
    participant Neo4j as Neo4j

    User->>Vercel: POST /api/graph/chat\n{message, session_id, model}
    Vercel->>Render: POST /threads/{id}/runs/stream

    Render->>Neo4j: MATCH (i:Intervention)\nRETURN i.name (get live taxonomy)
    Neo4j-->>Render: [list of intervention names]

    Render->>Render: LLM generates 3 Cypher queries\n(specific → medium → broad)

    Render->>Neo4j: execute specific query
    Neo4j-->>Render: results (may be empty)

    alt 0 results on specific
        Render->>Neo4j: execute medium query
        Neo4j-->>Render: results
    end

    alt still 0 results
        Render->>Neo4j: execute broad query\n(searches extended_summary)
        Neo4j-->>Render: results
    end

    Render->>Render: LLM synthesizes results\ninto conversational response
    Render-->>Vercel: SSE stream
    Vercel-->>User: response text

    User->>Vercel: POST /api/graph/sessions (save session)
    Vercel->>RedisKV: store session + message history
```

---

## Diagram 4: Weekly KG Batch Pipeline

```mermaid
flowchart TD
    CRON["Cron Trigger\nMonday 06:00 UTC"]

    subgraph Batch ["run_weekly_batch.py"]
        S1["Step 1: Read queue\nSELECT FROM kg_queue\nWHERE status = 'queued'"]
        S2["Step 2: PDF Extraction\npdf_extractor_kg\n3-call LLM extraction per paper\n(metadata · taxonomy · citations)"]
        S3["Step 3: Citation Chasing\ncitation_chaser --incremental\nTraverse Semantic Scholar\ncitation graph L1/L2/L3"]
        S4["Step 4: CCM Retrain\nfastRP embeddings K=128\nK-means clusters k=15\nPageRank fitness scores\nSleeping beauty coefficients"]
        S5["Step 5: Neo4j Write\nneo4j_writer --skip-wipe\nMERGE Paper · Intervention\nEmpiricalFinding · Outcome nodes"]
        S6["Step 6: Mark complete\nUPDATE kg_queue\nSET status = 'done'"]
    end

    Postgres[("Postgres\nkg_queue table")]
    SemanticScholar["Semantic Scholar\nCitation API"]
    Neo4j[("Neo4j\nKnowledge Graph")]

    CRON --> S1
    S1 -->|queued papers| S2
    S1 <-->|read/write| Postgres
    S2 --> S3
    S3 <-->|citation edges| SemanticScholar
    S3 --> S4
    S4 --> S5
    S5 -->|MERGE nodes + edges| Neo4j
    S5 --> S6
    S6 -->|update status| Postgres
```

---

## Diagram 5: Paper Queue Flow (Research Run → Weekly Batch)

```mermaid
flowchart LR
    subgraph ResearchRun ["Deep Research Run"]
        KGWrite["kg_write node\n(end of each run)"]
    end

    subgraph Queue ["Postgres — kg_queue"]
        Row["status: queued\nsession_id, doi, title\nurl, profile JSONB\nqueued_at"]
    end

    subgraph WeeklyBatch ["Weekly Batch"]
        Read["SELECT WHERE\nstatus = 'queued'"]
        Process["extract → cite-chase\n→ CCM → Neo4j"]
        Done["UPDATE status\n= 'done'"]
    end

    Neo4j[("Neo4j")]

    KGWrite -->|"INSERT ON CONFLICT (doi) DO NOTHING"| Row
    Row --> Read
    Read --> Process
    Process -->|MERGE| Neo4j
    Process --> Done
    Done -->|processed_at, batch_date| Row

    style Row fill:#f0f4ff,stroke:#6366f1
```

---

## Diagram 6: Data Persistence Overview

```mermaid
graph LR
    subgraph Ephemeral ["Per-Request (Ephemeral)"]
        SSE["SSE event stream\n(in-flight only)"]
    end

    subgraph Postgres ["Postgres"]
        LGState["LangGraph thread state\n(run checkpoints)"]
        KGQueue["kg_queue\n(paper ingest queue)"]
    end

    subgraph Redis ["Redis (LangGraph)"]
        PubSub["SSE pub/sub\n(event routing)"]
    end

    subgraph RedisKV ["Redis KV (Frontend)"]
        Runs["Run metadata\n+ reports"]
        Sessions["Graph chat\nsessions"]
    end

    subgraph Neo4j ["Neo4j"]
        Graph["Knowledge graph\nPaper · Intervention\nEmpiricalFinding · Outcome"]
    end

    LGState -->|"survives restarts"| Postgres
    KGQueue -->|"survives restarts"| Postgres
    PubSub -->|"in-memory, short-lived"| Redis
    Runs -->|"accessible cross-device"| RedisKV
    Sessions -->|"accessible cross-device"| RedisKV
    Graph -->|"persistent, weekly updates"| Neo4j
```

---

## Component Summary

| Component | Current Host | Role |
|---|---|---|
| Next.js Frontend | Vercel | UI, API proxy, run history |
| LangGraph Backend | Render | Deep Research + Graph Traversal execution |
| Postgres | Render add-on | LangGraph checkpoints + KG ingest queue |
| Redis (backend) | Render add-on | LangGraph SSE pub/sub |
| Redis KV (frontend) | Vercel KV | Run metadata + graph session history |
| Neo4j | AuraDB (→ Gates Enterprise) | AI-in-education knowledge graph |
| Weekly Batch | Manual (→ Render Cron / Nomad periodic) | KG update pipeline |
