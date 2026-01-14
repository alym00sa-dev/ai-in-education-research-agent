# Deployment Guide - AI Education Research Evidence Map

This guide walks you through deploying the visualization dashboard to production.

## Architecture Overview

```
┌─────────────────────────┐
│  Vercel (Frontend)      │  ← Next.js App
│  https://*.vercel.app   │
└────────┬────────────────┘
         │ API Calls
         ▼
┌─────────────────────────┐
│  Render (Backend)       │  ← FastAPI
│  https://*.onrender.com │
└────────┬────────────────┘
         │ Bolt Protocol
         ▼
┌─────────────────────────┐
│  Neo4j Aura (Database)  │  ← Already running
│  *.databases.neo4j.io   │
└─────────────────────────┘
```

---

## Prerequisites

- [x] GitHub account
- [x] GitHub repository: `https://github.com/alym00sa-dev/ai-in-education-research-agent.git`
- [x] Vercel account (sign up at https://vercel.com)
- [x] Render account (sign up at https://render.com)
- [x] Neo4j Aura credentials (you already have these)

---

## Part 1: Deploy FastAPI Backend to Render

### Step 1: Push Latest Code to GitHub

```bash
cd /Users/alymoosa/Documents/A-Moosa-Dev/LangChain-Agent
git add .
git commit -m "Add deployment configuration files"
git push origin main
```

### Step 2: Create New Web Service on Render

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository:
   - Select: `alym00sa-dev/ai-in-education-research-agent`
4. Configure the service:

   **Basic Settings:**
   - Name: `ai-education-api`
   - Region: `Oregon (US West)` or closest to you
   - Branch: `main`
   - Root Directory: `research_assistant`
   - Runtime: `Python 3`

   **Build & Deploy:**
   - Build Command: `pip install -r api/requirements.txt`
   - Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

   **Plan:**
   - Select **Free** tier (or paid for better performance)

5. Click **"Advanced"** and add environment variables:

   ```
   NEO4J_URI          = neo4j+s://your-instance.databases.neo4j.io
   NEO4J_USER         = neo4j
   NEO4J_PASSWORD     = your-password
   NEO4J_DATABASE     = neo4j
   ANTHROPIC_API_KEY  = your-anthropic-key (optional, for synthesis)
   PYTHON_VERSION     = 3.11
   ```

6. Click **"Create Web Service"**

### Step 3: Wait for Deployment

- First deploy takes 2-5 minutes
- Watch the logs for any errors
- Once deployed, you'll get a URL like: `https://ai-education-api.onrender.com`

### Step 4: Test Backend

```bash
# Test health endpoint
curl https://ai-education-api.onrender.com/api/health

# Should return:
# {"status":"healthy","neo4j_connected":true,"version":"1.0.0"}

# Test Level 1 data
curl https://ai-education-api.onrender.com/api/v1/visualizations/level1
```

**✅ Backend is now deployed!** Copy your Render URL for the next step.

---

## Part 2: Deploy Next.js Frontend to Vercel

### Step 1: Push Frontend Code

If not already pushed:

```bash
cd /Users/alymoosa/Documents/A-Moosa-Dev/LangChain-Agent
git add kg-viz-frontend/
git commit -m "Prepare frontend for Vercel deployment"
git push origin main
```

### Step 2: Import Project to Vercel

1. Go to https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository:
   - Select: `alym00sa-dev/ai-in-education-research-agent`
4. Configure the project:

   **Framework Preset:** Next.js (should auto-detect)

   **Root Directory:**
   - Click "Edit" next to Root Directory
   - Select: `kg-viz-frontend`

   **Build Settings:** (leave defaults)
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`

5. **Environment Variables** - Add these:

   ```
   NEXT_PUBLIC_API_URL = https://ai-education-api.onrender.com
   ```

   ⚠️ Replace with YOUR actual Render URL from Part 1!

6. Click **"Deploy"**

### Step 3: Wait for Deployment

- First deploy takes 1-3 minutes
- Vercel will automatically build and deploy
- You'll get a URL like: `https://your-project-name.vercel.app`

### Step 4: Test Frontend

1. Visit your Vercel URL
2. You should see the intro page
3. Try navigating to Level 1 and Level 2
4. Click on bubbles to see details
5. Test filters

**✅ Frontend is now deployed!**

---

## Part 3: Update CORS (if needed)

If you see CORS errors in the browser console:

### Option A: Update via Render Dashboard

1. Go to Render dashboard → Your service
2. Click **"Environment"**
3. Add a new environment variable:
   ```
   ALLOWED_ORIGINS = https://your-vercel-url.vercel.app
   ```
4. Save (will trigger redeploy)

### Option B: Update in Code

1. Edit `research_assistant/api/config.py`:
   ```python
   ALLOWED_ORIGINS: list = [
       "http://localhost:3000",
       "https://your-vercel-url.vercel.app",  # Add your Vercel URL
       "https://*.vercel.app",
   ]
   ```
2. Commit and push:
   ```bash
   git add research_assistant/api/config.py
   git commit -m "Update CORS for production"
   git push origin main
   ```
3. Render will auto-deploy the changes

---

## Part 4: Custom Domain (Optional)

### For Frontend (Vercel)

1. Go to Vercel project → **"Settings"** → **"Domains"**
2. Add your custom domain (e.g., `evidence-map.yourdomain.com`)
3. Follow DNS configuration instructions
4. Vercel will automatically provision SSL certificate

### For Backend (Render)

1. Go to Render service → **"Settings"** → **"Custom Domain"**
2. Add your custom domain (e.g., `api.yourdomain.com`)
3. Update DNS records as instructed
4. SSL is automatic

---

## Troubleshooting

### Backend Issues

**Problem:** "Module not found" error
```
Solution: Check that rootDir in render.yaml is set to "research_assistant"
```

**Problem:** Neo4j connection error
```
Solution:
1. Check environment variables are set correctly
2. Verify Neo4j URI format: neo4j+s://xxxxx.databases.neo4j.io
3. Check Neo4j Aura is not paused
```

**Problem:** Port binding error
```
Solution: Make sure start command uses $PORT variable:
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

### Frontend Issues

**Problem:** "Failed to fetch" or CORS errors
```
Solution:
1. Check NEXT_PUBLIC_API_URL is set correctly
2. Must start with https:// (not http://)
3. No trailing slash
4. Update CORS in backend config
```

**Problem:** Blank page or 404
```
Solution:
1. Check Root Directory is set to "kg-viz-frontend"
2. Verify build completed successfully in deployment logs
```

**Problem:** Environment variables not updating
```
Solution:
1. Redeploy after changing environment variables
2. Or use Vercel CLI: vercel env pull
```

---

## Deployment Commands Reference

### Render (Backend)

```bash
# View logs
render logs -f

# Trigger manual deploy
render deploy

# Check service status
render ps
```

### Vercel (Frontend)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy manually
cd kg-viz-frontend
vercel --prod

# View logs
vercel logs

# Pull environment variables
vercel env pull
```

---

## Environment Variables Checklist

### Backend (Render)
- [x] NEO4J_URI
- [x] NEO4J_USER
- [x] NEO4J_PASSWORD
- [x] NEO4J_DATABASE
- [x] ANTHROPIC_API_KEY (optional)
- [x] PYTHON_VERSION

### Frontend (Vercel)
- [x] NEXT_PUBLIC_API_URL

---

## Post-Deployment

### Monitor Performance

**Render:**
- Dashboard shows CPU/Memory usage
- View logs for errors
- Free tier sleeps after 15 min inactivity (first request takes 30s)

**Vercel:**
- Analytics dashboard shows page views
- Function logs show API errors
- Free tier has bandwidth limits

### Update Deployment

**For Backend Changes:**
```bash
git add research_assistant/api/
git commit -m "Update backend"
git push origin main
# Render auto-deploys
```

**For Frontend Changes:**
```bash
git add kg-viz-frontend/
git commit -m "Update frontend"
git push origin main
# Vercel auto-deploys
```

---

## URLs After Deployment

Once deployed, save these URLs:

```
Frontend:  https://your-project.vercel.app
Backend:   https://ai-education-api.onrender.com
API Docs:  https://ai-education-api.onrender.com/docs
Health:    https://ai-education-api.onrender.com/api/health
```

---

## Cost Estimates

### Free Tier Limits

**Render (Free):**
- ✅ 750 hours/month
- ⚠️ Sleeps after 15 min inactivity
- ⚠️ 512 MB RAM
- ⚠️ Shared CPU

**Vercel (Hobby - Free):**
- ✅ Unlimited deployments
- ✅ 100 GB bandwidth/month
- ✅ No sleep time
- ⚠️ 100 GB-hours serverless execution

### Paid Options

**Render Starter ($7/month):**
- No sleep
- 512 MB RAM
- Faster builds

**Vercel Pro ($20/month):**
- 1 TB bandwidth
- Team collaboration
- Better analytics

---

## Security Checklist

- [x] Use environment variables for secrets (never commit .env)
- [x] Enable HTTPS only (both platforms do this automatically)
- [x] Configure CORS properly (restrict to your domains)
- [x] Keep dependencies updated
- [x] Use Neo4j Aura (managed, secure)

---

## Next Steps

1. ✅ Deploy backend to Render
2. ✅ Deploy frontend to Vercel
3. ✅ Test full functionality
4. Optional: Set up custom domains
5. Optional: Configure monitoring/alerts
6. Optional: Set up staging environment

---

## Support

- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- Next.js Docs: https://nextjs.org/docs

Need help? Check the deployment logs first - they usually show the exact error.
