# Connecting the Frontend to Open Deep Research

This guide explains how to connect your frontend dashboard to the Open Deep Research backend.

## Architecture Overview

```
Frontend (Port 80/443)
    ↓
Bridge Server (Port 8000) ← FastAPI adapter
    ↓
LangGraph Server (Port 2024) ← Open Deep Research backend
```

The bridge server (`bridge_server.py`) translates between:
- Frontend's custom API format (`/api/deep-research`)
- LangGraph's standard API format

## Step 1: Start the LangGraph Server

First, start the Open Deep Research backend:

```bash
cd /Users/alymoosa/Downloads/LangChain-Agent/open_deep_research

# Make sure your .env file has the required API keys:
# - OPENAI_API_KEY (required)
# - TAVILY_API_KEY (required)
# - ANTHROPIC_API_KEY (optional)
# - LANGSMITH_API_KEY (optional)

# Start the LangGraph server
uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.11 langgraph dev --allow-blocking
```

This will start the server at `http://127.0.0.1:2024`

You should see output like:
```
- 🚀 API: http://127.0.0.1:2024
- 🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- 📚 API Docs: http://127.0.0.1:2024/docs
```

## Step 2: Start the Bridge Server

In a **new terminal window**, start the bridge server:

```bash
cd /Users/alymoosa/Downloads/LangChain-Agent/open_deep_research

# Activate the same virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Start the bridge server
python bridge_server.py
```

The bridge server will start at `http://localhost:8000`

You should see:
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 3: Update the Frontend

Your frontend at `https://xd2164.github.io/AI-Market-Intelligence-Dashboard/deepresearch.html` needs to point to your local bridge server.

Since the frontend is hosted on GitHub Pages, you have two options:

### Option A: Download and Modify the Frontend (Recommended)

1. Download the frontend HTML file
2. Find the API endpoint configuration (likely something like `const API_URL = ...`)
3. Change it to point to `http://localhost:8000/api/deep-research`
4. Open the modified HTML file in your browser

### Option B: Use Browser Extension to Modify Requests

Use a browser extension like "ModHeader" or "Requestly" to redirect API calls from the original endpoint to `http://localhost:8000/api/deep-research`

### Option C: Host Frontend Locally

If you have the frontend source code:

```bash
# Serve the frontend locally (requires a simple HTTP server)
cd /path/to/frontend
python -m http.server 3000
```

Then access it at `http://localhost:3000/deepresearch.html`

## Step 4: Test the Connection

1. Open your frontend in a browser
2. Enter a research query (or use one of the preset buttons)
3. Click "Start Research"
4. You should see the research progress in both:
   - The frontend interface (loading state)
   - The bridge server logs (in the terminal)
   - The LangGraph server logs (in the other terminal)

## API Endpoints

### Bridge Server Endpoints

- `GET /` - Health check
- `POST /api/deep-research` - Main research endpoint

### Request Format (from frontend)

```json
{
  "query": "What are the latest trends in AI education?",
  "model_provider": "openai:gpt-4.1",
  "search_depth": "standard",
  "focus_area": "Educational Technology",
  "store_in_graph": false
}
```

### Response Format (to frontend)

```json
{
  "executive_summary": "Brief overview of findings...",
  "detailed_findings": "Comprehensive research results...",
  "key_insights": "Key takeaways and insights...",
  "sources": [
    {
      "title": "Source Title",
      "url": "https://example.com",
      "author": "Author Name",
      "publication": "Publication Name",
      "year": "2025"
    }
  ]
}
```

## Troubleshooting

### CORS Errors

If you see CORS errors in the browser console:
- The bridge server has CORS enabled for all origins (`allow_origins=["*"]`)
- For production, update this in `bridge_server.py` to specify your frontend's domain

### Connection Refused

If the bridge server can't connect to LangGraph:
- Make sure the LangGraph server is running on port 2024
- Check the `LANGGRAPH_URL` constant in `bridge_server.py`

### Timeout Errors

Research can take several minutes:
- The bridge server has a 10-minute timeout
- For longer research, increase the timeout in `bridge_server.py`:
  ```python
  async with httpx.AsyncClient(timeout=1200.0) as client:  # 20 minutes
  ```

### Model Not Found

If you see model-related errors:
- Check that your `.env` file has the correct API keys
- Verify the model name format: `provider:model-name` (e.g., `openai:gpt-4.1`)

## Configuration Options

### Search Depth Mapping

The bridge server maps frontend search depths to researcher iterations:
- `standard` → 4 iterations
- `deep` → 6 iterations
- `comprehensive` → 8 iterations

You can adjust these in `bridge_server.py` in the `deep_research` function.

### Model Provider Options

The frontend supports:
- `openai:gpt-4.1`
- `anthropic:claude-sonnet-4-20250514`
- Various OpenRouter models

Make sure you have the appropriate API keys in your `.env` file.

## Production Deployment

For production deployment:

1. **Deploy LangGraph to LangGraph Platform**
   - Follow the [LangGraph deployment guide](https://langchain-ai.github.io/langgraph/concepts/#deployment-options)
   - Update `LANGGRAPH_URL` in `bridge_server.py` to your deployed URL

2. **Deploy Bridge Server**
   - Deploy to a service like Render, Railway, or AWS
   - Update CORS settings to only allow your frontend domain
   - Add proper authentication/rate limiting

3. **Update Frontend**
   - Change API endpoint to your deployed bridge server URL
   - Deploy updated frontend

## Need Help?

- Check the bridge server logs for detailed error messages
- Check the LangGraph server logs for backend errors
- Visit the [Open Deep Research repository](https://github.com/langchain-ai/open_deep_research) for issues and documentation
