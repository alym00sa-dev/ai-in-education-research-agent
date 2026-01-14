"""API configuration and settings."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from research_assistant directory (shares same credentials)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

class Settings:
    """Application settings loaded from environment variables."""

    # Neo4j Configuration
    NEO4J_URI: str = os.getenv("NEO4J_URI")
    NEO4J_USER: str = os.getenv("NEO4J_USER")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD")
    NEO4J_DATABASE: str = os.getenv("NEO4J_DATABASE", "neo4j")

    # API Metadata
    API_VERSION: str = "1.0.0"
    API_TITLE: str = "AI Education Research API"
    API_DESCRIPTION: str = "REST API for Evidence Map and Research Data"

    # CORS - Allow all origins (you can restrict this later to your specific Vercel domain)
    ALLOWED_ORIGINS: list = ["*"]  # Allows all origins - replace with your specific Vercel URL for production

settings = Settings()
