# Render Deployment Guide - LangGraph Backend (Free Tier)

## Prerequisites
- Render account (https://render.com) - FREE, no credit card required
- OpenAI API key
- Tavily API key
- GitHub repository with your code

## Step 1: Create New Render Web Service

1. Go to https://render.com and sign up (free)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select your repository
5. Configure:
   - **Name:** langgraph-backend
   - **Root Directory:** `open_deep_research`
   - **Environment:** Docker
   - **Plan:** Free

## Step 2: Configure Environment Variables

In Render dashboard, add these environment variables:

### Required Variables:
```
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### Optional Variables (for monitoring):
```
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=your_project_name
LANGSMITH_TRACING=true
```

### Optional Variables (for other models - not needed since using GPT-4.1):
```
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
```

## Step 3: Deploy

1. Render will auto-detect the Dockerfile
2. Click "Create Web Service" button
3. Wait for build to complete (~5-10 minutes)
4. Render will assign a public URL (e.g., `https://langgraph-backend.onrender.com`)

## Step 4: Verify Deployment

Test your deployment:
```bash
curl https://langgraph-backend.onrender.com/ok
```

You should see a health check response.

⚠️ **Note:** Free tier services sleep after 15 minutes of inactivity. First request after sleep takes ~30-60 seconds to wake up.

## Step 5: Get Your API Endpoint

Your LangGraph API endpoint will be:
```
https://langgraph-backend.onrender.com
```

This is what you'll use in your Streamlit frontend to connect to the backend.

## API Endpoints

Once deployed, your backend exposes these endpoints:

- `GET /ok` - Health check
- `POST /runs/stream` - Stream research results
- `GET /assistants/search` - List available assistants
- `POST /assistants/{assistant_id}/invoke` - Invoke research assistant

## Troubleshooting

### Build fails
- Check Render logs for errors
- Verify Dockerfile is in `open_deep_research/` directory
- Ensure all dependencies in `pyproject.toml` are correct

### Server won't start
- Check environment variables are set correctly
- Verify OpenAI API key is valid
- Check Render logs for startup errors

### Connection timeout
- Free tier sleeps after 15 min - first request takes ~30-60s to wake
- LangGraph server needs ~30-60 seconds to start

### "Service Unavailable" error
- Service is probably sleeping - wait 30-60 seconds and retry

## Monitoring

View logs in Render dashboard:
1. Go to your service
2. Click "Logs" tab for real-time logs
3. Monitor health checks

## Render Free Tier Limits

**What you get:**
- 750 hours/month (enough for 24/7 uptime for 1 service)
- Free SSL certificates
- Auto-deploy from GitHub
- Sleeps after 15 minutes of inactivity

**Limitations:**
- 512 MB RAM
- 0.1 CPU (shared)
- Services spin down after 15 min idle
- Spin-up time: ~30-60 seconds

**For production:**
- Upgrade to paid plan ($7/month)
- No sleep on inactivity
- More resources (512MB+ RAM)
- Custom domains included
