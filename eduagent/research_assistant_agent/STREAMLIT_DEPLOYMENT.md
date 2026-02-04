# Streamlit Cloud Deployment Guide

## Prerequisites

Before deploying, gather these credentials:

### 1. **Backend URL** (from Render)
- Your deployed backend URL from Render
- Example: `https://langgraph-backend.onrender.com`
- Test it first: `curl https://your-backend.onrender.com/ok`

### 2. **Neo4j Credentials** (your free Neo4j Aura)
- `NEO4J_URI` - Connection string (e.g., `neo4j+s://xxxxx.databases.neo4j.io`)
- `NEO4J_USER` - Username (usually `neo4j`)
- `NEO4J_PASSWORD` - Your password
- `NEO4J_DATABASE` - Database name (usually `neo4j`)

### 3. **API Keys**
- `OPENAI_API_KEY` - Your OpenAI API key
- `TAVILY_API_KEY` - Your Tavily API key

---

## Step 1: Push Code to GitHub

Make sure your code is pushed:

```bash
cd /Users/alymoosa/Documents/LangChain-Agent
git add .
git commit -m "Add Streamlit deployment configuration"
git push
```

---

## Step 2: Deploy to Streamlit Cloud

### 2.1 Sign Up
1. Go to https://share.streamlit.io
2. Sign in with GitHub (free, no credit card)

### 2.2 Create New App
1. Click "New app"
2. Select your repository
3. Configure:
   - **Branch:** `main`
   - **Main file path:** `research_assistant/app.py`
   - **App URL:** Choose a custom subdomain (e.g., `ai-research-assistant`)

### 2.3 Advanced Settings
Click "Advanced settings" and set:
- **Python version:** `3.11`
- **Root directory:** Leave blank (or set to `research_assistant` if issues)

---

## Step 3: Configure Secrets

In Streamlit Cloud app settings:

1. Click the **"⋮"** menu → **Settings**
2. Go to **Secrets** section
3. Add these secrets in TOML format:

```toml
# Neo4j Database
NEO4J_URI = "neo4j+s://xxxxx.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your_password_here"
NEO4J_DATABASE = "neo4j"

# Backend API
LANGGRAPH_API_URL = "https://your-app.onrender.com"

# API Keys
OPENAI_API_KEY = "sk-..."
TAVILY_API_KEY = "tvly-..."

# Optional: LangSmith
LANGSMITH_API_KEY = "lsv2_pt_..."
LANGSMITH_PROJECT = "your_project"
LANGSMITH_TRACING = "false"
```

4. Click **Save**

---

## Step 4: Deploy

1. Click **Deploy**
2. Wait 2-5 minutes for deployment
3. Watch the build logs for any errors

---

## Step 5: Test Your App

Once deployed:

1. **Health Check:**
   - Visit your app URL: `https://your-app.streamlit.app`
   - Should see the AI Research Assistant interface

2. **Test Research:**
   - Enter a simple query: "What is machine learning?"
   - Select search depth: "standard"
   - Click "Start Research"
   - Should see:
     - Research progress
     - Generated report
     - Knowledge graph visualization
     - Papers in Neo4j

3. **Check Backend Connection:**
   - If research fails, check:
     - Backend URL is correct in secrets
     - Backend is running on Render
     - API keys are valid

---

## Troubleshooting

### Build Fails

**Issue:** Missing dependencies
```
ModuleNotFoundError: No module named 'X'
```

**Fix:**
- Ensure `requirements.txt` is in `research_assistant/` directory
- Check Python version is 3.11

---

### Backend Connection Error

**Issue:** Cannot connect to backend
```
httpx.ConnectError: [Errno -2] Name or service not known
```

**Fix:**
1. Verify `LANGGRAPH_API_URL` in secrets
2. Test backend: `curl https://your-backend.onrender.com/ok`
3. Check Render backend is running (not sleeping)
4. First request after sleep takes ~30-60 seconds

---

### Neo4j Connection Error

**Issue:** Cannot connect to Neo4j
```
ServiceUnavailable: Failed to establish connection
```

**Fix:**
1. Verify Neo4j credentials in secrets
2. Check Neo4j Aura instance is running
3. Verify URI format: `neo4j+s://...` (with `+s` for secure)
4. Test connection from Neo4j Aura console

---

### App Crashes

**Issue:** App shows error page

**Fix:**
1. Check logs in Streamlit Cloud dashboard
2. Look for specific error messages
3. Common issues:
   - Missing environment variables
   - Invalid API keys
   - Neo4j connection timeout

---

## Monitoring & Maintenance

### View Logs
- Streamlit Cloud dashboard → Your app → **Logs** tab
- Check for errors and warnings

### Update App
- Push changes to GitHub
- Streamlit Cloud auto-deploys on push
- Or manually trigger: **Reboot app** in settings

### Usage Limits (Free Tier)
- **Resources:** 1 GB RAM, 1 CPU core
- **Uptime:** Unlimited
- **Users:** Unlimited
- **Apps:** Up to 3 private apps

---

## Going to Production

### Custom Domain
1. Upgrade to Streamlit Cloud Pro ($20/month)
2. Add custom domain in settings
3. Configure DNS records

### Scaling
If you need more resources:
- **Option A:** Upgrade Streamlit Cloud to Pro
- **Option B:** Deploy on your own server:
  ```bash
  streamlit run research_assistant/app.py --server.port 8501
  ```

---

## Security Notes

1. **Never commit secrets** to GitHub
2. **Use Streamlit secrets** for all credentials
3. **Rotate API keys** regularly
4. **Monitor usage** to prevent unexpected charges

---

## Next Steps

After deployment:
1. Share your app URL with users
2. Monitor usage and errors
3. Gather feedback
4. Iterate on features

---

## Support

- Streamlit Docs: https://docs.streamlit.io
- Community Forum: https://discuss.streamlit.io
- GitHub Issues: Your repository issues page
