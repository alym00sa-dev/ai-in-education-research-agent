"""Graph Traversal Chat — conversational interface over the Neo4j KG corpus.

Single-node LangGraph graph. Multi-turn conversation handled via LangGraph threads.
Each user message:
  1. LLM generates a Cypher query from the full schema + few-shot examples
  2. Execute query against Neo4j
  3. LLM synthesizes a prose response from the results

Graph name: "graph_traversal" (registered in langgraph.json)
"""

import asyncio
import logging
import os
import sys
import time

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

class CypherQueries(BaseModel):
    specific: str = Field(description="Narrow query: exact intervention names (from the list), study design filter, outcome category — most precise")
    medium: str = Field(description="Moderate query: broader name patterns, is_ai_powered flag, or outcome category families — catches near misses")
    broad: str = Field(description="Widest fallback: topic keywords in toLower(p.extended_summary) CONTAINS, minimal filters — ensures results even when specific/medium miss")


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

Q: What is the most recent research around GenAI in education?
```cypher
MATCH (p:Paper)-[:EVALUATES]->(i:Intervention)
WHERE i.is_ai_powered = true
  AND p.quality_tier <> 'red'
OPTIONAL MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding)
WITH p, collect(DISTINCT i.name) AS interventions, collect(f)[0..3] AS findings
RETURN p, interventions, findings
ORDER BY p.year DESC
LIMIT 15
```

Q: What effect sizes exist around GenAI use and literacy outcomes?
```cypher
MATCH (p:Paper)-[:EVALUATES]->(i:Intervention)
WHERE i.is_ai_powered = true
  AND p.quality_tier <> 'red'
OPTIONAL MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding)
  WHERE f.outcome_category CONTAINS 'Literacy' OR f.outcome_category CONTAINS 'Language'
WITH p, collect(DISTINCT i.name) AS interventions, collect(f)[0..3] AS findings
RETURN p, interventions, findings
ORDER BY p.quality_tier ASC, p.year DESC
LIMIT 15
```

Q: What does the corpus say about GenAI and math?
```cypher
MATCH (p:Paper)-[:EVALUATES]->(i:Intervention)
WHERE i.is_ai_powered = true
  AND p.quality_tier <> 'red'
OPTIONAL MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding)
  WHERE f.outcome_category CONTAINS 'Mathematical'
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

## 3-query structure example

Q: What research exists on AI tools for student writing improvement?

specific:
```cypher
MATCH (p:Paper)-[:EVALUATES]->(i:Intervention)
WHERE i.is_ai_powered = true AND p.quality_tier <> 'red'
OPTIONAL MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding)
  WHERE f.outcome_category CONTAINS 'Literacy'
WITH p, collect(DISTINCT i.name) AS interventions, collect(f)[0..3] AS findings
WHERE size(findings) > 0
RETURN p, interventions, findings
ORDER BY p.quality_tier ASC, p.year DESC LIMIT 15
```

medium:
```cypher
MATCH (p:Paper)-[:FOCUSES_ON_OUTCOME]->(o:Outcome)
WHERE p.quality_tier <> 'red' AND o.name CONTAINS 'Literacy'
OPTIONAL MATCH (p)-[:EVALUATES]->(i:Intervention)
OPTIONAL MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding)
WITH p, collect(DISTINCT i.name) AS interventions, collect(f)[0..3] AS findings
RETURN p, interventions, findings
ORDER BY p.quality_tier ASC, p.year DESC LIMIT 15
```

broad:
```cypher
MATCH (p:Paper)-[:EVALUATES]->(i:Intervention)
WHERE p.quality_tier <> 'red'
  AND (toLower(p.extended_summary) CONTAINS 'writing' OR toLower(p.extended_summary) CONTAINS 'literacy')
OPTIONAL MATCH (p)-[:REPORTS_FINDING]->(f:EmpiricalFinding)
WITH p, collect(DISTINCT i.name) AS interventions, collect(f)[0..3] AS findings
RETURN p, interventions, findings
ORDER BY p.quality_tier ASC, p.year DESC LIMIT 15
```
"""

_CYPHER_SYSTEM = f"""You are a Neo4j Cypher expert for an AI-in-education research corpus.

Given a user question, write a Cypher query to retrieve the most relevant data.

{_SCHEMA}

{_FEW_SHOT}

## Rules
- You must always generate THREE queries: specific (narrow), medium (moderate), broad (widest fallback)
- Use CONTAINS (not =) for fuzzy string matching on names/titles
- Always filter out red quality papers: AND p.quality_tier <> 'red'
- Use toLower() for case-insensitive matching
- LIMIT 15 for paper lists; no limit needed for counts/aggregations
- For topic-based searches (reading, math, writing, etc.) the broad query MUST use toLower(p.extended_summary) CONTAINS — this is the most reliable fallback
- populations is only for grade/group filters (elementary, high school, undergraduate) — NOT for topic searches
- When the question mentions "K-12" as context (e.g. "ChatGPT in K-12"), do NOT add a populations filter — K-12 here means the domain, not a population filter
- For GenAI / generative AI concept queries, use `i.is_ai_powered = true` — do NOT search for a literal "genai" string. The corpus has no intervention named "genai"; AI-powered tools include ChatGPT, GenAI (General), LLM-based Tutoring, and others
- Use the exact intervention names from the list provided — never guess or invent a name
- For "most recent" queries, ORDER BY p.year DESC
- When the question asks for counts or stats, return counts not paper lists
- Always include OPTIONAL MATCH for relationships that may not exist on every paper
- Return p, interventions, findings for paper lists so the synthesizer has full context
"""


# ── AuraDB auto-resume ────────────────────────────────────────────────────────

_NEO4J_HEALTHY_UNTIL: float = 0.0  # epoch seconds; skip connectivity probe before this


def _aura_resume_and_wait(max_wait: int = 30) -> bool:
    """Call the Neo4j AuraDB Management API to resume a paused instance.
    Returns True if the instance reaches 'running' within max_wait seconds."""
    client_id = os.environ.get("AURA_CLIENT_ID")
    client_secret = os.environ.get("AURA_CLIENT_SECRET")
    instance_id = os.environ.get("AURA_INSTANCE_ID")
    if not all([client_id, client_secret, instance_id]):
        log.info("[graph_traversal] AURA credentials not set — skipping auto-resume")
        return False
    try:
        import httpx
        token_resp = httpx.post(
            "https://api.neo4j.io/oauth/token",
            data={"grant_type": "client_credentials"},
            auth=(client_id, client_secret),
            timeout=10,
        )
        token_resp.raise_for_status()
        token = token_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        instance_url = f"https://api.neo4j.io/v1/instances/{instance_id}"
        status = httpx.get(instance_url, headers=headers, timeout=10).json().get("data", {}).get("status", "")
        log.info(f"[graph_traversal] AuraDB instance status: {status}")

        if status == "running":
            return True
        if status == "paused":
            log.info("[graph_traversal] Instance paused — sending resume request")
            httpx.post(f"{instance_url}/resume", headers=headers, timeout=10)

        deadline = time.time() + max_wait
        while time.time() < deadline:
            time.sleep(5)
            resp = httpx.get(instance_url, headers=headers, timeout=10)
            if resp.is_success:
                status = resp.json().get("data", {}).get("status", "")
                log.info(f"[graph_traversal] AuraDB poll: {status}")
                if status == "running":
                    return True
        return False
    except Exception as e:
        log.warning(f"[graph_traversal] AuraDB resume error: {e}")
        return False


# ── Neo4j connection ───────────────────────────────────────────────────────────

def _neo4j_session():
    global _NEO4J_HEALTHY_UNTIL
    if not os.environ.get("NEO4J_URI"):
        return None, None
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            os.environ["NEO4J_URI"],
            auth=(os.environ.get("NEO4J_USER", "neo4j"), os.environ["NEO4J_PASSWORD"]),
        )
        database = os.environ.get("NEO4J_DATABASE", "neo4j")
        session = driver.session(database=database)
        # Probe connectivity unless recently verified
        if time.time() > _NEO4J_HEALTHY_UNTIL:
            session.run("RETURN 1").consume()
            _NEO4J_HEALTHY_UNTIL = time.time() + 300  # trust for 5 minutes
        return driver, session
    except Exception as e:
        log.warning(f"[graph_traversal] Neo4j connection failed: {e}")
        _NEO4J_HEALTHY_UNTIL = 0.0
        return None, None


# ── Intervention name cache ────────────────────────────────────────────────────

_INTERVENTION_CACHE: list[str] = []
_INTERVENTION_CACHE_TS: float = 0.0
_INTERVENTION_CACHE_TTL = 3600  # 1 hour


def _get_intervention_names() -> list[str]:
    """Fetch all Intervention.name values from Neo4j; cached for 1 hour."""
    global _INTERVENTION_CACHE, _INTERVENTION_CACHE_TS
    if _INTERVENTION_CACHE and (time.time() - _INTERVENTION_CACHE_TS) < _INTERVENTION_CACHE_TTL:
        return _INTERVENTION_CACHE
    driver, db = _neo4j_session()
    if db is None:
        return []
    try:
        rows = list(db.run("MATCH (i:Intervention) RETURN i.name AS name ORDER BY i.name"))
        names = [r["name"] for r in rows if r["name"]]
        _INTERVENTION_CACHE = names
        _INTERVENTION_CACHE_TS = time.time()
        return names
    except Exception as e:
        log.warning(f"[graph_traversal] Failed to fetch intervention names: {e}")
        return []
    finally:
        db.close()
        if driver:
            driver.close()


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


# ── Run multiple queries, merge and deduplicate results ───────────────────────

def _run_queries(queries: list[str]) -> tuple[str, int]:
    """Execute up to 3 Cypher queries, merge paper results deduplicating by doi/title."""
    driver, db = _neo4j_session()
    if db is None:
        log.info("[graph_traversal] Neo4j unavailable — attempting AuraDB auto-resume")
        if _aura_resume_and_wait(max_wait=30):
            driver, db = _neo4j_session()
    if db is None:
        return (
            "The knowledge graph is waking up from a paused state — this usually takes "
            "about 60 seconds. Please ask your question again in a moment."
        ), 0
    try:
        seen: set[str] = set()
        merged_rows: list = []
        is_paper_query: bool | None = None

        for cypher in queries:
            if not cypher.strip():
                continue
            try:
                rows = list(db.run(cypher))
                if not rows:
                    continue
                first = dict(rows[0])
                if is_paper_query is None:
                    is_paper_query = "p" in first
                if is_paper_query:
                    for row in rows:
                        d = dict(row)
                        p = dict(d.get("p") or {})
                        key = p.get("doi") or p.get("title", "")
                        if key and key not in seen:
                            seen.add(key)
                            merged_rows.append(row)
                else:
                    # Aggregate query — use first query's results only
                    merged_rows = rows
                    break
            except Exception as e:
                log.warning(f"[graph_traversal] Query failed: {e}")
                continue

        if not merged_rows:
            return "No results found.", 0

        if is_paper_query:
            return _format_paper_rows(merged_rows), len(merged_rows)
        else:
            lines = []
            for row in merged_rows:
                d = dict(row)
                lines.append("  " + " | ".join(f"{k}: {v}" for k, v in d.items()))
            return "\n".join(lines), len(merged_rows)
    finally:
        db.close()
        if driver:
            driver.close()


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
    """Single-node: fetch intervention names → generate 3 Cypher queries → execute + merge → retry on 0 → synthesize."""
    from configuration import Configuration
    configurable = Configuration.from_runnable_config(config)
    model_name = getattr(configurable, "model", None) or _DEFAULT_MODEL

    messages = state.get("messages", [])
    user_message = next(
        (m.content for m in reversed(messages) if isinstance(m, HumanMessage)), ""
    )
    if not user_message:
        return {"messages": [AIMessage(content="Please ask a question about the research corpus.")]}

    # Step 1 — fetch live intervention names (cached 1h) and inject into prompt
    intervention_names = await asyncio.get_event_loop().run_in_executor(None, _get_intervention_names)
    if intervention_names:
        names_block = "\n".join(f'  - "{n}"' for n in intervention_names)
        cypher_system = (
            _CYPHER_SYSTEM
            + f"\n\n## All intervention names currently in the graph (use these exact strings with CONTAINS — do not guess):\n{names_block}"
        )
    else:
        cypher_system = _CYPHER_SYSTEM

    # Step 2 — generate 3 Cypher queries: specific → medium → broad
    cypher_llm = init_chat_model(model=_CYPHER_MODEL, temperature=0).with_structured_output(CypherQueries)
    queries: list[str] = []
    try:
        result: CypherQueries = await cypher_llm.ainvoke([
            SystemMessage(content=cypher_system),
            HumanMessage(content=user_message),
        ])
        queries = [q.strip() for q in [result.specific, result.medium, result.broad] if q.strip()]
        for i, q in enumerate(queries, 1):
            log.info(f"[graph_traversal] Query {i}: {q[:150]}")
    except Exception as e:
        log.warning(f"[graph_traversal] Cypher generation failed: {e}")

    # Step 3 — execute all 3, merge and deduplicate
    corpus_data = "The knowledge graph is not currently available."
    result_count = 0

    if queries:
        try:
            corpus_data, result_count = await asyncio.get_event_loop().run_in_executor(
                None, _run_queries, queries
            )
        except Exception as e:
            corpus_data = f"Query error: {e}"
            log.warning(f"[graph_traversal] Executor failed: {e}")

    log.info(f"[graph_traversal] Results after 3 queries: {result_count} rows")

    # Step 4 — retry with relaxed queries if still 0 results
    if result_count == 0 and queries:
        log.info("[graph_traversal] 0 results — retrying with broadened queries")
        retry_message = (
            f"{user_message}\n\n"
            f"The previous 3 queries returned 0 results. Generate broader fallback queries:\n"
            f"- Use toLower(p.extended_summary) CONTAINS with topic keywords and synonyms\n"
            f"- Remove study_design and population filters entirely\n"
            f"- Keep only p.quality_tier <> 'red'\n"
            f"- Try adjacent concepts (e.g. 'reading' → 'literacy', 'math' → 'numeracy')"
        )
        try:
            retry_result: CypherQueries = await cypher_llm.ainvoke([
                SystemMessage(content=cypher_system),
                HumanMessage(content=retry_message),
            ])
            retry_queries = [q.strip() for q in [retry_result.specific, retry_result.medium, retry_result.broad] if q.strip()]
            if retry_queries:
                corpus_data, result_count = await asyncio.get_event_loop().run_in_executor(
                    None, _run_queries, retry_queries
                )
                log.info(f"[graph_traversal] Retry results: {result_count} rows")
                queries = retry_queries
        except Exception as e:
            log.warning(f"[graph_traversal] Retry failed: {e}")

    # Step 5 — synthesize response
    synth_llm = init_chat_model(model=model_name)
    response = await synth_llm.ainvoke([
        SystemMessage(content=_SYNTH_SYSTEM),
        *messages[:-1],
        HumanMessage(content=_SYNTH_HUMAN.format(
            question=user_message,
            corpus_data=corpus_data,
        )),
    ])

    return {
        "messages": [AIMessage(content=str(response.content))],
        "last_cypher": queries[0] if queries else "",
        "last_result_count": result_count,
    }


# ── Build graph ────────────────────────────────────────────────────────────────

_builder = StateGraph(GraphChatState)
_builder.add_node("graph_chat", graph_chat)
_builder.add_edge(START, "graph_chat")
_builder.add_edge("graph_chat", END)

graph = _builder.compile()
