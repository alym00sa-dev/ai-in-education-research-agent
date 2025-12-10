# Railway Deployment Guide - LangGraph Backend

## Prerequisites
- Railway account (https://railway.app)
- OpenAI API key
- Tavily API key

## Step 1: Create New Railway Project

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub repository
5. Select the `open_deep_research` directory as the root

## Step 2: Configure Environment Variables

In Railway dashboard, add these environment variables:

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

1. Railway will auto-detect the Dockerfile
2. Click "Deploy" button
3. Wait for build to complete (~5-10 minutes)
4. Railway will assign a public URL (e.g., `https://your-app.railway.app`)

## Step 4: Verify Deployment

Test your deployment:
```bash
curl https://your-app.railway.app/ok
```

You should see a health check response.

## Step 5: Get Your API Endpoint

Your LangGraph API endpoint will be:
```
https://your-app.railway.app
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
- Check Railway logs for errors
- Verify Dockerfile is in `open_deep_research/` directory
- Ensure all dependencies in `pyproject.toml` are correct

### Server won't start
- Check environment variables are set correctly
- Verify OpenAI API key is valid
- Check Railway logs for startup errors

### Connection timeout
- Increase healthcheck timeout in Railway settings
- LangGraph server needs ~30-60 seconds to start

## Monitoring

View logs in Railway dashboard:
1. Go to your project
2. Click on the deployment
3. View "Logs" tab for real-time logs

## Scaling

Railway free tier limits:
- 500 hours/month
- $5 free credit
- Sleeps after 30 minutes of inactivity

For production:
- Upgrade to Pro plan ($20/month)
- Enable auto-scaling
- Set up custom domain
