# EDU Viz - AI Education Research Visualization Dashboard

## Overview

**EDU Viz** is an interactive visualization dashboard for exploring education research evidence. It provides a comprehensive visual interface for analyzing research landscapes, tracking intervention effectiveness, and identifying evidence gaps in AI-enabled education.

The system transforms complex research data from a Neo4j knowledge graph into intuitive, interactive visualizations that support evidence-based decision-making for education technology investments and policy.

---

## Core Capabilities

### 📊 Evidence Landscape Mapping
- **Bubble charts** showing research distribution across implementation objectives and outcomes
- **Priority matrices** combining evidence maturity with problem burden
- **Interactive filtering** by priority levels and categories

### 📈 Time Series Analysis
- **Effect size evolution** tracking intervention effectiveness over time
- **Student impact tracking** showing cumulative research reach
- **Geographic distribution** of research across U.S. states
- **Demographic breakdowns** by learner type and institution

### 🪜 Evidence Ladder Visualization
- **Six-rung framework** from monitoring to personalized effectiveness
- **Study classification** by research design and methodology
- **Gap identification** showing where more research is needed
- **Use case breakdown** showing evidence by intervention type

### 💰 Investment Analysis
- **Gates Foundation overlap** with WWC research concentration
- **State-level investment** mapping against research density
- **ROI visualization** for education technology interventions

---

## System Architecture

```
EDU Viz System
│
├── kg-viz-frontend/                 # Next.js Dashboard
│   ├── app/                         # Main application
│   │   └── page.tsx                # Dashboard UI
│   ├── components/                  # Visualization components
│   │   ├── BubbleChart.tsx         # Evidence matrices
│   │   ├── LineChart.tsx           # Time series
│   │   ├── P1EffectSizeEvolution.tsx      # Effect size charts
│   │   ├── P1CurrentEvidenceLadder.tsx    # Evidence ladder
│   │   ├── P1CurrentByUseCase.tsx         # Multi-ladder view
│   │   ├── GeographicDistribution.tsx     # State maps
│   │   └── GatesInvestmentMap.tsx         # Investment overlay
│   ├── lib/                         # Utilities
│   │   ├── api.ts                  # Backend API client
│   │   └── types.ts                # TypeScript definitions
│   └── public/                      # Static assets
│
└── research_assistant_viz/          # FastAPI Backend
    ├── api/                         # API application
    │   ├── main.py                 # API entry point
    │   ├── routers/                # Endpoints
    │   │   ├── visualizations.py  # Viz endpoints
    │   │   ├── evidence_map.py    # Evidence gap endpoints
    │   │   ├── taxonomy.py        # Taxonomy endpoints
    │   │   └── sessions.py        # Session endpoints
    │   ├── services/               # Business logic
    │   │   ├── visualization_service.py    # Data generation
    │   │   ├── evidence_map_service.py     # Evidence mapping
    │   │   └── session_service.py          # Sessions
    │   └── models/                 # Pydantic models
    │       ├── visualization.py    # Response models
    │       └── evidence_map.py     # Evidence models
    └── src/                        # Shared dependencies
        └── neo4j_config.py         # Database connection
```

---

## Visualization Layers

### Level 1: Problem Burden Map
**Purpose:** Identify high-priority learning challenges

**Shows:**
- 12 outcome categories (bubbles)
- X-axis: Evidence maturity (0-100)
- Y-axis: Problem burden scale
- Bubble size: Investment/effort required
- Color: Priority level (high priority, on watch, research gap)

**Use Case:** "What are the biggest problems with the most mature evidence?"

---

### Level 2: Intervention Evidence Map
**Purpose:** Evaluate intervention readiness across objectives

**Shows:**
- 4 implementation objectives (bubbles)
- X-axis: Evidence maturity
- Y-axis: Potential impact
- Bubble size: Investment required
- Color: Priority level

**Use Case:** "Which AI interventions have the strongest evidence?"

---

### Level 3: Evidence-Based Interventions (WWC)
**Purpose:** Focus on interventions meeting WWC quality standards

**Shows:**
- Same as Level 2 but filtered to RCT-only evidence
- 4 implementation objectives with stricter quality bar
- Highlights gold-standard research

**Use Case:** "What interventions have rigorous RCT evidence?"

---

### Level 5: Evidence Evolution Over Time
**Purpose:** Track how research evidence has accumulated

**Shows:**
- Time series (1995-2025)
- Y-axis: Generalizability score
- Bubble size: New students studied per period
- Multiple lines per implementation objective

**Use Case:** "How has evidence for AI tutoring grown over time?"

---

### P1: Effect Size Evolution Over Time
**Purpose:** Track intervention effectiveness across years

**Shows:**
- 20 WWC interventions in Adaptive Instruction & Tutoring
- X-axis: Year
- Y-axis: Effect size (WWC standardized)
- Bubble size: Students studied
- Bubble color: Finding direction (favorable/unfavorable)
- Two views: By intervention or by use case

**Use Cases:**
- "How effective is math tutoring over time?"
- "Do real-time feedback systems show stable effects?"

---

### P1 Current: Evidence Ladder
**Purpose:** Show current research landscape maturity

**Shows:**
- 238 non-WWC papers on Intelligent Tutoring
- 6 rungs: Monitoring → Implementation → Comparative → Causal → Generalizability → Personalized
- Two views: Overall ladder or by use case (5 parallel ladders)

**Use Cases:**
- "Where is the evidence strongest?"
- "What research gaps exist at higher rungs?"

---

### P5: Delivery Pillar Distribution
**Purpose:** Geographic and demographic research coverage

**Shows:**
- U.S. state-level distribution
- Student counts by state
- Demographic breakdowns (FRPL, ELL, IEP, Minority)
- Institution types (Public, Charter, Private)
- Grade levels (PreK, K-5, 6-8, 9-12)
- Time slider to see evolution

**Use Cases:**
- "Which states have the most research?"
- "Are we studying diverse student populations?"

---

### Gates Investment Overlap
**Purpose:** Compare foundation investments with research concentration

**Shows:**
- State-level Gates Foundation investments (pre-LLM)
- WWC study concentration by state
- Overlay showing alignment/misalignment
- $200M+ in mapped investments

**Use Case:** "Where did Gates invest vs. where research happened?"

---

## Technology Stack

### Frontend (kg-viz-frontend)
- **Framework:** Next.js 14 (React)
- **Language:** TypeScript
- **Visualization:** D3.js
- **Styling:** Tailwind CSS
- **Icons:** Lucide React

### Backend (research_assistant_viz)
- **Framework:** FastAPI (Python)
- **Database:** Neo4j (via Cypher queries)
- **Data Models:** Pydantic
- **CORS:** Enabled for frontend access

### Data Layer
- **Neo4j Knowledge Graph:** 2000+ research papers
- **WWC Dataset:** 600+ intervention studies
- **Gates Investment Data:** Foundation grant records

---

## Current Data Coverage

### Research Papers
- **2,238** total papers in knowledge graph
- **600+** WWC intervention studies
- **238** non-WWC papers on Intelligent Tutoring
- **40** adaptive instruction interventions (WWC)
- **152** papers classified across evidence ladder

### Evidence Distribution
**By Study Design:**
- Meta-Analysis/Systematic Review: 86
- Quasi-Experimental Design: 58
- Randomized Control Trial: 37
- Mixed-Methods: 18
- Qualitative: 11

**By Evidence Ladder Rung:**
- Rung 1 (Monitoring): 57 papers
- Rung 2 (Implementation): 0 papers
- Rung 3 (Comparative): 58 papers
- Rung 4 (Causal Effectiveness): 37 papers
- Rung 5 (Generalizability): 0 papers
- Rung 6 (Personalized): 0 papers

### Geographic Coverage
- **All 50 U.S. states** represented
- **~50,000** students across WWC studies
- **Major concentration:** CA, TX, FL, NY

---

## Getting Started

### Prerequisites

1. **Neo4j Database** (running with data loaded)
   - URI: `bolt://localhost:7687` or cloud instance
   - Credentials configured

2. **Node.js 18+** for frontend

3. **Python 3.9+** for backend

---

### Setup Backend API

```bash
cd research_assistant_viz

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
cd api
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with Neo4j credentials

# Run API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**API will be available at:** `http://localhost:8000`
**API Docs:** `http://localhost:8000/docs`

---

### Setup Frontend Dashboard

```bash
cd kg-viz-frontend

# Install dependencies
npm install

# Configure environment (optional)
# Create .env.local if using custom API URL
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev
```

**Dashboard will be available at:** `http://localhost:3000`

---

## API Endpoints

### Visualization Endpoints

**Level Visualizations:**
- `GET /api/v1/visualizations/level1` - Problem Burden Map
- `GET /api/v1/visualizations/level2` - Intervention Evidence Map
- `GET /api/v1/visualizations/level3` - Evidence-Based Interventions
- `GET /api/v1/visualizations/level5` - Evidence Evolution Over Time

**Pillar Visualizations:**
- `GET /api/v1/visualizations/p1` - Effect Size Evolution
- `GET /api/v1/visualizations/p5` - Delivery Pillar Distribution
- `GET /api/v1/visualizations/p1-current/{io}` - Evidence Ladder (overall)
- `GET /api/v1/visualizations/p1-current-by-usecase/{io}` - Evidence Ladder (by use case)
- `GET /api/v1/visualizations/gates-investment-overlap` - Investment Analysis

**Evidence Map:**
- `GET /api/v1/evidence-map/matrix` - Full evidence matrix
- `GET /api/v1/evidence-map/cell/{io}/{outcome}` - Cell details
- `GET /api/v1/evidence-map/cell/{io}/{outcome}/synthesis` - AI synthesis

**Taxonomy:**
- `GET /api/v1/taxonomy/implementation-objectives` - List IOs
- `GET /api/v1/taxonomy/outcomes` - List outcomes
- `GET /api/v1/taxonomy/study-designs` - List study designs

**Health:**
- `GET /api/health` - Health check
- `GET /api/v1/stats` - Database statistics

---

## Visualization Features

### Interactive Elements
- **Hover tooltips** - Detailed info on hover
- **Click interactions** - Drill down into details
- **Filtering** - Hide/show by priority or category
- **Time sliders** - Explore temporal changes
- **View toggles** - Switch between perspectives
- **Legends** - Color/size guides

### Right Sidebar Details
When clicking visualizations:
- **Breakdown panels** - Detailed metrics
- **Strategic insights** - Contextual analysis
- **Evidence gaps** - Research opportunities
- **Paper lists** - Access to source studies

---

## Use Cases

### 1. Strategic Investment Planning
**Scenario:** Foundation deciding where to invest in education technology

**Workflow:**
1. View **Level 1** to identify high-burden problems
2. Check **Level 2** for intervention evidence maturity
3. Examine **P1 Effect Size** to see what works
4. Review **Gates Investment** overlay to see historical patterns
5. Check **P1 Current** to identify research gaps

---

### 2. Intervention Selection
**Scenario:** District evaluating tutoring programs

**Workflow:**
1. View **P1 Effect Size** filtered by "Math Tutoring" use case
2. Examine effect size trends over time
3. Check student impact (bubble sizes)
4. Review study findings in detail panel
5. Compare to other use cases

---

### 3. Research Gap Analysis
**Scenario:** Researcher identifying study opportunities

**Workflow:**
1. View **Evidence Map Matrix** to see all 48 cells
2. Click cells with low paper counts
3. Review AI-generated gap analysis
4. Check **P1 Current Evidence Ladder** for rung gaps
5. Identify underrepresented populations in **P5**

---

### 4. Equity Analysis
**Scenario:** Ensuring diverse student representation

**Workflow:**
1. View **P5 Delivery** visualization
2. Check demographic distribution (FRPL, ELL, IEP)
3. Compare across states
4. Identify underrepresented groups
5. Cross-reference with **Level 1** problem burden

---

## Configuration

### Backend (.env in research_assistant_viz/api/)

```bash
# Neo4j Connection
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# API Configuration
API_TITLE=AI Education Research API
API_VERSION=1.0.0
ALLOWED_ORIGINS=["http://localhost:3000"]
```

### Frontend (.env.local in kg-viz-frontend/)

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Deployment

### Backend (API)

**Option 1: Render.com**
- Use `research_assistant_viz/api/render.yaml`
- Connect to Neo4j Cloud

**Option 2: Docker**
```bash
cd research_assistant_viz/api
docker build -t eduviz-api .
docker run -p 8000:8000 eduviz-api
```

### Frontend (Dashboard)

**Option 1: Vercel**
```bash
cd kg-viz-frontend
vercel deploy
```

**Option 2: Static Export**
```bash
npm run build
npm run export
# Deploy dist/ folder to any static host
```

---

## Maintenance

### Updating Data
When new papers are added to Neo4j:
1. Restart backend API (data is queried live)
2. Frontend automatically fetches updated data
3. No rebuild needed

### Adding New Visualizations
1. Add endpoint to `research_assistant_viz/api/routers/visualizations.py`
2. Add service logic to `research_assistant_viz/api/services/visualization_service.py`
3. Add Pydantic model to `research_assistant_viz/api/models/visualization.py`
4. Add TypeScript types to `kg-viz-frontend/lib/types.ts`
5. Add API function to `kg-viz-frontend/lib/api.ts`
6. Create component in `kg-viz-frontend/components/`
7. Integrate into `kg-viz-frontend/app/page.tsx`

---

## Troubleshooting

### Backend Issues

**API won't start:**
```bash
# Check Neo4j connection
cd research_assistant_viz
python -c "from src.neo4j_config import get_neo4j_connection; get_neo4j_connection()"

# Check dependencies
pip install -r api/requirements.txt --upgrade
```

**Endpoints returning errors:**
- Check logs: `tail -f /tmp/backend.log`
- Verify Neo4j has data: `GET /api/v1/stats`
- Test health: `GET /api/health`

### Frontend Issues

**Frontend won't start:**
```bash
# Clear cache and reinstall
rm -rf node_modules .next
npm install
npm run dev
```

**Data not loading:**
- Check API is running: `curl http://localhost:8000/api/health`
- Check browser console for CORS errors
- Verify `NEXT_PUBLIC_API_URL` in .env.local

**Visualizations not rendering:**
- Check browser console for D3 errors
- Verify data shape matches TypeScript types
- Clear browser cache

---

## Future Enhancements

### Planned Visualizations
- [ ] Network graph of citation connections
- [ ] Sankey diagram of research pathways
- [ ] Heatmap of outcome correlations
- [ ] Timeline of intervention emergence
- [ ] Cost-effectiveness scatter plots

### Planned Features
- [ ] Export visualizations as PNG/SVG
- [ ] Custom date range filtering
- [ ] Saved view configurations
- [ ] Collaborative annotations
- [ ] Real-time data updates
- [ ] Mobile responsive design

---

## Support & Documentation

### Key Files
- `kg-viz-frontend/README.md` - Frontend setup
- `research_assistant_viz/README.md` - Backend setup
- `research_assistant_viz/api/README.md` - API documentation
- `SEPARATION_GUIDE.md` - Module separation details

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

## Architecture Notes

### Why Separated from Agent?
- **Agent** focuses on research acquisition and knowledge graph population
- **Viz** focuses on presenting existing knowledge graph data
- **Separation benefits:**
  - Independent deployment
  - Different scaling needs
  - Clear boundaries
  - Agent can be moved elsewhere while viz stays

### Data Flow
```
Neo4j Database
      ↓
research_assistant_viz API (FastAPI)
      ↓ (REST endpoints)
kg-viz-frontend Dashboard (Next.js)
      ↓
User's Browser
```

### Shared Dependencies
- Both agent and viz use same Neo4j database
- Same data model and schema
- No direct communication between agent and viz
- Communication happens via shared database

---

## Contact & Attribution

**Project:** AI Education Research Visualization Dashboard (EDU Viz)
**Purpose:** Evidence-based visualization for education research decision-making
**Data Sources:** Neo4j knowledge graph (2000+ papers, 600+ WWC studies)
**Technology:** Next.js, FastAPI, D3.js, Neo4j

---

## Version History

- **v2.0** - Module separation (agent/viz independent), P1 Current Evidence Ladder
- **v1.5** - Gates Investment overlay, P1 Effect Size Evolution
- **v1.4** - P5 Delivery Pillar visualizations
- **v1.3** - Level 5 time series, evidence evolution
- **v1.2** - Interactive filtering and detail panels
- **v1.1** - Levels 1-3 bubble charts
- **v1.0** - Initial dashboard prototype

---

## License & Usage

This visualization system is designed for education research analysis and evidence communication. The underlying data comes from publicly available sources (WWC) and proprietary knowledge graph. Visualizations should be interpreted by domain experts and used to inform, not replace, human decision-making in education policy and investment.
