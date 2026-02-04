# AI Education Research Assistant

An intelligent research assistant that combines Open Deep Research with Neo4j knowledge graphs to conduct comprehensive literature reviews on AI in education, with a focus on tutoring systems.

## Features

- 🔍 **Automated Research**: Leverages Open Deep Research for comprehensive literature search
- 📊 **Knowledge Graph**: Automatically extracts and structures findings into Neo4j
- 💬 **Session Management**: Maintain multiple research chats with conversation history
- 🎯 **Preset Queries**: 8 tutoring-focused research templates
- 📈 **Interactive Visualization**: Explore knowledge graph connections
- 🔄 **Cumulative Learning**: Graph grows across sessions, revealing cross-topic insights

## Architecture

```
Streamlit UI → Research Pipeline → Open Deep Research (LangGraph)
                      ↓
              KG Extractor (Claude)
                      ↓
              Neo4j Knowledge Graph
```

## Installation

### Prerequisites

1. **Neo4j Database** (Aura or local)
   - Sign up for free at https://neo4j.com/cloud/aura-free/
   - Or run locally with Neo4j Desktop

2. **Open Deep Research Backend**
   - Must be running on `http://127.0.0.1:2024`
   - See `../open_deep_research/` for setup

3. **API Keys**
   - OpenAI API key (required)
   - Anthropic API key (required for KG extraction)
   - Tavily API key (required for research)

### Setup

1. **Install dependencies:**
```bash
cd research_assistant
pip install -r requirements.txt
```

2. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your credentials
```

Required in `.env`:
```
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
LANGGRAPH_API_URL=http://127.0.0.1:2024
```

3. **Initialize Neo4j database:**
```bash
python init_database.py
```

This creates the taxonomy nodes (Population, UserType, StudyDesign, etc.)

## Usage

### Start the Application

**Terminal 1 - Open Deep Research Backend:**
```bash
cd ../open_deep_research
uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev --allow-blocking
```

**Terminal 2 - Research Assistant:**
```bash
cd research_assistant
streamlit run app.py
```

The Streamlit UI will open at `http://localhost:8501`

### Using the Interface

1. **Select a Preset Query** from the sidebar (e.g., "ITS Effectiveness")
   - Or enter your own custom research question

2. **Configure Research Parameters:**
   - Model Provider (GPT-4.1, Claude Sonnet, etc.)
   - Search Depth (standard/deep/comprehensive)
   - Focus Area (K-12, Higher Ed, etc.)

3. **Start Research** - Takes 3-7 minutes:
   - Conducts deep literature search
   - Extracts paper content
   - Uses Claude to extract structured metadata
   - Adds to Neo4j knowledge graph
   - Returns summary + visualization

4. **View Results:**
   - Natural language research summary
   - Papers added to knowledge graph
   - Interactive graph visualization
   - Paper metadata (objective, outcome, findings)

5. **Session Management:**
   - View past research sessions in sidebar
   - Load previous sessions to see their graphs
   - Start new research chats
   - Follow-up questions extend the session

## Knowledge Graph Schema

### Node Types
- **Paper**: Research papers with metadata
- **EmpiricalFinding**: Study results with direction, effect size, etc.
- **Population**: Target population (Elementary, High School, etc.)
- **UserType**: Who uses the system (Student, Educator, etc.)
- **StudyDesign**: Research methodology (RCT, Meta-Analysis, etc.)
- **ImplementationObjective**: AI system purpose (Tutoring, Advising, etc.)
- **Outcome**: Measured outcomes (Cognitive, Behavioral, Affective)

### Relationships
- `Paper → Population, UserType, StudyDesign, ImplementationObjective, Outcome, EmpiricalFinding`
- `Outcome → EmpiricalFinding`
- `ImplementationObjective → Outcome` (derived from papers, shows common patterns)

See `SCHEMA.md` for complete details.

## Pipeline Flow

See `PIPELINE.md` for detailed step-by-step execution flow from query to response.

## Project Structure

```
research_assistant/
├── src/
│   ├── neo4j_config.py          # Neo4j connection & taxonomy setup
│   ├── session_manager.py       # Research session management
│   ├── kg_extractor.py          # Paper fetching & KG extraction
│   └── research_pipeline.py     # Orchestrates complete workflow
├── app.py                       # Streamlit UI
├── init_database.py             # Initialize Neo4j with taxonomies
├── test_neo4j.py                # Test Neo4j connection
├── requirements.txt             # Python dependencies
├── .env                         # Your credentials (not in git)
├── .env.example                 # Template
├── SCHEMA.md                    # Knowledge graph schema
├── PIPELINE.md                  # Complete pipeline documentation
└── README.md                    # This file
```

## Example Research Session

**Query:** "What is the effectiveness of intelligent tutoring systems on student learning outcomes in mathematics?"

**Results after 5 minutes:**
- 5 papers found and analyzed
- Extracted structured metadata:
  - Implementation Objectives: "Intelligent Tutoring and Instruction"
  - Outcomes: "Cognitive - Mathematical numeracy"
  - Findings: 4 Positive, 1 Mixed
  - Effect sizes: Range 0.2-0.5
- Knowledge graph updated with:
  - 5 Paper nodes
  - 5 EmpiricalFinding nodes
  - 30+ relationships created
  - 1 ImplementationObjective→Outcome connection strengthened

**Next Query:** "How does adaptive feedback timing affect learning?"
- New session created
- 4 more papers added
- Graph now shows connections across both topics
- Can visualize cumulative knowledge

## Advanced Usage

### Querying Neo4j Directly

```python
from src.neo4j_config import get_neo4j_connection

conn = get_neo4j_connection()

# Find all papers about tutoring that improved math outcomes
query = """
MATCH (p:Paper)-[:HAS_IMPLEMENTATION_OBJECTIVE]->(io:ImplementationObjective)
MATCH (p)-[:FOCUSES_ON_OUTCOME]->(o:Outcome)
MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding)
WHERE io.type = "Intelligent Tutoring and Instruction"
  AND o.name = "Cognitive - Mathematical numeracy"
  AND f.direction = "Positive"
RETURN p.title, f.effect_size
ORDER BY f.effect_size DESC
"""

results = conn.execute_query(query)
for r in results:
    print(f"{r['p.title']}: {r['f.effect_size']}")
```

### Custom Extraction Prompt

Edit `src/kg_extractor.py` to modify the LLM extraction prompt if you want to:
- Add new taxonomy categories
- Change extraction instructions
- Adjust structured output format

## Troubleshooting

### "Connection refused" to Neo4j
- Verify Neo4j is running
- Check URI in `.env` (should be `neo4j+s://` for Aura)
- Test with `python test_neo4j.py`

### "No response from LangGraph server"
- Ensure Open Deep Research backend is running on port 2024
- Check with `curl http://127.0.0.1:2024/ok`

### "Anthropic API error"
- Verify `ANTHROPIC_API_KEY` in `.env`
- Ensure you have API credits
- Check rate limits

### Papers not being extracted
- Some URLs may be inaccessible (paywalls, broken links)
- PDF extraction can fail for scanned/image PDFs
- Web scraping may be blocked by some sites

### Slow performance
- Research takes 3-7 minutes (normal)
- Reduce `search_depth` to "standard" for faster results
- LLM extraction is the bottleneck (1-2 min per paper)

## Contributing

This is a research tool built for education AI literature reviews. Feel free to:
- Add new preset queries
- Extend the taxonomy
- Improve paper extraction for specific sources
- Add new visualization types

## License

MIT - See LICENSE file

## Acknowledgments

- Built on [Open Deep Research](https://github.com/langchain-ai/open_deep_research)
- Uses [Neo4j](https://neo4j.com/) for knowledge graph
- Powered by [LangChain](https://langchain.com/), [Streamlit](https://streamlit.io/), [Anthropic Claude](https://anthropic.com/)
