# Evidence Map Visualization - Deployment Guide

## 🎉 What We Built

A beautiful, interactive visualization dashboard with:

### ✅ **Backend (FastAPI)**
- **Location**: `research_assistant/api/`
- **Endpoints**:
  - `GET /api/v1/visualizations/level1` - Problem Burden Map data (12 outcome bubbles)
  - `GET /api/v1/visualizations/level2` - Intervention Evidence Map data (4 IO bubbles)
- **Features**:
  - Evidence maturity calculation (0-100 composite score)
  - Problem burden scale (1-4 weighted user types)
  - Complete breakdown data for click dialogues
  - Real-time data from Neo4j Aura

### ✅ **Frontend (Next.js + D3.js)**
- **Location**: `kg-viz-frontend/`
- **Features**:
  - Accordion navigation between Level 1 and Level 2
  - Interactive D3.js bubble charts
  - Click dialogues with detailed breakdowns
  - Responsive design
  - Clean, minimal UI with legends

---

## 🚀 Local Development

### Start Backend:
```bash
cd /Users/alymoosa/Documents/A-Moosa-Dev/LangChain-Agent/research_assistant/api
python -m uvicorn main:app --reload --port 8000
```
Access API docs: http://localhost:8000/docs

### Start Frontend:
```bash
cd /Users/alymoosa/Documents/A-Moosa-Dev/LangChain-Agent/kg-viz-frontend
npm run dev
```
Access visualization: http://localhost:3000

---

## 📦 Deployment to Vercel

### Step 1: Deploy Backend to Render

1. **Create Render Account**: https://render.com
2. **New Web Service**:
   - Repository: Connect your GitHub repo
   - Root Directory: `research_assistant/api`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. **Environment Variables**:
   ```
   NEO4J_URI=<your neo4j uri>
   NEO4J_USER=<your neo4j username>
   NEO4J_PASSWORD=<your neo4j password>
   NEO4J_DATABASE=neo4j
   ```
4. **Deploy** and copy the production URL (e.g., `https://your-api.onrender.com`)

### Step 2: Deploy Frontend to Vercel

1. **Create Vercel Account**: https://vercel.com
2. **Import Project**:
   - Connect GitHub repository
   - Root Directory: `kg-viz-frontend`
   - Framework Preset: Next.js (auto-detected)
3. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://your-api.onrender.com
   ```
4. **Deploy!**

### Step 3: Update CORS in Backend

After deploying frontend, update `research_assistant/api/config.py`:

```python
ALLOWED_ORIGINS: list = [
    "http://localhost:3000",
    "https://*.vercel.app",
    "https://your-actual-vercel-url.vercel.app"  # Add your production URL
]
```

Redeploy backend on Render.

---

## 🎨 What Users Will See

### Level 1: Problem Burden Map
- **12 bubbles** (one per outcome like "Cognitive - Mathematical numeracy")
- **X-axis**: Evidence Maturity (0-100) - how well-understood the problem is
- **Y-axis**: Problem Burden Scale (1-4) - localized to systemic impact
- **Bubble Size**: Effort required to shift the problem
- **Click**: Detailed breakdown with evidence components, user type distribution, effort components

### Level 2: Intervention Evidence Map
- **4 bubbles** (one per Implementation Objective like "Intelligent Tutoring")
- **X-axis**: Evidence Maturity (0-100) - quality of intervention evidence
- **Y-axis**: Potential Impact - alignment to high-burden problems
- **Bubble Size**: R&D investment required
- **Click**: Investment amount ($315M for Intelligent Tutoring), evidence breakdown, outcomes targeted

---

## 📊 Current Data

- **Total Papers**: 254 (247 enriched with 23 additional fields)
- **Level 1 Bubbles**: 12 outcomes
- **Level 2 Bubbles**: 4 implementation objectives
- **Data Source**: Neo4j Aura database

---

## 🔧 Troubleshooting

### Frontend can't reach backend:
- Check `NEXT_PUBLIC_API_URL` in `.env.local` (local) or Vercel dashboard (production)
- Verify CORS settings in backend `config.py`

### Bubbles not showing:
- Check browser console for errors
- Verify API endpoints return data: `curl http://localhost:8000/api/v1/visualizations/level1`

### TypeScript errors:
- Run `npm run build` to check for compilation errors
- Fix any type mismatches

---

## 🎯 Next Steps (Future Enhancements)

1. **Add Filters**: Region, study design, date range
2. **Export Features**: Download visualization as PNG/SVG
3. **Search**: Find specific outcomes or papers
4. **Zoom/Pan**: D3.js zoom behavior for large datasets
5. **Comparison Mode**: Side-by-side Level 1 vs Level 2

---

## 📁 Project Structure

```
research_assistant/
├── api/
│   ├── main.py                    # FastAPI app
│   ├── routers/
│   │   └── visualizations.py      # Visualization endpoints
│   ├── services/
│   │   └── visualization_service.py  # Data computation logic
│   └── models/
│       └── visualization.py       # Pydantic models

kg-viz-frontend/
├── app/
│   └── page.tsx                   # Main page with accordion
├── components/
│   ├── BubbleChart.tsx           # D3.js bubble chart
│   └── BubbleDialog.tsx          # Click dialogue modal
├── lib/
│   ├── api.ts                    # API client
│   └── types.ts                  # TypeScript types
└── .env.local                    # Environment variables
```

---

## ✨ Built With

- **Backend**: FastAPI, Python, Neo4j
- **Frontend**: Next.js 15, React, TypeScript, D3.js, Tailwind CSS, Radix UI
- **Database**: Neo4j Aura (247 enriched papers)
- **Deployment**: Render (API) + Vercel (Frontend)

---

🎊 **Congratulations! Your interactive evidence map is ready to visualize AI education research!**
