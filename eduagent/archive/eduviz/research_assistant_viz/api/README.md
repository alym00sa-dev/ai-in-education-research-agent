# AI Education Research API

FastAPI backend for the Evidence Map Visualization Dashboard.

## Quick Start (Local Development)

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp ../.env .env  # Use shared .env from research_assistant/

# Run server
uvicorn api.main:app --reload --port 8000

# View API docs
open http://localhost:8000/docs
```

## API Endpoints

### Health & Stats
- `GET /api/health` - Health check
- `GET /api/v1/stats` - Database statistics

### Visualizations
- `GET /api/v1/visualizations/level1` - Problem Burden Map data
- `GET /api/v1/visualizations/level2` - Intervention Evidence Map data

### Evidence Map
- `GET /api/v1/evidence-map/matrix` - Full 48-cell matrix
- `GET /api/v1/evidence-map/cell/{io}/{outcome}` - Papers for specific cell
- `GET /api/v1/evidence-map/cell/{io}/{outcome}/synthesis` - AI synthesis

### Sessions
- `GET /api/v1/sessions` - List research sessions
- `GET /api/v1/sessions/{id}` - Session details
- `GET /api/v1/sessions/{id}/papers` - Session papers
- `GET /api/v1/sessions/{id}/graph` - Graph visualization data

### Taxonomy
- `GET /api/v1/taxonomy/implementation-objectives`
- `GET /api/v1/taxonomy/outcomes`
- `GET /api/v1/taxonomy/populations`
- `GET /api/v1/taxonomy/user-types`
- `GET /api/v1/taxonomy/study-designs`

## Deployment

See [DEPLOYMENT.md](../../DEPLOYMENT.md) in the root directory for full deployment instructions.

### Quick Deploy to Render

1. Push code to GitHub
2. Connect repository to Render
3. Set root directory: `research_assistant`
4. Set build command: `pip install -r api/requirements.txt`
5. Set start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables (see DEPLOYMENT.md)

## Architecture

```
Frontend (Vercel)
    ↓ REST API
Backend (FastAPI)
    ↓ Reuses existing code
research_assistant/src/
    ↓ Neo4j Driver
Neo4j Aura
```

## Environment Variables

Required:
- `NEO4J_URI` - Neo4j connection URI
- `NEO4J_USER` - Neo4j username
- `NEO4J_PASSWORD` - Neo4j password
- `NEO4J_DATABASE` - Neo4j database name (default: "neo4j")

Optional:
- `ANTHROPIC_API_KEY` - For synthesis generation

## Project Structure

```
api/
├── main.py              # FastAPI app entry point
├── config.py            # Configuration & CORS
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── routers/            # API route handlers
│   ├── evidence_map.py
│   ├── sessions.py
│   ├── taxonomy.py
│   └── visualizations.py
├── models/             # Pydantic response models
│   ├── evidence_map.py
│   ├── session.py
│   └── visualization.py
└── services/           # Business logic
    ├── evidence_map_service.py
    ├── session_service.py
    └── visualization_service.py
```

## Development

### Adding New Endpoints

1. Create route handler in `routers/`
2. Define response models in `models/`
3. Add business logic in `services/`
4. Include router in `main.py`

### Testing

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest tests/

# Test specific endpoint
curl http://localhost:8000/api/v1/visualizations/level1
```

## CORS Configuration

By default, CORS allows:
- `http://localhost:3000` (local dev)
- `https://*.vercel.app` (Vercel deployments)

Update `config.py` to add more origins.

## Documentation

- Interactive API docs: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc
- OpenAPI schema: http://localhost:8000/openapi.json
