# EduAgent

EduAgent is an AI-powered education research assistant with two modes of interaction:

**Deep Research** — generates full literature review reports (20-45 min) by searching academic databases (ERIC, OpenAlex, arXiv, Elsevier, Semantic Scholar) and the open web, then synthesizing findings into a cited report with QA scoring.

**Graph Traversal** — instant conversational access to a curated corpus of 230+ AI-in-education papers stored in a Neo4j knowledge graph. Ask questions in plain English; the system generates Cypher queries and synthesizes answers in seconds.

For architecture details, knowledge graph schema, and pipeline changelog, see [docs/](docs/).

---

## Local Setup

### Prerequisites

- Python 3.11+ with [uv](https://github.com/astral-sh/uv)
- Node.js 18+
- Neo4j (local or Aura) — required for Graph Traversal mode only
- API keys: OpenAI, Tavily, and optionally Anthropic

### 1. Backend

```bash
cd eduagent_backend
cp .env.example .env   # fill in API keys
uv sync
langgraph dev
```

The LangGraph dev server runs on `http://localhost:2024`.

### 2. Frontend

```bash
cd eduagent_frontend
cp .env.local.example .env.local   # set LANGGRAPH_URL and RENDER_URL
npm install
npm run dev
```

The Next.js app runs on `http://localhost:3000`.

### Environment Variables

**Backend `.env`:**

```
OPENAI_API_KEY=
TAVILY_API_KEY=
ANTHROPIC_API_KEY=
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=
NEO4J_DATABASE=neo4j
ERIC_API_KEY=
ELSEVIER_API_KEY=
```

**Frontend `.env.local`:**

```
LANGGRAPH_URL=http://localhost:2024
RENDER_URL=http://localhost:2024
```

In production, `RENDER_URL` points to the deployed Render backend and `LANGGRAPH_URL` is unused (the backend handles LangGraph internally).

---

## Output Directories

- `eduagent_backend/deep-research-output/` — deep research reports and state snapshots
- `eduagent_backend/graph-traversal-output/` — graph traversal chat session JSON files

---

## Deployment

See [docs/deployment-guide.md](docs/deployment-guide.md) for Render (backend) and Vercel (frontend) deployment steps.
