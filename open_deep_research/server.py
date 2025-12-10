"""
Simple FastAPI server to host the LangGraph Deep Researcher.
For use in production without LangGraph Cloud.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import os
import json
import uuid
from src.open_deep_research.deep_researcher import deep_researcher
from langchain_core.messages import BaseMessage

def serialize_value(obj):
    """Convert LangChain objects to JSON-serializable format."""
    if isinstance(obj, BaseMessage):
        return {
            "type": obj.__class__.__name__,
            "content": obj.content,
            "additional_kwargs": obj.additional_kwargs,
        }
    elif isinstance(obj, dict):
        return {k: serialize_value(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_value(item) for item in obj]
    else:
        return obj

app = FastAPI(title="LangGraph Deep Researcher API")

# In-memory thread storage (for stateless deployment)
threads = {}

class ResearchRequest(BaseModel):
    """Request model for research queries."""
    assistant_id: str = "Deep Researcher"
    input: Dict[str, Any]
    config: Optional[Dict[str, Any]] = None
    stream_mode: str = "values"

class Message(BaseModel):
    """Message model."""
    role: str
    content: str

@app.get("/ok")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "LangGraph Deep Researcher API",
        "status": "running",
        "version": "1.0.0"
    }

@app.post("/threads")
async def create_thread(request: Optional[Dict[str, Any]] = None):
    """
    Create a new thread for conversation tracking.
    Compatible with LangGraph API format.
    """
    thread_id = str(uuid.uuid4())
    threads[thread_id] = {
        "thread_id": thread_id,
        "created_at": None,
        "metadata": request or {}
    }
    return {
        "thread_id": thread_id,
        "created_at": None,
        "metadata": {}
    }

@app.post("/threads/{thread_id}/runs/stream")
async def run_thread_stream(thread_id: str, request: Dict[str, Any]):
    """
    Stream research results for a thread.
    Compatible with LangGraph API format.
    """
    try:
        # Extract query from messages
        messages = request.get("input", {}).get("messages", [])
        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")

        query = messages[0].get("content", "")
        if not query:
            raise HTTPException(status_code=400, detail="Empty query")

        # Get config
        config = request.get("config", {})
        configurable = config.get("configurable", {})

        # Create state input
        state_input = {"messages": [{"role": "user", "content": query}]}

        # Stream results
        async def generate():
            try:
                async for chunk in deep_researcher.astream(
                    state_input,
                    config={"configurable": configurable}
                ):
                    # Serialize LangChain objects to JSON
                    serialized_chunk = serialize_value(chunk)

                    # Format as server-sent events
                    event_data = {
                        "event": "values",
                        "data": serialized_chunk
                    }
                    yield f"data: {json.dumps(event_data)}\n\n"

                # Send end signal
                yield "data: [DONE]\n\n"
            except Exception as e:
                error_event = {
                    "event": "error",
                    "data": {"error": str(e)}
                }
                yield f"data: {json.dumps(error_event)}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/runs/stream")
async def run_research_stream(request: ResearchRequest):
    """
    Stream research results.
    Compatible with LangGraph API format.
    """
    try:
        # Extract query from messages
        messages = request.input.get("messages", [])
        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")

        query = messages[0].get("content", "")
        if not query:
            raise HTTPException(status_code=400, detail="Empty query")

        # Get config
        config = request.config or {}
        configurable = config.get("configurable", {})

        # Create state input
        state_input = {"messages": [{"role": "user", "content": query}]}

        # Stream results
        async def generate():
            try:
                async for chunk in deep_researcher.astream(
                    state_input,
                    config={"configurable": configurable}
                ):
                    # Serialize LangChain objects to JSON
                    serialized_chunk = serialize_value(chunk)
                    yield f"data: {json.dumps(serialized_chunk)}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                error_data = {"error": str(e)}
                yield f"data: {json.dumps(error_data)}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/assistants/{assistant_id}/invoke")
async def invoke_research(assistant_id: str, request: Dict[str, Any]):
    """
    Invoke research synchronously.
    Returns complete result.
    """
    try:
        # Extract query
        messages = request.get("input", {}).get("messages", [])
        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")

        query = messages[0].get("content", "")
        config = request.get("config", {})
        configurable = config.get("configurable", {})

        # Run research
        state_input = {"messages": [{"role": "user", "content": query}]}
        result = await deep_researcher.ainvoke(
            state_input,
            config={"configurable": configurable}
        )

        # Serialize result
        serialized_result = serialize_value(result)
        return {"result": serialized_result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/assistants/search")
async def list_assistants():
    """List available assistants."""
    return {
        "assistants": [
            {
                "assistant_id": "Deep Researcher",
                "name": "Deep Researcher",
                "description": "Autonomous research agent for comprehensive analysis"
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
