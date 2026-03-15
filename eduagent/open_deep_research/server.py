"""
Simple FastAPI server to host the LangGraph Deep Researcher.
For use in production without LangGraph Cloud.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import os
import sys
import json
import uuid

# Add src/ to path so bare imports (from configuration import ...) resolve correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.deep_researcher import deep_researcher
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

    Emits two SSE event types so the Streamlit client receives both live
    events (thoughts, tokens, node transitions) and the final state snapshot:

      event: events
      data: <LangGraph event object JSON>

      event: values
      data: <full graph state snapshot JSON>
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

        async def generate():
            try:
                async for mode, chunk in deep_researcher.astream(
                    state_input,
                    config={"configurable": configurable},
                    stream_mode=["values", "events"],
                ):
                    if mode == "values":
                        # Full state snapshot after each node — emit as SSE values event
                        try:
                            serialized = serialize_value(chunk)
                            yield f"event: values\ndata: {json.dumps(serialized)}\n\n"
                        except Exception:
                            pass
                    elif mode == "events":
                        # LangGraph event object (on_chain_start, on_tool_start, etc.)
                        try:
                            yield f"event: events\ndata: {json.dumps(chunk)}\n\n"
                        except (TypeError, ValueError):
                            # Fallback: serialize LangChain objects and retry
                            try:
                                yield f"event: events\ndata: {json.dumps(serialize_value(chunk))}\n\n"
                            except Exception:
                                pass

                # Send end signal
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

        async def generate():
            try:
                async for mode, chunk in deep_researcher.astream(
                    state_input,
                    config={"configurable": configurable},
                    stream_mode=["values", "events"],
                ):
                    if mode == "values":
                        try:
                            serialized = serialize_value(chunk)
                            yield f"event: values\ndata: {json.dumps(serialized)}\n\n"
                        except Exception:
                            pass
                    elif mode == "events":
                        try:
                            yield f"event: events\ndata: {json.dumps(chunk)}\n\n"
                        except (TypeError, ValueError):
                            try:
                                yield f"event: events\ndata: {json.dumps(serialize_value(chunk))}\n\n"
                            except Exception:
                                pass
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
