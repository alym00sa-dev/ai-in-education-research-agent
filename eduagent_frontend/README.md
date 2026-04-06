# EduAgent — Education Research Platform

A professional web interface for the EduAgent research system, replacing the Streamlit frontend with a clean, modern Next.js application.

## What this is

EduAgent is a research tool for education professionals and researchers. It connects to a LangGraph-powered deep research backend (hosted on Render) and surfaces findings through a minimal, easy-to-read interface.

The platform is designed around two core modes:

**Research mode** — Submit a research question and let the agent pull from academic databases (ERIC, OpenAlex, Semantic Scholar, Arxiv) and the web. Results stream back live as the agent works, and past sessions are loaded from the Neo4j knowledge graph so your research history is always available.

**Strategic Canvas** — (in progress) A guided mode for turning a broad education challenge into a structured research strategy, powered by the same research engine.

## Current status

- Research mode is fully functional: query submission, live streaming, report display, source listing, thought log
- Past sessions load from Neo4j via the Render backend and merge with local browser jobs
- Strategic Canvas tab renders a placeholder shell — full port in progress
- Deployment target: Vercel (frontend) + Render (Python backend)

## Stack

- **Next.js 14** (App Router, TypeScript)
- **Tailwind CSS** — neutral/cream color palette (`--bg: #fafaf9`)
- **LangGraph** backend on Render — streamed via SSE (`event: values` / `event: events`)
- **Neo4j** — session persistence and knowledge graph

## Local development

```bash
cd eduagent/edu_discovery_platform
npm install
cp .env.local.example .env.local   # set RENDER_API_URL
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

The backend must be running (locally at `http://127.0.0.1:2024` or point `RENDER_API_URL` to Render).

## Environment variables

| Variable | Description |
|---|---|
| `RENDER_API_URL` | Base URL of the Render FastAPI backend |

Neo4j credentials are set on the Render server side (`NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `NEO4J_DATABASE`).

## Project structure

```
app/
  agent/page.tsx       — main page (Research + Canvas modes)
  api/
    research/stream/   — SSE proxy to Render backend
    sessions/          — sessions proxy (30s cache)
components/
  layout/Navbar.tsx    — top bar, mode switcher
  agent/
    QueryBar.tsx       — query input + config (model, depth, sources)
    JobsFeed.tsx       — job history feed
    JobRow.tsx         — single job card
    ReportDrawer.tsx   — slide-over: Report, Sources, Thoughts tabs
  canvas/
    CanvasShell.tsx    — Strategic Canvas placeholder
hooks/
  useJobs.ts           — localStorage job state
  useResearch.ts       — SSE streaming + state updates
  useSessions.ts       — Neo4j session fetching
lib/
  types.ts             — shared types (Job, ResearchConfig, etc.)
  utils.ts             — cn(), timeAgo(), truncate()
```
