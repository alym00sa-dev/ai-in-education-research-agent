# Railway Streamlit Deployment - Fix Later

## Issue
The recent commit broke the Railway deployment of the Streamlit research agent backend.

## What Needs to Be Fixed

The Railway deployment is looking for the Streamlit app but finding the new API files instead.

## Solution Options

### Option 1: Update Railway Configuration (Easiest)
1. Go to Railway dashboard
2. Update the service settings:
   - **Root Directory:** Keep blank or set to root
   - **Start Command:** `streamlit run open_deep_research/app.py --server.port $PORT --server.address 0.0.0.0`
   - Or whatever the original command was

### Option 2: Add Railway-Specific Config File
Create `railway.toml` in project root:
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "streamlit run open_deep_research/app.py --server.port $PORT --server.address 0.0.0.0"
```

### Option 3: Use Separate Branch for Railway
- Create a `production-streamlit` branch
- Point Railway to that branch instead of `main`
- Keeps deployments independent

### Option 4: Check Railway Logs
The Railway dashboard logs will show exactly what error occurred and guide the fix.

## Environment Variables to Check
Make sure these are still set in Railway:
- NEO4J_URI
- NEO4J_USER
- NEO4J_PASSWORD
- NEO4J_DATABASE
- ANTHROPIC_API_KEY
- Any other Streamlit-specific variables

## Priority
Not urgent - fix after the visualization dashboard is deployed to Render/Vercel.

## Links
- Railway Dashboard: https://railway.app/dashboard
- GitHub Repo: https://github.com/alym00sa-dev/ai-in-education-research-agent
