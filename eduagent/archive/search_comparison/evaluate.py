"""LLM-based scoring of search results using Claude."""
import json
import os
from typing import Dict

import anthropic
from dotenv import load_dotenv
from pathlib import Path

_here = Path(__file__).parent
load_dotenv(_here / ".env")
load_dotenv(_here.parent / "research_assistant_agent" / ".env")

from searchers.base import SearchResponse
from config import SCORING_DIMENSIONS


_SCORE_PROMPT = """\
You are evaluating search results for an education research system.

Query: {query}

Results returned by the "{searcher}" search API:
{results_text}

Score this result set on each dimension from 1 to 5:

{dimensions}

Respond with ONLY valid JSON in this exact format:
{{
  "relevance": <1-5>,
  "source_quality": <1-5>,
  "snippet_usefulness": <1-5>,
  "reasoning": "<1-2 sentence explanation>"
}}
"""


def score_response(response: SearchResponse) -> Dict:
    """Ask Claude to score a SearchResponse. Returns dict with scores + reasoning."""
    if response.error or not response.results:
        return {
            "relevance": 0,
            "source_quality": 0,
            "snippet_usefulness": 0,
            "reasoning": f"Error or no results: {response.error or 'empty'}",
        }

    results_text = "\n".join(
        f"{i+1}. [{r.title}]({r.url})\n   {r.snippet[:200] or '(no snippet)'}"
        for i, r in enumerate(response.results)
    )
    dimensions_text = "\n".join(
        f"- {dim}: {desc}" for dim, desc in SCORING_DIMENSIONS.items()
    )

    prompt = _SCORE_PROMPT.format(
        query=response.query,
        searcher=response.searcher,
        results_text=results_text,
        dimensions=dimensions_text,
    )

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = msg.content[0].text.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(l for l in lines if not l.strip().startswith("```")).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "relevance": 0,
            "source_quality": 0,
            "snippet_usefulness": 0,
            "reasoning": f"Could not parse scores: {raw[:100]}",
        }
