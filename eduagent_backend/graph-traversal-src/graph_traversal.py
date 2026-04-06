"""Graph Traversal Chat — conversational interface over the Neo4j KG corpus.

Single-node LangGraph graph. Multi-turn conversation handled via LangGraph threads.
Each user message:
  1. LLM generates a Cypher query from the full schema + few-shot examples
  2. Execute query against Neo4j
  3. LLM synthesizes a prose response from the results

Graph name: "graph_traversal" (registered in langgraph.json)
"""

import logging
import os
import sys

# Allow imports from deep-research-src (configuration, etc.)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "deep-research-src"))

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import MessagesState
from pydantic import BaseModel, Field

log = logging.getLogger(__name__)

_CYPHER_MODEL = "openai:gpt-4.1"       # strong model for Cypher generation
_DEFAULT_MODEL = "openai:gpt-4.1-mini"  # fallback synthesis model


# ── State ─────────────────────────────────────────────────────────────────────

class GraphChatState(MessagesState):
    session_id: str = ""
    last_cypher: str = ""
    last_result_count: int = 0


# ── Cypher generation ─────────────────────────────────────────────────────────

class CypherQuery(BaseModel):
    cypher: str = Field(description="The Cypher query to execute against Neo4j")
    description: str = Field(description="One sentence describing what this query retrieves")


_SCHEMA = """
## Neo4j Schema

### Nodes
- (p:Paper) — title, year, doi, url, venue, source_db,
    study_design, quality_tier (blue/green/yellow/red),
    impact_tier, populations (list of grade/group strings),
    extended_summary, limitations (list), duration_weeks,
    setting, teacher_training, implementation_fidelity,
    study_country, study_region,
    eta (CCM citation fitness score, float),
    cluster_id, field_momentum, is_sleeping_beauty, sb_coef

- (i:Intervention) — name, intervention_id, description, is_ai_powered (bool)

- (f:EmpiricalFinding) — finding_id, outcome_category, finding_type,
    direction (Positive/Negative/No Effect/Mixed),
    finding_summary, measure, effect_size, sample_size,
    confidence_interval, study_count, source_paper

- (o:Outcome) — name (one of the outcome categories below)

### Relationships (all that exist with meaningful data)
- (p:Paper)-[:EVALUATES]->(i:Intervention)          — paper studies this tool
- (i:Intervention)-[:PRODUCES_FINDING]->(f:EmpiricalFinding)
- (p:Paper)-[:REPORTS_FINDING]->(f:EmpiricalFinding) — direct paper→finding link
- (f:EmpiricalFinding)-[:TARGETS_OUTCOME]->(o:Outcome)
- (p:Paper)-[:FOCUSES_ON_OUTCOME]->(o:Outcome)      — direct paper→outcome link
- (p:Paper)-[:CITES]->(p2:Paper)                    — corpus-to-corpus only (sparse)

### Controlled vocabularies

study_design exact values (use CONTAINS for fuzzy match):
  "Randomized Controlled Trial (RCT)"
  "Quasi-Experimental Design (QED)"
  "Meta-Analysis / Systematic Review"
  "Mixed-Methods"
  "Observational / Correlational"
  "Qualitative"
  "Framework / Theoretical"

quality_tier: blue (highest rigor) > green > yellow > red (lowest)
  — always filter out red: AND p.quality_tier <> 'red'

populations (list on Paper — grade/group of study participants):
  "Elementary (PreK-5th)", "Middle School (6th-8th)", "High School (9th-12th)",
  "K-12 (unspecified grade)", "Undergraduate", "Graduate / Doctoral", "Adult (non-academic)"
  — use: any(pop IN p.populations WHERE toLower(pop) CONTAINS $val)
  — NOTE: populations is about WHO was studied, NOT what topic. For topic search use extended_summary.

Outcome node names (use for outcome-based queries):
  "Academic — Literacy"
  "Academic — Mathematical Numeracy"
  "Academic — Language Fluency"
  "Academic — Scientific Reasoning"
  "Academic — Other"
  "Social-Emotional Skills"
  "Durable Skills"
  "Operational Efficiency"
  "Systemic / Institutional Impact"
  "Academic Achievement"

intervention names (sample — use CONTAINS for fuzzy match):
  "ChatGPT", "ITS (General)", "ALEKS", "ASSISTments", "Cognitive Tutor",
  "Khan Academy", "Khanmigo", "Lexia PowerUp", "MathIA", "Duolingo"

EmpiricalFinding.outcome_category values (string property — use for outcome filtering):
  "Academic — Literacy", "Academic — Mathematical Numeracy", "Academic — Language Fluency",
  "Academic — Scientific Reasoning", "Academic — Other", "Durable Skills",
  "Social-Emotional Skills", "Operational Efficiency", "Systemic / Institutional Impact"
"""

_FEW_SHOT = """
## Few-shot examples

Q: What RCT evidence exists for ChatGPT in K-12?
```cypher
MATCH (p:Paper)-[:EVALUATES]->(i:Intervention)
WHERE toLower(i.name) CONTAINS 'chatgpt'
  AND p.study_design IN ['Randomized Controlled Trial (RCT)', 'Quasi-Experimental Design (QED)', 'Meta-Analysis / Systematic Review']
  AND p.quality_tier <> 'red'
OPTIONAL MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding)
WITH p, collect(DISTINCT i.name) AS interventions, collect(f)[0..3] AS findings
RETURN p, interventions, findings
ORDER BY p.quality_tier ASC, p.year DESC
LIMIT 15
```

Q: How many papers study reading and literacy outcomes?
```cypher
MATCH (p:Paper)-[:FOCUSES_ON_OUTCOME]->(o:Outcome)
WHERE o.name CONTAINS 'Literacy'
  AND p.quality_tier <> 'red'
RETURN count(DISTINCT p) AS paper_count, collect(DISTINCT o.name) AS outcome_names
```

Q: What does the corpus say about AI tutoring for math in middle school?
```cypher
MATCH (p:Paper)-[:EVALUATES]->(i:Intervention)
WHERE p.quality_tier <> 'red'
  AND any(pop IN p.populations WHERE toLower(pop) CONTAINS 'middle school')
OPTIONAL MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding)
  WHERE f.outcome_category CONTAINS 'Mathematical'
WITH p, collect(DISTINCT i.name) AS interventions, collect(f)[0..3] AS findings
WHERE size(findings) > 0
RETURN p, interventions, findings
ORDER BY p.quality_tier ASC, p.year DESC
LIMIT 15
```

Q: Compare ChatGPT vs ITS tools
```cypher
MATCH (p:Paper)-[:EVALUATES]->(i:Intervention)
WHERE (toLower(i.name) CONTAINS 'chatgpt' OR toLower(i.name) CONTAINS 'its')
  AND p.quality_tier <> 'red'
OPTIONAL MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding)
WITH p, collect(DISTINCT i.name) AS interventions, collect(f)[0..2] AS findings
RETURN p, interventions, findings
ORDER BY p.quality_tier ASC, p.year DESC
LIMIT 20
```

Q: How does AI tutoring compare to traditional instruction?
```cypher
MATCH (p:Paper)-[:EVALUATES]->(i:Intervention)
WHERE p.quality_tier <> 'red'
  AND (toLower(i.name) CONTAINS 'tutor' OR toLower(i.name) CONTAINS 'its' OR toLower(i.description) CONTAINS 'tutor')
OPTIONAL MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding)
WITH p, collect(DISTINCT i.name) AS interventions, collect(f)[0..3] AS findings
RETURN p, interventions, findings
ORDER BY p.quality_tier ASC, p.year DESC
LIMIT 15
```

Q: What are the most influential papers in the corpus?
```cypher
MATCH (p:Paper)
WHERE p.eta IS NOT NULL AND p.quality_tier <> 'red'
OPTIONAL MATCH (p)-[:EVALUATES]->(i:Intervention)
WITH p, collect(DISTINCT i.name) AS interventions
RETURN p, interventions, [] AS findings
ORDER BY p.eta DESC
LIMIT 15
```

Q: How many papers are in the corpus? Show quality breakdown.
```cypher
MATCH (p:Paper)
RETURN p.quality_tier AS tier, count(p) AS cnt
ORDER BY cnt DESC
```

Q: What outcome areas have the most evidence?
```cypher
MATCH (o:Outcome)<-[:TARGETS_OUTCOME]-(f:EmpiricalFinding)<-[:REPORTS_FINDING]-(p:Paper)
WHERE p.quality_tier <> 'red'
RETURN o.name AS outcome, count(DISTINCT p) AS papers, count(f) AS findings
ORDER BY papers DESC
```
"""

_CYPHER_SYSTEM = f"""You are a Neo4j Cypher expert for an AI-in-education research corpus.

Given a user question, write a Cypher query to retrieve the most relevant data.

{_SCHEMA}

{_FEW_SHOT}

## Rules
- Use CONTAINS (not =) for fuzzy string matching on names/titles
- Always filter out red quality papers: AND p.quality_tier <> 'red'
- Use toLower() for case-insensitive matching
- LIMIT 15 for paper lists; no limit needed for counts/aggregations
- For topic-based searches (reading, math, etc.) use extended_summary or outcome_category — NOT populations
- populations is only for grade/group filters (elementary, high school, undergraduate)
- When the question mentions "K-12" as context (e.g. "ChatGPT in K-12"), do NOT add a populations filter — K-12 here means the domain, not that you should filter papers to only those with K-12 populations tags
- When the question asks for counts or stats, return counts not paper lists
- Always include OPTIONAL MATCH for relationships that may not exist on every paper
- Return p, interventions, findings for paper lists so the synthesizer has full context
"""


# ── Neo4j connection ───────────────────────────────────────────────────────────

def _neo4j_session():
    if not os.environ.get("NEO4J_URI"):
        return None, None
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            os.environ["NEO4J_URI"],
            auth=(os.environ.get("NEO4J_USER", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        )
        database = os.environ.get("NEO4J_DATABASE", "neo4j")
        return driver, driver.session(database=database)
    except Exception as e:
        log.warning(f"[graph_traversal] Neo4j connection failed: {e}")
        return None, None


# ── Execute Cypher and format results ─────────────────────────────────────────

_QUALITY_CIRCLE = {"blue": "🔵", "green": "🟢", "yellow": "🟡", "red": "🔴"}


def _execute_and_format(db, cypher: str) -> tuple[str, int]:
    """Run cypher, return (formatted_string, result_count)."""
    try:
        rows = list(db.run(cypher))
    except Exception as e:
        return f"Query error: {e}", 0

    if not rows:
        return "No results found.", 0

    # Detect if this is a paper list (has 'p' key) or aggregate (counts/stats)
    first = dict(rows[0])

    if "p" in first:
        return _format_paper_rows(rows), len(rows)
    else:
        # Aggregate / stats result — format as key-value table
        lines = []
        for row in rows:
            d = dict(row)
            lines.append("  " + " | ".join(f"{k}: {v}" for k, v in d.items()))
        return "\n".join(lines), len(rows)


def _format_paper_rows(rows: list) -> str:
    lines = []
    for idx, row in enumerate(rows[:15], 1):
        d = dict(row)
        p = dict(d.get("p") or {})
        interventions = d.get("interventions") or []
        findings_raw = d.get("findings") or []

        title   = p.get("title", "Unknown")
        year    = p.get("year") or "n.d."
        design  = p.get("study_design", "not_reported")
        tier    = p.get("quality_tier", "yellow")
        quality = _QUALITY_CIRCLE.get(tier, "🟡")
        pops    = ", ".join((p.get("populations") or [])[:2]) or "—"
        url     = p.get("url") or p.get("doi") or ""
        tools   = ", ".join(interventions) or "—"
        summary = (p.get("extended_summary") or "")[:180]
        eta_str = f" | η={p['eta']:.2f}" if p.get("eta") else ""

        if url:
            line = f"{idx}. {quality} ({year}) [{title}]({url})"
        else:
            line = f"{idx}. {quality} ({year}) **{title}**"
        line += f"\n   Design: {design} | Tool: {tools} | Population: {pops}{eta_str}"
        if summary:
            line += f"\n   {summary}"

        for f in findings_raw[:1]:
            fd = dict(f) if f else {}
            s = fd.get("finding_summary", "")
            e = fd.get("effect_size", "")
            n = fd.get("sample_size", "")
            if s:
                stat = f"   Finding: {s}"
                if e and e != "not_reported": stat += f" [{e}]"
                if n and n != "not_reported": stat += f" [n={n}]"
                line += f"\n{stat}"

        lines.append(line)
    return "\n\n".join(lines)


# ── Synthesis prompt ───────────────────────────────────────────────────────────

_SYNTH_SYSTEM = """You are a research corpus assistant for an AI-in-education knowledge base of 230+ peer-reviewed papers (2023+).

Answer the user's question using ONLY the corpus data provided. Rules:
- Cite papers inline as [Short Title Year] using title/year from the data
- Be specific: name tools, populations, effect sizes, sample sizes when available
- When describing study populations, state the actual participant age/grade from the data (e.g. "195 college-aged adults 18–22" not just "adults who took SAT/ACT"). Do not conflate a measurement instrument (SAT/ACT used as a baseline metric) with the population grade level.
- Be honest when the corpus has limited or no evidence on something
- Keep responses to 2–4 paragraphs unless more detail is clearly needed
- Use markdown (bold, bullets) where it aids clarity
- Do not invent citations or facts not in the data"""

_SYNTH_HUMAN = """User question: {question}

Corpus query results:
{corpus_data}

Answer based on these results."""


# ── Main graph node ────────────────────────────────────────────────────────────

async def graph_chat(state: GraphChatState, config: RunnableConfig) -> dict:
    """Single-node: generate Cypher → execute Neo4j → synthesize response."""
    from configuration import Configuration
    configurable = Configuration.from_runnable_config(config)
    model_name = getattr(configurable, "model", None) or _DEFAULT_MODEL

    messages = state.get("messages", [])
    user_message = next(
        (m.content for m in reversed(messages) if isinstance(m, HumanMessage)), ""
    )
    if not user_message:
        return {"messages": [AIMessage(content="Please ask a question about the research corpus.")]}

    # Step 1 — generate Cypher
    cypher_llm = init_chat_model(model=_CYPHER_MODEL, temperature=0).with_structured_output(CypherQuery)
    try:
        cypher_result: CypherQuery = await cypher_llm.ainvoke([
            SystemMessage(content=_CYPHER_SYSTEM),
            HumanMessage(content=user_message),
        ])
        cypher = cypher_result.cypher.strip()
        log.info(f"[graph_traversal] Cypher: {cypher[:200]}")
    except Exception as e:
        log.warning(f"[graph_traversal] Cypher generation failed: {e}")
        cypher = ""

    # Step 2 — execute query (run sync Neo4j driver in thread to avoid blocking the async event loop)
    corpus_data = "The knowledge graph is not currently available."
    result_count = 0

    if cypher:
        import asyncio

        def _run_query():
            driver, db = _neo4j_session()
            if db is None:
                return "The knowledge graph is not currently available.", 0
            try:
                return _execute_and_format(db, cypher)
            except Exception as e:
                log.warning(f"[graph_traversal] Query failed: {e}")
                return f"Query error: {e}", 0
            finally:
                db.close()
                if driver:
                    driver.close()

        try:
            corpus_data, result_count = await asyncio.get_event_loop().run_in_executor(None, _run_query)
        except Exception as e:
            corpus_data = f"Query error: {e}"
            log.warning(f"[graph_traversal] Executor failed: {e}")

    log.info(f"[graph_traversal] Results: {result_count} rows")

    # Step 3 — synthesize response
    synth_llm = init_chat_model(model=model_name)
    response = await synth_llm.ainvoke([
        SystemMessage(content=_SYNTH_SYSTEM),
        *messages[:-1],  # prior conversation context
        HumanMessage(content=_SYNTH_HUMAN.format(
            question=user_message,
            corpus_data=corpus_data,
        )),
    ])

    return {
        "messages": [AIMessage(content=str(response.content))],
        "last_cypher": cypher,
        "last_result_count": result_count,
    }


# ── Build graph ────────────────────────────────────────────────────────────────

_builder = StateGraph(GraphChatState)
_builder.add_node("graph_chat", graph_chat)
_builder.add_edge(START, "graph_chat")
_builder.add_edge("graph_chat", END)

graph = _builder.compile()
