# Research Assistant Pipeline: Query to Response

## Complete Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. USER INPUT (Streamlit UI)                                    │
│    • Selects preset query or enters custom question             │
│    • Chooses: Model, Search Depth, Focus Area                   │
│    • Clicks "Start Research"                                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. SESSION CREATION                                              │
│    session_manager.create_session()                              │
│    • Generate unique session_id                                  │
│    • Store session metadata in Neo4j                             │
│    • Return ResearchSession object                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. RESEARCH EXECUTION                                            │
│    research_pipeline.conduct_research()                          │
│    │                                                              │
│    ├─► Call Open Deep Research LangGraph API                    │
│    │   • POST to http://127.0.0.1:2024/threads/{id}/runs/stream│
│    │   • Pass query + config (model, search_depth)              │
│    │   • Stream results                                          │
│    │                                                              │
│    └─► Receive research report                                  │
│        • Natural language summary                                │
│        • Sources list (URLs to papers)                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. PAPER EXTRACTION & FETCHING                                   │
│    kg_extractor.extract_papers_from_sources()                    │
│    │                                                              │
│    ├─► For each source URL:                                     │
│    │   ├─ Check if PDF/ArXiv/PubMed                             │
│    │   ├─ Download & extract text                               │
│    │   └─ Store: (url, title, text)                             │
│    │                                                              │
│    └─► Result: List[PaperDocument]                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. KNOWLEDGE EXTRACTION (LLM)                                    │
│    kg_extractor.extract_structured_info()                        │
│    │                                                              │
│    ├─► For each paper:                                          │
│    │   │                                                          │
│    │   ├─ Call Claude/GPT with extraction prompt                │
│    │   │  (same prompt as build_kg_csvs.py)                     │
│    │   │                                                          │
│    │   └─ Extract structured JSON:                              │
│    │      {                                                       │
│    │        "title": str,                                        │
│    │        "year": int,                                         │
│    │        "venue": str,                                        │
│    │        "population": str,        // ONE from taxonomy      │
│    │        "user_type": str,         // ONE from taxonomy      │
│    │        "study_design": str,      // ONE from taxonomy      │
│    │        "implementation_objective": str,                     │
│    │        "outcome": str,           // ONE from taxonomy      │
│    │        "empirical_finding": {                               │
│    │          "direction": str,                                  │
│    │          "results_summary": str,                            │
│    │          "measure": str,                                    │
│    │          "study_size": int,                                 │
│    │          "effect_size": float                               │
│    │        }                                                     │
│    │      }                                                       │
│    │                                                              │
│    └─► Result: List[StructuredPaper]                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. KNOWLEDGE GRAPH UPDATE (Neo4j)                                │
│    kg_extractor.add_to_neo4j()                                   │
│    │                                                              │
│    ├─► For each structured paper:                               │
│    │   │                                                          │
│    │   ├─ MERGE Paper node (by title to avoid duplicates)      │
│    │   │  • Add session_id, added_date                          │
│    │   │                                                          │
│    │   ├─ CREATE EmpiricalFinding node                          │
│    │   │                                                          │
│    │   ├─ CREATE relationships:                                 │
│    │   │  • Paper -[TARGETS_POPULATION]-> Population           │
│    │   │  • Paper -[TARGETS_USER_TYPE]-> UserType              │
│    │   │  • Paper -[USES_STUDY_DESIGN]-> StudyDesign           │
│    │   │  • Paper -[HAS_IMPLEMENTATION_OBJECTIVE]-> Impl...    │
│    │   │  • Paper -[FOCUSES_ON_OUTCOME]-> Outcome              │
│    │   │  • Paper -[REPORTS_FINDING]-> EmpiricalFinding        │
│    │   │  • Outcome -[HAS_FINDING]-> EmpiricalFinding          │
│    │   │                                                          │
│    │   └─ CREATE/UPDATE derived relationship:                   │
│    │      • ImplementationObjective -[TARGETS_OUTCOME]-> Outcome│
│    │      • Increment weight property                           │
│    │                                                              │
│    └─► Update session.paper_count in Neo4j                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. GRAPH VISUALIZATION PREP                                      │
│    session_manager.get_session_graph()                           │
│    │                                                              │
│    ├─► Query Neo4j for session subgraph:                        │
│    │   MATCH (p:Paper {session_id: $session_id})                │
│    │   MATCH (p)-[*1..2]->(connected)                           │
│    │   RETURN nodes, relationships                               │
│    │                                                              │
│    └─► Format for visualization:                                │
│        {                                                          │
│          "nodes": [                                              │
│            {id, label, properties},                              │
│            ...                                                    │
│          ],                                                       │
│          "edges": [                                              │
│            {source, target, type},                               │
│            ...                                                    │
│          ]                                                        │
│        }                                                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. RESPONSE TO USER (Streamlit UI)                              │
│    │                                                              │
│    ├─► Display natural language summary                         │
│    │   • From Open Deep Research                                │
│    │   • Formatted markdown                                      │
│    │                                                              │
│    ├─► Show metadata                                            │
│    │   • X papers found and added to knowledge graph            │
│    │   • Session statistics                                      │
│    │                                                              │
│    └─► Render expandable graph visualization                    │
│        • st.expander("📊 View Knowledge Graph")                 │
│        • Interactive Plotly network graph                        │
│        • Colored by node type                                    │
│        • Hover to see properties                                 │
│        • Click to expand                                         │
└─────────────────────────────────────────────────────────────────┘
```

## Example: Step-by-Step

### User Query
"What is the effectiveness of intelligent tutoring systems on student learning outcomes in mathematics?"

### Step-by-Step Execution

**Step 1: User Input**
```python
query = "What is the effectiveness of ITS..."
model = "openai:gpt-4.1"
search_depth = "deep"
focus_area = "K-12 Education"
```

**Step 2: Session Created**
```python
session = {
    "session_id": "abc123...",
    "query": "What is the effectiveness...",
    "created_at": "2025-12-08T10:30:00",
    "model_provider": "openai:gpt-4.1",
    ...
}
# Stored in Neo4j
```

**Step 3: Research Runs**
```
→ Calling Open Deep Research...
→ Searching web with Tavily...
→ Analyzing 20 sources...
→ Generating comprehensive report...
```

**Step 4: Papers Extracted**
```python
sources = [
    "https://arxiv.org/abs/1234.5678",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC...",
    ...
]
# Downloads PDFs, extracts text
papers = [PaperDocument(...), PaperDocument(...), ...]
```

**Step 5: Knowledge Extracted**
```python
# For each paper, Claude extracts:
{
    "title": "Effectiveness of ITS in Algebra",
    "year": 2023,
    "population": "High School (9th-12th)",
    "user_type": "Student",
    "study_design": "Randomized Control Trial",
    "implementation_objective": "Intelligent Tutoring and Instruction",
    "outcome": "Cognitive - Mathematical numeracy",
    "empirical_finding": {
        "direction": "Positive",
        "results_summary": "ITS improved algebra test scores by 0.3 SD...",
        "measure": "Standardized test scores",
        "study_size": 250,
        "effect_size": 0.3
    }
}
```

**Step 6: Added to Neo4j**
```cypher
// Paper node created
CREATE (p:Paper {
    paper_id: "paper_123",
    title: "Effectiveness of ITS in Algebra",
    session_id: "abc123...",
    added_date: "2025-12-08T10:32:00"
})

// Finding node created
CREATE (f:EmpiricalFinding {
    finding_id: "finding_123",
    direction: "Positive",
    results_summary: "ITS improved algebra...",
    ...
})

// Relationships created
CREATE (p)-[:TARGETS_POPULATION]->(:Population {type: "High School (9th-12th)"})
CREATE (p)-[:HAS_IMPLEMENTATION_OBJECTIVE]->(:ImplementationObjective {type: "Intelligent Tutoring..."})
CREATE (p)-[:FOCUSES_ON_OUTCOME]->(:Outcome {name: "Cognitive - Mathematical numeracy"})
CREATE (p)-[:REPORTS_FINDING]->(f)
...

// Derived relationship updated
MERGE (io:ImplementationObjective {type: "Intelligent Tutoring..."})-[r:TARGETS_OUTCOME]->(o:Outcome {name: "Cognitive - Mathematical numeracy"})
ON CREATE SET r.weight = 1
ON MATCH SET r.weight = r.weight + 1
```

**Step 7: Graph Retrieved**
```python
graph_data = {
    "nodes": [
        {"id": "p1", "label": "Paper", "properties": {...}},
        {"id": "o1", "label": "Outcome", "properties": {...}},
        ...
    ],
    "edges": [
        {"source": "p1", "target": "o1", "type": "FOCUSES_ON_OUTCOME"},
        ...
    ]
}
```

**Step 8: UI Display**
```
╔════════════════════════════════════════════════╗
║  Research Summary                               ║
╠════════════════════════════════════════════════╣
║                                                 ║
║  Intelligent Tutoring Systems (ITS) have       ║
║  shown positive effects on mathematics         ║
║  learning outcomes across multiple studies...  ║
║                                                 ║
║  ✅ 5 papers added to knowledge graph          ║
║                                                 ║
║  📊 View Knowledge Graph (click to expand) ▼   ║
║                                                 ║
╚════════════════════════════════════════════════╝
```

## Data Persistence

**After this query completes:**

✅ **Neo4j contains:**
- 1 Session node
- 5 Paper nodes (tagged with session_id)
- 5 EmpiricalFinding nodes
- Relationships to taxonomy nodes
- Updated ImplementationObjective→Outcome relationships

✅ **User can:**
- Ask follow-up questions (same session)
- Start new research chat (new session)
- View past sessions
- Visualize cumulative knowledge graph

✅ **Next time user runs a query:**
- Papers already in DB won't be duplicated (MERGE by title)
- New papers will be added
- Graph grows cumulatively
- Can see connections across research topics

## Performance Notes

- **Step 3** (Research): 2-5 minutes (Open Deep Research)
- **Step 4** (Paper fetch): 10-30 seconds (depending on source count)
- **Step 5** (KG extraction): 1-2 minutes (LLM calls, one per paper)
- **Step 6** (Neo4j update): <1 second (fast graph writes)
- **Total**: ~3-7 minutes per research query
