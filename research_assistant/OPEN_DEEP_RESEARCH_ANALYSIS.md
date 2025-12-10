# Open Deep Research: Comprehensive Analysis

## Overview

Open Deep Research is a configurable, fully open-source deep research agent built on LangGraph. It orchestrates multiple LLM agents to conduct comprehensive research across various sources and generate detailed reports.

---

## High-Level Architecture

### 4-Phase Research Workflow

The agent operates in four distinct phases:

1. **Clarification Phase**
   - Takes user's research question
   - Supervisor agent analyzes the query
   - Generates clarifying questions if needed
   - Produces a refined, focused research objective

2. **Research Brief Phase**
   - Creates a structured research plan
   - Defines key subtopics to investigate
   - Sets search strategies
   - Establishes evaluation criteria

3. **Parallel Research Phase**
   - Spawns multiple researcher agents
   - Each researcher investigates specific subtopics
   - Concurrent execution for speed
   - Gathers evidence from multiple sources
   - Iterative refinement based on findings

4. **Final Report Phase**
   - Aggregates all research findings
   - Synthesizes information into coherent narrative
   - Generates comprehensive report with citations
   - Includes methodology and confidence ratings

---

## Technical Implementation

### Core Components

**File**: `src/open_deep_research/deep_researcher.py`

This is the main entry point defining the LangGraph workflow.

#### Agent Hierarchy

```
Supervisor Agent (Orchestrator)
    ├── Clarifier Agent
    ├── Brief Writer Agent
    └── Researcher Agents (Parallel)
        ├── Researcher 1 (Subtopic A)
        ├── Researcher 2 (Subtopic B)
        └── Researcher N (Subtopic N)
```

#### State Management

**File**: `src/open_deep_research/state.py`

The system uses a shared state object that flows through the graph:

```python
@dataclass
class ResearchState:
    messages: List[Message]
    research_question: str
    clarifications: List[str]
    research_brief: str
    raw_notes: List[str]
    final_report: str
    sources: List[Source]
    # ... other fields
```

Key state transitions:
- `messages` → Communication between agents
- `research_question` → Refined query
- `research_brief` → Research plan
- `raw_notes` → Individual researcher findings
- `final_report` → Synthesized output

#### Prompts System

**File**: `src/open_deep_research/prompts.py`

Contains system prompts for each agent:
- `CLARIFIER_PROMPT` - Guides question refinement
- `BRIEF_WRITER_PROMPT` - Structures research plan
- `RESEARCHER_PROMPT` - Directs evidence gathering
- `REPORT_WRITER_PROMPT` - Formats final output

These prompts are the **easiest customization point** for changing agent behavior.

---

## Configurability

### What You Can Change

#### 1. Model Providers

**File**: `src/open_deep_research/configuration.py`

Supports multiple LLM providers:
- OpenAI (GPT-4, GPT-4o, GPT-4.1)
- Anthropic (Claude Sonnet, Opus)
- Google (Gemini models)
- Groq (Llama models)
- DeepSeek

**How to change**:
```python
# Via configuration
config = {
    "configurable": {
        "research_model": "anthropic:claude-sonnet-4-20250514",
        "supervisor_model": "openai:gpt-4o"
    }
}
```

Or via environment variables in `.env`:
```bash
RESEARCH_MODEL=anthropic:claude-sonnet-4-20250514
```

#### 2. Search APIs

Multiple search providers supported:
- **Tavily** (default, best for comprehensive search)
- **OpenAI/Anthropic native search** (model-integrated)
- **DuckDuckGo** (free, no API key needed)
- **Exa** (semantic search)

**How to change**:
```python
config = {
    "configurable": {
        "search_api": "tavily",  # or "duckduckgo", "exa"
    }
}
```

#### 3. Research Depth

Controls thoroughness vs speed:

```python
config = {
    "configurable": {
        "max_researcher_iterations": 6,  # Higher = more thorough
        "max_research_time": 300,  # Seconds
    }
}
```

Typical mappings:
- Standard: 4 iterations (~3-5 min)
- Deep: 6 iterations (~5-7 min)
- Comprehensive: 8 iterations (~7-10 min)

#### 4. Concurrency

Control parallel researcher agents:

```python
config = {
    "configurable": {
        "max_concurrent_researchers": 3,  # Number of parallel researchers
    }
}
```

#### 5. MCP (Model Context Protocol) Tools

**File**: `langgraph.json`

Add custom tools and servers:

```json
{
  "tools": {
    "arxiv_search": "mcp",
    "pubmed_search": "mcp",
    "custom_tool": "mcp"
  },
  "mcp_servers": {
    "arxiv": {
      "command": "uvx",
      "args": ["mcp-server-arxiv"]
    }
  }
}
```

This extends the agent's capabilities with domain-specific search.

---

## What's Prepackaged vs Customizable

### Prepackaged (Core Framework)

These are **stable components** you shouldn't need to change:

1. **LangGraph orchestration logic** (`deep_researcher.py`)
   - State transitions
   - Agent coordination
   - Parallel execution

2. **State schema** (`state.py`)
   - Data structures
   - Message passing

3. **Utility functions** (`utils.py`)
   - Helper methods
   - Common operations

### Highly Customizable

These are **designed for modification**:

1. **Prompts** (`prompts.py`)
   - **Easiest to customize**
   - Change agent instructions
   - Modify output format
   - Add domain expertise

2. **Configuration** (`configuration.py`)
   - Model selection
   - Search provider
   - Research parameters

3. **Tools and MCP servers** (`langgraph.json`)
   - Add new search sources
   - Integrate APIs
   - Custom data access

---

## Extension Points

### 1. Custom Prompts

**Example**: Add domain expertise for education research

```python
# In prompts.py
EDUCATION_RESEARCHER_PROMPT = """
You are an expert in educational technology research.
Focus on:
- Empirical studies with effect sizes
- Controlled vocabulary from AI in Education taxonomy
- Population types (K-12, Higher Ed, etc.)
...
"""
```

### 2. Custom Tools

Add specialized search:

```python
# Create new MCP server for education databases
{
  "mcp_servers": {
    "eric_database": {
      "command": "uvx",
      "args": ["mcp-server-eric"]
    }
  }
}
```

### 3. Custom Post-Processing

After research completes:

```python
# In your research pipeline
results = await pipeline.conduct_research(query)
research_report = results["final_report"]

# Custom extraction
structured_data = extract_education_metadata(research_report)
save_to_neo4j(structured_data)
```

This is **exactly what you're doing** in `research_assistant/src/research_pipeline.py`.

### 4. Graph Modifications

Add new nodes to workflow:

```python
# In deep_researcher.py
workflow.add_node("custom_validator", validate_research)
workflow.add_edge("research", "custom_validator")
workflow.add_edge("custom_validator", "report")
```

---

## Integration Patterns

### Pattern 1: API Client (Your Current Approach)

```python
async with httpx.AsyncClient() as client:
    response = await client.post(
        f"{langgraph_url}/threads/{thread_id}/runs/stream",
        json=payload
    )
```

**Pros**:
- Clean separation
- Easy to deploy separately
- Version independence

**Cons**:
- Network overhead
- Requires server running

### Pattern 2: Direct Library Import

```python
from open_deep_research.deep_researcher import deep_researcher

# Compile graph
app = deep_researcher.compile()

# Run directly
result = await app.ainvoke({
    "messages": [{"role": "user", "content": query}]
})
```

**Pros**:
- No network calls
- Easier debugging
- Tighter integration

**Cons**:
- Dependency management
- Version coupling

---

## Key Strengths

1. **Multi-source research**
   - Aggregates information from many sources
   - Parallel processing for speed
   - Iterative refinement

2. **Configurable models**
   - Not locked to single provider
   - Can mix models (cheap supervisor, expensive researchers)
   - Easy to test different approaches

3. **MCP extensibility**
   - Add domain-specific tools
   - Custom search sources
   - API integrations

4. **Open source**
   - Full code visibility
   - Can modify anything
   - No vendor lock-in

---

## Limitations & Trade-offs

1. **Cost**
   - Multiple LLM calls per research query
   - Deep research = expensive
   - Mitigation: Use cheaper models for some agents

2. **Speed**
   - Even with parallelization, takes 3-10 minutes
   - Trade-off between thoroughness and latency
   - Mitigation: Adjust iteration limits

3. **Source quality**
   - Dependent on search API results
   - May miss specialized databases
   - Mitigation: Add domain-specific MCP tools

4. **Hallucination risk**
   - LLMs can still make up facts
   - Report quality varies by model
   - Mitigation: Use high-quality models, verify citations

---

## Best Practices for Customization

### 1. Start with Prompts

Before changing code, try modifying prompts:

```python
# Add specificity
CUSTOM_PROMPT = f"""
{RESEARCHER_PROMPT}

ADDITIONAL INSTRUCTIONS:
- Only cite peer-reviewed sources
- Include effect sizes when available
- Use controlled vocabulary: {POPULATIONS}
"""
```

### 2. Use Configuration First

Leverage existing config system:

```python
# Don't hard-code
research_model = "gpt-4o"  # Bad

# Use configuration
config = {
    "configurable": {
        "research_model": os.getenv("RESEARCH_MODEL", "gpt-4o")
    }
}
```

### 3. Add Custom Post-Processing

Instead of modifying the agent, process outputs:

```python
# Let agent do research
results = await conduct_research(query)

# Custom extraction
structured = extract_with_schema(results["final_report"])
validate_with_taxonomy(structured)
save_to_graph(structured)
```

### 4. Test Incrementally

When customizing:
1. Test with original implementation
2. Change one thing at a time
3. Compare outputs
4. Iterate

---

## Your Implementation Strategy

Your `research_assistant` system demonstrates an excellent integration pattern:

1. **Use Open Deep Research as-is** for research
2. **Custom post-processing** for structured extraction
3. **Neo4j integration** for knowledge graph
4. **Streamlit frontend** for user interface

This approach:
- Keeps Open Deep Research modular
- Adds domain-specific functionality
- Maintains upgradeability
- Clear separation of concerns

---

## Recommended Next Steps

### Immediate

1. **Fix extraction** - Get Claude Sonnet 4 working for controlled vocabulary matching
2. **Verify graph edges** - Ensure taxonomies connect properly
3. **Test end-to-end** - Complete workflow with real queries

### Short-term

1. **Custom prompts** - Add education-specific instructions to researcher agents
2. **Add ERIC tool** - MCP server for education research database
3. **Optimize costs** - Use cheaper models for supervisor/clarifier

### Long-term

1. **Add validators** - Custom node to verify taxonomy matching
2. **Citation tracking** - Link papers to specific claims in report
3. **Confidence scoring** - Rate quality of evidence for each finding

---

## Configuration Reference

### Environment Variables

```bash
# Models
RESEARCH_MODEL=anthropic:claude-sonnet-4-20250514
SUPERVISOR_MODEL=openai:gpt-4o

# Search
SEARCH_API=tavily
TAVILY_API_KEY=tvly-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx

# Neo4j
NEO4J_URI=neo4j+s://xxx.databases.neo4j.io
NEO4J_PASSWORD=xxx

# LangGraph
LANGGRAPH_API_URL=http://127.0.0.1:2024
```

### Runtime Configuration

```python
config = {
    "configurable": {
        # Model selection
        "research_model": "anthropic:claude-sonnet-4-20250514",
        "supervisor_model": "openai:gpt-4o",

        # Search configuration
        "search_api": "tavily",

        # Research depth
        "max_researcher_iterations": 6,
        "max_research_time": 300,

        # Concurrency
        "max_concurrent_researchers": 3,

        # Output
        "output_format": "markdown",
        "include_sources": True
    }
}
```

---

## Conclusion

Open Deep Research is a **highly configurable** system with clear extension points:

- **Easy changes**: Prompts, configuration, post-processing
- **Medium changes**: Adding MCP tools, custom validators
- **Advanced changes**: Graph structure modifications

The system is designed to be **extended rather than modified**. Your current integration approach is excellent - use it as a research engine and add your domain-specific logic around it.

**Key takeaway**: You don't need to change the core agent. Instead, customize prompts, add MCP tools, and process outputs with your own extraction logic.
