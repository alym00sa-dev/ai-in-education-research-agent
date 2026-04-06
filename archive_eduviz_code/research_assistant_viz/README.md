# Research Assistant Visualization API

This folder contains the **visualization API** that powers the dashboard frontend.

## What's Inside

- **`api/`** - FastAPI application
  - `main.py` - API entry point
  - `config.py` - API configuration
  - `routers/` - API endpoints
    - `visualizations.py` - Visualization endpoints (Level 1-5, P1, P5, P1Current, Gates Investment)
    - `evidence_map.py` - Evidence map endpoints
    - `taxonomy.py` - Taxonomy endpoints
    - `sessions.py` - Session endpoints
  - `services/` - Business logic
    - `visualization_service.py` - Visualization data generation
    - `evidence_map_service.py` - Evidence map service
    - `session_service.py` - Session service
  - `models/` - Pydantic models
    - `visualization.py` - Visualization response models
    - `evidence_map.py` - Evidence map models

- **`src/`** - Shared dependencies (Neo4j, evidence mapping)
  - Required by the API for data access

## Purpose

This is the **backend API** for the visualization dashboard (`kg-viz-frontend`).

It provides REST endpoints that:
- Generate bubble charts (Level 1-5)
- Generate time series visualizations (Level 5, P1, P5)
- Generate evidence ladders (P1Current)
- Serve evidence map data
- Handle taxonomy queries

## Dependencies

- FastAPI
- Neo4j database (via `src/neo4j_config.py`)
- Python packages in `api/requirements.txt`
- Environment variables in `.env`

## Running

```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Note

This module should **stay with the visualization dashboard**. It's tightly coupled to `kg-viz-frontend` and provides all the data endpoints the frontend needs.

The frontend fetches data from: `http://localhost:8000/api/v1/visualizations/...`
