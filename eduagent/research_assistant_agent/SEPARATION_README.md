# Research Assistant Agent

This folder contains the **agent-only** components of the research assistant system.

## What's Inside

- **`src/`** - Core agent logic
  - `neo4j_config.py` - Neo4j database connection
  - `evidence_map.py` - Evidence gap map queries
  - `kg_extractor.py` - Knowledge graph extraction
  - `research_pipeline.py` - Research pipeline
  - `session_manager.py` - Session management

- **`app.py`** - Streamlit interface for the agent

- **Data Processing Scripts**:
  - `import_wwc_to_neo4j.py` - Import WWC data to Neo4j
  - `map_wwc_to_ios.py` - Map WWC to implementation objectives
  - `process_wwc_data.py` - Process WWC datasets
  - `init_database.py` - Initialize database
  - `migrate_schema.py` - Database migrations
  - `test_neo4j.py` - Test Neo4j connection

- **Data Files**:
  - `wwc_*.json` - What Works Clearinghouse data
  - `*interventions*.json` - Intervention mapping data

- **Documentation**:
  - `SCHEMA.md` - Database schema
  - `PIPELINE.md` - Research pipeline documentation
  - `QUICKSTART.md` - Quick start guide
  - `IMPROVEMENTS.md` - Improvement notes
  - `STREAMLIT_DEPLOYMENT.md` - Deployment guide

## Purpose

This module can be moved to another location along with `open_deep_research` to consolidate agentic systems.

## Dependencies

- Neo4j database
- Python packages in `requirements.txt`
- Environment variables in `.env`

## Note

This module is **independent** of the visualization dashboard. It contains only the agent logic for deep research, evidence mapping, and knowledge graph operations.
