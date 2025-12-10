# AI Education Research Assistant

An intelligent research assistant that combines [Open Deep Research](https://github.com/langchain-ai/open-deep-research) with source quality checks and paper KG visualizations to conduct comprehensive literature reviews on AI in education.


## 📁 Project Structure

```
LangChain-Agent/
├── open_deep_research/          # Core research agent (LangGraph)
│   ├── src/
│   │   └── open_deep_research/
│   │       ├── deep_researcher.py    # Main LangGraph workflow
│   │       ├── prompts.py            # Research & evidence prompts
│   │       ├── state.py              # Graph state definitions
│   │       ├── configuration.py      # Settings & config
│   │       └── utils.py              # Search tools & utilities
│   ├── langgraph.json               # LangGraph deployment config
│   └── pyproject.toml               # Dependencies
│
├── research_assistant/          # Streamlit frontend + backend
│   ├── app.py                   # Main Streamlit UI
│   ├── src/
│   │   ├── research_pipeline.py     # Research orchestration
│   │   ├── kg_extractor.py          # Knowledge graph extraction
│   │   ├── session_manager.py       # Session persistence
│   │   └── neo4j_config.py          # Database config
│   └── files/                   # Research outputs
│
├── K12_Evidence_Guide_Summary.txt   # Evidence evaluation framework
```

## 🚀 Local Development Setup

### Prerequisites

- **Python 3.11+** (3.13 recommended)
- **Node.js 18+** (for LangGraph Studio)
- **Neo4j Database** (Desktop or Aura)
- **API Keys**:
  - OpenAI API key (or Anthropic/Google/Groq)
  - Tavily API key (for web search)

### Step 1: Clone the Repository

```bash
git clone https://github.com/alym00sa-dev/ai-in-education-research-agent.git
cd LangChain-Agent
```

### Step 2: Set Up Neo4j Database


1. Download and install [Neo4j Desktop](https://neo4j.com/)
2. Create a new project
3. Create a new database:
4. Start the database
5. Note the connection details:
   - URI: ``
   - Username: `neo4j`
   - Password: Your password


### Step 3: Install Dependencies

**Install UV (Python package manager):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Open Deep Research (LangGraph Backend) -- In One Terminal:**
```bash
cd open_deep_research
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

**Research Assistant (Streamlit Frontend) -- In Another Terminal:**
```bash
cd ../research_assistant
pip install -r requirements.txt  # Or create one if missing
pip install streamlit neo4j python-dotenv httpx
```

### Step 4: Configure Environment Variables

**Create `.env` in `open_deep_research/` directory:**

```bash
# LLM API Keys (choose at least one)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Search API Keys
TAVILY_API_KEY=tvly-...

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j

```

**Create `.env` in `research_assistant/` directory:**

```bash
# Same as above, plus:
LANGGRAPH_API_URL=http://127.0.0.1:2024

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j
```

### Step 5: Initialize Neo4j Database

```bash
cd research_assistant
python -c "from src.neo4j_config import initialize_database; initialize_database()"
```

This creates the controlled vocabulary nodes (Population, UserType, StudyDesign, etc.)

### Step 6: Start LangGraph Server

```bash
cd ../open_deep_research
uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev --allow-blocking
```

**You should see:**
```
LangGraph Server is running!
- LangGraph Studio: http://127.0.0.1:2024/studio
- API Docs: http://127.0.0.1:2024/docs
```

Leave this terminal running.

### Step 7: Start Streamlit Frontend

**In a new terminal:**

```bash
cd research_assistant
streamlit run app.py
```

**You should see:**
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### Step 8: Test the System

1. Open browser to `http://localhost:8501`
2. Select a preset query or enter your own
3. Click "Conduct Research"
4. Wait 5-8 minutes for research to complete
5. View the research summary, knowledge graph, and extracted papers

### Accessing the Application

- **Streamlit UI**: http://localhost:8501 (main user interface)
- **LangGraph Studio**: http://127.0.0.1:2024/studio (backend debugging/visualization)
- **LangGraph API Docs**: http://127.0.0.1:2024/docs (API documentation)


## 📊 Understanding the Evidence Framework

Sources are evaluated using the **K-12 Evidence Framework**:

- **🔵 BLUE (Highest Quality)**: Meta-analyses, RCTs, peer-reviewed, addresses priority populations
- **🟢 GREEN (Moderate-Strong)**: Quasi-experimental, credible third-party, recent
- **🟡 YELLOW (Limited)**: Correlational, qualitative, some methodological concerns
- **🔴 RED (Low)**: Poor design, not credible, irrelevant

**Body of Evidence Maturity:**
- **MATURE 🔵**: Fully addresses all dimensions, confident in outcomes
- **LIMITED 🟢**: Addresses most dimensions, some gaps
- **EMERGING 🟡**: Some evidence, major gaps
- **EARLY 🔴**: Very little evidence, hypothesis only


## 🐛 Troubleshooting

### LangGraph Server Won't Start

```bash
# Check if port 2024 is in use
lsof -i :2024
# Kill the process if needed
kill -9 <PID>

# Try starting with verbose logging
uvx langgraph dev --allow-blocking --verbose
```

### Neo4j Connection Failed

```bash
# Test connection
python -c "from neo4j import GraphDatabase; driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'your-password')); driver.verify_connectivity(); print('✅ Connected!')"

# Check Neo4j is running
# In Neo4j Desktop, ensure database is started
```

### Streamlit App Crashes

```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install --upgrade streamlit neo4j httpx python-dotenv

# Check for port conflicts
lsof -i :8501
```

### Research Returns No Sources

**Check:**
1. Tavily API key is valid
2. LangGraph server is running (`curl http://127.0.0.1:2024/info`)
3. Check LangGraph terminal for errors
4. Try a simpler, more common query (e.g., "intelligent tutoring systems effectiveness")

### Knowledge Graph Shows No Edges

**This happens with old sessions.** Solution:
1. Delete old sessions (click X button in sidebar)
2. Run a new research query
3. New sessions will store graph data properly

### API Rate Limits

If you hit rate limits:
1. Use cheaper models: `gpt-4o-mini` instead of `gpt-4.1`
2. Reduce search depth to "Standard"
3. Lower `max_concurrent_research_units` in configuration

## 📚 Additional Resources

- **LangGraph Documentation**: https://langchain-ai.github.io/langgraph/
- **Open Deep Research**: https://github.com/langchain-ai/open-deep-research
- **Neo4j Documentation**: https://neo4j.com/docs/
- **Streamlit Documentation**: https://docs.streamlit.io/

## 🎓 Key Workflows

### Research Flow

```
1. User enters query → Streamlit UI
2. Streamlit calls research_pipeline.conduct_research()
3. Pipeline creates session in Neo4j
4. Pipeline calls LangGraph API (Open Deep Research)
5. LangGraph:
   - Clarifies query (if needed)
   - Creates research brief
   - Spawns parallel researchers
   - Each researcher searches & collects sources
   - Compresses findings
   - Generates final report with evidence ratings
6. Pipeline extracts structured data from report
7. Pipeline saves papers to Neo4j
8. Pipeline builds knowledge graph visualization
9. Pipeline saves graph data to session
10. Streamlit displays results
```


## 🔐 Security Notes

- **Never commit `.env` files** to Git (already in `.gitignore`)
- **API Keys**: Keep secure, rotate regularly
- **Neo4j**: Use strong passwords, enable encryption in production
- **Rate Limits**: Monitor API usage to avoid unexpected costs


## 🙏 Acknowledgments

- [LangChain](https://www.langchain.com/) for LangGraph framework
- [Open Deep Research](https://github.com/langchain-ai/open-deep-research) for research agent architecture
- [Neo4j](https://neo4j.com/) for graph database
- [Streamlit](https://streamlit.io/) for rapid UI development
- [Tavily](https://tavily.com/) for web search API

