"""FastAPI application for AI Education Research API."""
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add research_assistant to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.config import settings
from api.routers import evidence_map, sessions, taxonomy, visualizations

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS for Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=False,  # Changed to False to allow wildcard origins
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    evidence_map.router,
    prefix="/api/v1/evidence-map",
    tags=["Evidence Map"]
)
app.include_router(
    sessions.router,
    prefix="/api/v1/sessions",
    tags=["Sessions"]
)
app.include_router(
    taxonomy.router,
    prefix="/api/v1/taxonomy",
    tags=["Taxonomy"]
)
app.include_router(
    visualizations.router,
    prefix="/api/v1/visualizations",
    tags=["Visualizations"]
)


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
        "docs": "/docs",
        "health": "/api/health"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify API and Neo4j connectivity."""
    try:
        from src.neo4j_config import get_neo4j_connection
        conn = get_neo4j_connection()

        # Try to get node counts as a connectivity test
        node_counts = conn.get_node_counts()

        return {
            "status": "healthy",
            "neo4j_connected": True,
            "version": settings.API_VERSION,
            "database_stats": {
                "total_nodes": sum(node_counts.values()),
                "node_types": len(node_counts)
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "neo4j_connected": False,
            "version": settings.API_VERSION,
            "error": str(e)
        }


@app.get("/api/v1/stats")
async def get_stats():
    """Get database statistics."""
    try:
        from src.neo4j_config import get_neo4j_connection
        conn = get_neo4j_connection()
        node_counts = conn.get_node_counts()

        return {
            "total_papers": node_counts.get('Paper', 0),
            "total_sessions": node_counts.get('Session', 0),
            "total_findings": node_counts.get('EmpiricalFinding', 0),
            "node_counts": node_counts
        }
    except Exception as e:
        return {
            "error": f"Failed to retrieve stats: {str(e)}"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
