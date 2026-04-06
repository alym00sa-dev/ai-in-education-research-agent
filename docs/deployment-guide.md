# Deployment Guide

EduAgent has two deployable components:

- **Backend** — LangGraph server hosting the deep research and graph traversal graphs, deployed on Render
- **Frontend** — Next.js app, deployed on Vercel

---

## Backend: Render

The backend uses LangGraph Platform, which bundles the graphs defined in `langgraph.json` into a managed server. Render runs it as a Docker-based web service.

### What to deploy

The root of the deployment is `eduagent/eduagent_backend/`. Render needs to build and run this as a LangGraph server.

### Steps

1. **Create a Render Web Service** pointing at the repo.

2. **Set the root directory** to `eduagent/eduagent_backend` in Render's service settings.

3. **Set the build command:**
   ```
   pip install langgraph-cli && langgraph build -t eduagent-backend
   ```
   Or if using Docker directly, LangGraph CLI generates a Dockerfile — run `langgraph dockerfile Dockerfile` locally and commit the Dockerfile, then set Render to use it.

4. **Set the start command:**
   ```
   langgraph up
   ```
   Or if using the generated Dockerfile, Render will use the `CMD` in it automatically.

5. **Set environment variables** in Render's dashboard:

   | Variable | Value |
   |---|---|
   | `OPENAI_API_KEY` | Your OpenAI key |
   | `TAVILY_API_KEY` | Your Tavily key |
   | `ANTHROPIC_API_KEY` | Your Anthropic key (optional) |
   | `NEO4J_URI` | Your Neo4j Aura connection string (e.g. `neo4j+s://xxxx.databases.neo4j.io`) |
   | `NEO4J_USERNAME` | `neo4j` |
   | `NEO4J_PASSWORD` | Your Neo4j Aura password |
   | `NEO4J_DATABASE` | `neo4j` |
   | `ERIC_API_KEY` | ERIC API key |
   | `ELSEVIER_API_KEY` | Elsevier/Scopus API key |
   | `LANGSMITH_API_KEY` | LangSmith key (optional, for tracing) |

6. **Port**: LangGraph server listens on port 8000 by default. Set `PORT=8000` in Render or configure Render's port setting to 8000.

7. **Instance type**: Deep research runs are CPU-intensive and can take 20-45 minutes. Use at least a Standard instance (1 CPU, 2GB RAM). For concurrent users, use a larger instance or enable auto-scaling.

8. After deploy, note the service URL (e.g. `https://eduagent-backend.onrender.com`). This is your `RENDER_URL`.

### Notes on disk

The backend does not persist output to Render's ephemeral disk between deploys — that is intentional. Deep research outputs are returned to the frontend via the streaming API. Graph traversal chat sessions are stored in the frontend (Vercel) via the `graph-traversal-output/` JSON files, but on Vercel those are also ephemeral.

If you need persistent output storage, attach a Render Disk or use an S3 bucket and update `output_saver.py` and the sessions route accordingly.

---

## Frontend: Vercel

The frontend is a standard Next.js App Router project. Vercel is the natural host.

### Steps

1. **Import the repo** into Vercel and set the root directory to `eduagent/eduagent_frontend`.

2. **Framework preset**: Vercel auto-detects Next.js.

3. **Set environment variables** in Vercel's project settings:

   | Variable | Value |
   |---|---|
   | `RENDER_URL` | Your Render backend URL (e.g. `https://eduagent-backend.onrender.com`) |
   | `LANGGRAPH_URL` | Same as `RENDER_URL` (used by deep research API routes) |

   Do not expose API keys in the frontend — all LLM calls go through the backend.

4. **Deploy**. Vercel handles build and CDN distribution automatically.

### API routes

The Next.js app contains several API routes under `app/api/` that proxy requests to the Render backend:

- `app/api/graph/chat/route.ts` — proxies graph traversal queries to LangGraph
- `app/api/research/route.ts` — proxies deep research requests to LangGraph
- `app/api/local-runs/route.ts` — reads from `deep-research-output/` on disk (local dev only; in production this directory won't exist on Vercel)
- `app/api/graph/sessions/route.ts` — reads/writes graph session JSON to `graph-traversal-output/` (local dev only)

For production, `local-runs` and `graph/sessions` will need to be backed by a persistent store (database or object storage) rather than the local filesystem. For now, these routes are primarily useful in local development.

---

## Local Development

```bash
# Terminal 1 — backend
cd eduagent/eduagent_backend
cp .env.example .env   # fill in keys
uv sync
langgraph dev           # runs on http://localhost:2024

# Terminal 2 — frontend
cd eduagent/eduagent_frontend
cp .env.local.example .env.local
# Set RENDER_URL=http://localhost:2024 and LANGGRAPH_URL=http://localhost:2024
npm install
npm run dev             # runs on http://localhost:3000
```

---

## Knowledge Graph Setup (Neo4j)

The graph traversal mode requires a populated Neo4j database. To rebuild the corpus from scratch:

```bash
cd eduagent/eduagent_backend/KG-src
python backfill_kg.py   # re-indexes all papers into Neo4j
```

For production, use Neo4j Aura (managed cloud). Free tier supports the current corpus size (~234 papers, ~5000 relationships). Set the Aura connection string in both local `.env` and Render environment variables.
