"""FastAPI bridge server to connect the frontend to Open Deep Research LangGraph backend.

This server provides a REST API endpoint that matches the frontend's expected format
and communicates with the LangGraph server running on port 2024.
"""

import re
from typing import List, Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class Source(BaseModel):
    """Source citation model."""
    title: str
    url: str
    author: Optional[str] = ""
    publication: Optional[str] = ""
    year: Optional[str] = ""


class ResearchRequest(BaseModel):
    """Request model matching the frontend format."""
    query: str
    model_provider: str = "openai:gpt-4.1"
    search_depth: str = "standard"
    focus_area: Optional[str] = None
    store_in_graph: bool = False


class ResearchResponse(BaseModel):
    """Response model matching the frontend format."""
    executive_summary: str
    detailed_findings: str
    key_insights: str
    sources: List[Source]


app = FastAPI(
    title="Deep Research Bridge API",
    description="Bridge API connecting the frontend to Open Deep Research LangGraph backend",
    version="1.0.0"
)

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LangGraph server configuration
LANGGRAPH_URL = "http://127.0.0.1:2024"
ASSISTANT_ID = "Deep Researcher"  # From langgraph.json


def extract_sources_from_report(report: str) -> List[Source]:
    """Extract source citations from the research report.

    Looks for URLs and tries to extract source information.
    """
    sources = []

    # Find URLs in the report
    url_pattern = r'https?://[^\s\)"\]>]+'
    urls = re.findall(url_pattern, report)

    # Create source objects from URLs
    seen_urls = set()
    for url in urls:
        if url not in seen_urls:
            seen_urls.add(url)
            # Try to extract title from surrounding text
            title = url.split('//')[-1].split('/')[0]  # Use domain as fallback title
            sources.append(Source(
                title=title,
                url=url,
                author="",
                publication="",
                year=""
            ))

    return sources[:10]  # Limit to 10 sources


def parse_report_sections(report: str) -> dict:
    """Parse the research report into structured sections.

    Attempts to identify executive summary, detailed findings, and key insights
    from the generated report.
    """
    # Default structure
    result = {
        "executive_summary": "",
        "detailed_findings": "",
        "key_insights": ""
    }

    # Split report into sections based on common markdown headers
    lines = report.split('\n')
    current_section = None
    section_content = []

    for line in lines:
        # Check for section headers
        lower_line = line.lower().strip()

        if any(keyword in lower_line for keyword in ['executive summary', 'summary', 'overview']):
            if current_section and section_content:
                result[current_section] = '\n'.join(section_content).strip()
            current_section = 'executive_summary'
            section_content = []
        elif any(keyword in lower_line for keyword in ['detailed findings', 'findings', 'analysis', 'research findings']):
            if current_section and section_content:
                result[current_section] = '\n'.join(section_content).strip()
            current_section = 'detailed_findings'
            section_content = []
        elif any(keyword in lower_line for keyword in ['key insights', 'insights', 'key takeaways', 'conclusions']):
            if current_section and section_content:
                result[current_section] = '\n'.join(section_content).strip()
            current_section = 'key_insights'
            section_content = []
        elif current_section:
            section_content.append(line)

    # Add the last section
    if current_section and section_content:
        result[current_section] = '\n'.join(section_content).strip()

    # If sections weren't identified, create them from the full report
    if not result['executive_summary'] and not result['detailed_findings']:
        # Use first paragraph as executive summary
        paragraphs = [p.strip() for p in report.split('\n\n') if p.strip()]
        if paragraphs:
            result['executive_summary'] = paragraphs[0]
            result['detailed_findings'] = '\n\n'.join(paragraphs[1:]) if len(paragraphs) > 1 else report
            # Extract last paragraph or section as key insights
            if len(paragraphs) > 2:
                result['key_insights'] = paragraphs[-1]

    return result


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "Deep Research Bridge API",
        "langgraph_url": LANGGRAPH_URL
    }


@app.post("/api/deep-research", response_model=ResearchResponse)
async def deep_research(request: ResearchRequest):
    """
    Conduct deep research using the Open Deep Research backend.

    This endpoint receives a research query from the frontend, forwards it to
    the LangGraph server, and transforms the response into the expected format.
    """
    try:
        async with httpx.AsyncClient(timeout=600.0) as client:  # 10 minute timeout for long research
            # Step 1: Create a thread
            thread_response = await client.post(
                f"{LANGGRAPH_URL}/threads",
                json={}
            )
            thread_response.raise_for_status()
            thread = thread_response.json()
            thread_id = thread["thread_id"]

            # Step 2: Prepare the request for LangGraph API
            langgraph_payload = {
                "assistant_id": ASSISTANT_ID,
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": request.query
                        }
                    ]
                },
                "config": {
                    "configurable": {
                        "research_model": request.model_provider,
                        # Map search depth to researcher iterations
                        "max_researcher_iterations": {
                            "standard": 4,
                            "deep": 6,
                            "comprehensive": 8
                        }.get(request.search_depth, 6)
                    }
                },
                "stream_mode": "values"
            }

            # Step 3: Call the LangGraph API with streaming
            response = await client.post(
                f"{LANGGRAPH_URL}/threads/{thread_id}/runs/stream",
                json=langgraph_payload
            )
            response.raise_for_status()

            # Parse the streaming response to get the final state
            final_state = None
            for line in response.text.strip().split('\n'):
                if line.startswith('data: '):
                    import json
                    data = json.loads(line[6:])  # Remove 'data: ' prefix
                    if data:
                        final_state = data

            if not final_state:
                raise HTTPException(status_code=500, detail="No response from LangGraph server")

            # Extract the final report from the state
            final_report = final_state.get('final_report', '')

            if not final_report:
                # Try to get the last AI message if final_report is not available
                messages = final_state.get('messages', [])
                for msg in reversed(messages):
                    if isinstance(msg, dict) and msg.get('type') == 'ai':
                        final_report = msg.get('content', '')
                        break

            # Parse the report into sections
            sections = parse_report_sections(final_report)

            # Extract sources from the report
            sources = extract_sources_from_report(final_report)

            # Return the structured response
            return ResearchResponse(
                executive_summary=sections['executive_summary'] or "Research completed. See detailed findings below.",
                detailed_findings=sections['detailed_findings'] or final_report,
                key_insights=sections['key_insights'] or "Key insights are included in the detailed findings.",
                sources=sources
            )

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Research request timed out")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Could not connect to LangGraph server: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing research request: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
