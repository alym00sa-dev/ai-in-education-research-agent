# EDU Agent - AI Education Research Assistant

## Overview

**EDU Agent** is an intelligent research assistant designed specifically for education research. It combines deep research capabilities with a specialized knowledge graph to help analyze education interventions, research evidence, and learning outcomes.

The agent automates literature review, evidence synthesis, and gap analysis for AI-enabled educational interventions. It maintains a structured knowledge base of research papers, connects them to implementation objectives and outcomes, and provides evidence-based insights for decision-making.

---

## Core Capabilities

### 🔍 Deep Research
- Automated literature search and extraction
- Multi-source research aggregation
- Evidence quality assessment
- Citation tracking and synthesis

### 📊 Evidence Mapping
- Evidence gap analysis (Implementation Objectives × Outcomes)
- Research maturity scoring
- Intervention effectiveness tracking
- Study design classification

### 🧠 Knowledge Graph
- Neo4j-powered semantic network
- Papers linked to:
  - Implementation Objectives (e.g., "Intelligent Tutoring and Instruction")
  - Learning Outcomes (e.g., "Mathematical numeracy", "Reading literacy")
  - Populations (e.g., "K-12", "Undergraduate")
  - Study Designs (e.g., "RCT", "Quasi-Experimental")
  - Empirical Findings (effect sizes, directions, measures)

### 📈 Data Integration
- What Works Clearinghouse (WWC) corpus integration
- 600+ education intervention studies
- Standardized effect size calculations
- Quality ratings and study metadata

---

## System Architecture

```
EDU Agent System
│
├── open_deep_research/              # Deep Research Agent
│   ├── Core research pipeline
│   ├── Multi-source extraction
│   ├── Literature synthesis
│   └── Automated search & retrieval
│
├── research_assistant_agent/        # Knowledge & Data Management
│   ├── src/                         # Core Logic
│   │   ├── neo4j_config.py         # Database connection
│   │   ├── kg_extractor.py         # Knowledge graph extraction
│   │   ├── evidence_map.py         # Evidence gap mapping
│   │   ├── research_pipeline.py    # Research orchestration
│   │   └── session_manager.py      # Session handling
│   │
│   ├── app.py                       # Streamlit Interface
│   │
│   ├── Data Processing              # WWC Integration
│   │   ├── import_wwc_to_neo4j.py  # Import WWC data
│   │   ├── process_wwc_data.py     # Process datasets
│   │   ├── map_wwc_to_ios.py       # Map to objectives
│   │   └── wwc_*.json              # WWC data files
│   │
│   └── Database Management
│       ├── init_database.py        # Initialize Neo4j
│       ├── migrate_schema.py       # Schema migrations
│       └── test_neo4j.py           # Connection testing
│
└── Neo4j Database                   # Knowledge Graph Storage
    ├── Papers (2000+ nodes)
    ├── Implementation Objectives (4 types)
    ├── Outcomes (12 categories)
    ├── Populations, Study Designs
    └── Empirical Findings
```

---

## Current Setup

### Technology Stack

**Agent Core:**
- Python 3.9+
- Anthropic Claude API (research synthesis)
- Streamlit (user interface)

**Knowledge Graph:**
- Neo4j Database (v5.x)
- Graph data model with semantic relationships
- Cypher query language

**Data Sources:**
- What Works Clearinghouse (WWC)
- Custom research corpus
- Academic paper databases

### Database Schema

**Node Types:**
- `Paper` - Research papers and studies
- `ImplementationObjective` - AI intervention categories (4 types)
- `Outcome` - Learning outcomes (12 categories)
- `Population` - Student populations
- `StudyDesign` - Research methodologies
- `EmpiricalFinding` - Study results and effect sizes
- `Session` - Research sessions
- `UserType` - Target user groups

**Relationship Types:**
- `HAS_IMPLEMENTATION_OBJECTIVE`
- `FOCUSES_ON_OUTCOME`
- `TARGETS_POPULATION`
- `USES_STUDY_DESIGN`
- `REPORTS_FINDING`
- `HAS_SYNTHESIS` (cached AI summaries)

### Implementation Objectives (4 Categories)

1. **Intelligent Tutoring and Instruction**
   - Adaptive learning systems
   - AI tutors and assistants
   - Personalized instruction

2. **AI-Enabled Personalized Advising**
   - Student guidance systems
   - Career counseling
   - Academic planning

3. **Institutional Decision-making**
   - Predictive analytics
   - Resource allocation
   - Policy support

4. **AI-Enabled Learner Mobility**
   - Credential recognition
   - Pathway optimization
   - Transfer support

### Learning Outcomes (12 Categories)

**Cognitive Outcomes:**
- Mathematical numeracy
- Reading and writing literacy
- STEM proficiency
- Critical thinking/Metacognitive skills
- Language learning

**Affective/Behavioral Outcomes:**
- Engagement
- Motivation/Self-efficacy
- Persistence/Completion

**Systemic Outcomes:**
- Access and equity
- Cost-effectiveness
- Teacher/Instructor capacity
- Institutional effectiveness

---

## Data Coverage

### Current Knowledge Base

- **2,000+** research papers
- **600+** WWC intervention studies
- **238** papers on Intelligent Tutoring (non-WWC)
- **40** WWC-validated adaptive instruction interventions
- **152** classified studies across evidence ladder rungs

### Evidence Distribution

**By Study Design:**
- Meta-Analysis/Systematic Review: 86 papers
- Quasi-Experimental Design: 58 papers
- Randomized Control Trial: 37 papers
- Mixed-Methods Study: 18 papers
- Qualitative Study: 11 papers

**By Evidence Maturity:**
- Rung 1 (Monitoring): 57 studies
- Rung 2 (Implementation): 0 studies
- Rung 3 (Comparative): 58 studies
- Rung 4 (Causal Effectiveness): 37 studies
- Rung 5 (Generalizability): 0 studies
- Rung 6 (Personalized): 0 studies

---

## Use Cases

### 1. Evidence Gap Analysis
**Goal:** Identify where research is needed

**How it works:**
- Query papers by Implementation Objective × Outcome
- Generate evidence gap matrix (4×12 = 48 cells)
- AI synthesizes findings and identifies gaps
- Cached results for fast retrieval

**Example:** "Show me evidence for AI tutoring's impact on reading literacy"

### 2. Intervention Effectiveness
**Goal:** Understand what works in education

**How it works:**
- Filter by intervention type (e.g., "Intelligent Tutoring")
- Analyze effect sizes over time
- Track student impact (sample sizes, populations)
- Compare across use cases (math tutoring, feedback, etc.)

**Example:** "How effective is real-time feedback for K-12 math?"

### 3. Research Landscape Mapping
**Goal:** Understand current state of evidence

**How it works:**
- Classify studies into evidence ladder (6 rungs)
- Show distribution from monitoring → personalized effectiveness
- Identify research maturity levels
- Highlight replication gaps

**Example:** "Where is the evidence strongest for AI tutoring?"

### 4. Deep Literature Review
**Goal:** Comprehensive research synthesis

**How it works:**
- Automated search across multiple sources
- Extract key findings and metadata
- Synthesize into coherent narrative
- Link to knowledge graph

**Example:** "Do a deep dive on adaptive learning systems"

---

## Getting Started

### Prerequisites

1. **Neo4j Database**
   ```bash
   # Install Neo4j Desktop or use Neo4j Cloud
   # Create database with credentials
   ```

2. **Python Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

3. **API Keys**
   ```bash
   # Create .env file
   ANTHROPIC_API_KEY=your_key_here
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your_password
   ```

### Initialize Database

```bash
cd research_assistant_agent

# Test connection
python test_neo4j.py

# Initialize schema
python init_database.py

# Import WWC data (optional)
python import_wwc_to_neo4j.py
```

### Run the Agent

**Option 1: Streamlit Interface**
```bash
streamlit run app.py
```

**Option 2: Python API**
```python
from src.evidence_map import get_evidence_map_data
from src.kg_extractor import KGExtractor

# Get evidence gap matrix
df = get_evidence_map_data()

# Extract from a paper
extractor = KGExtractor()
result = extractor.extract_from_url(paper_url)
```

---

## Folder Structure

### open_deep_research/
Deep research agent with multi-source retrieval and synthesis capabilities.

**Key Files:**
- Research pipeline orchestration
- Source integration (academic databases, web)
- Extraction and synthesis logic

### research_assistant_agent/
Core knowledge management and data processing.

**Key Directories:**
- `src/` - Core agent logic
- `database/enrichment/` - Data enrichment scripts
- `.streamlit/` - Streamlit configuration

**Key Files:**
- `app.py` - Main Streamlit interface
- `import_wwc_to_neo4j.py` - WWC data import
- `process_wwc_data.py` - WWC data processing
- `map_wwc_to_ios.py` - Map WWC to objectives
- `wwc_*.json` - WWC datasets

**Documentation:**
- `README.md` - Main documentation
- `SCHEMA.md` - Database schema
- `PIPELINE.md` - Research pipeline
- `QUICKSTART.md` - Quick start guide
- `IMPROVEMENTS.md` - Enhancement notes

---

## Configuration

### Environment Variables (.env)

```bash
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-...

# Neo4j Connection
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# Optional: Neo4j Cloud
# NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
```

### Neo4j Configuration

**Recommended Settings:**
- Memory: 4GB+ heap size
- Indexes: Automatic on Paper.title, Paper.url
- Constraints: Unique on Paper.url

---

## Maintenance

### Adding New Papers

```python
from src.kg_extractor import KGExtractor

extractor = KGExtractor()
extractor.extract_from_url("https://paper-url.com")
```

### Updating Schema

```bash
python migrate_schema.py
```

### Backing Up Data

```bash
# Neo4j dump
neo4j-admin dump --database=neo4j --to=backup.dump

# Export JSON
python -c "from src.evidence_map import get_evidence_map_data; \
           get_evidence_map_data().to_json('evidence_backup.json')"
```

---

## Future Enhancements

### Planned Features
- [ ] Automated weekly literature scans
- [ ] Multi-language paper support
- [ ] Citation network analysis
- [ ] Intervention recommendation engine
- [ ] Longitudinal effectiveness tracking
- [ ] Custom evidence quality frameworks

### Research Gaps Being Addressed
- More multi-site RCT studies (Rung 5)
- Personalized effectiveness studies (Rung 6)
- Implementation fidelity studies (Rung 2)
- Long-term outcome tracking
- Equity and access research

---

## Support & Documentation

### Key Documentation Files
- `README.md` - Main overview
- `SCHEMA.md` - Database schema details
- `PIPELINE.md` - Research pipeline documentation
- `QUICKSTART.md` - Setup and usage guide
- `SEPARATION_README.md` - Module separation guide

### Troubleshooting

**Neo4j Connection Issues:**
```bash
python test_neo4j.py
# Check URI, username, password in .env
```

**Import Errors:**
```bash
pip install -r requirements.txt --upgrade
```

**Memory Issues:**
- Increase Neo4j heap size in neo4j.conf
- Process WWC data in batches

---

## Contact & Attribution

**Project:** AI Education Research Assistant (EDU Agent)
**Purpose:** Evidence-based decision support for AI in education
**Data Sources:** What Works Clearinghouse, academic literature
**Technology:** Neo4j, Claude AI, Python, Streamlit

---

## Version History

- **v2.0** - Module separation (agent + viz independent)
- **v1.5** - P1Current evidence ladder visualization
- **v1.4** - WWC intervention mapping (40 interventions)
- **v1.3** - Evidence gap matrix with AI synthesis
- **v1.2** - Deep research integration
- **v1.1** - Neo4j knowledge graph foundation
- **v1.0** - Initial research assistant prototype

---

## License & Usage

This agent is designed for education research analysis and evidence synthesis. The WWC data is publicly available and used under their terms of service. AI-generated syntheses should be reviewed by domain experts before use in decision-making.
