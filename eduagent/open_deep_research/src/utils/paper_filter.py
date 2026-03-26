"""Two-model ensemble filter for academic paper results.

Runs Haiku + GPT-4.1-mini in parallel. Each scores papers on a single
1–5 relevance scale. Papers with an average score > 1.5 pass; all others
are dropped. If both models fail, all papers pass through as a safety fallback.
"""

import asyncio
import logging
import os
import re
from statistics import mean
from typing import Optional

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from prompts import paper_filter_prompt

logger = logging.getLogger(__name__)

# Tools whose formatted string output can be parsed into [N] paper blocks
FILTERABLE_TOOLS = {
    "eric_search",
    "openalex_search",
    "arxiv_search",
    "elsevier_search",
    "semantic_scholar_search",
    "search_papers_by_relevance",
}

_PASS_THRESHOLD = 2.0  # avg score must be > 2.0 to pass (keeps scores 3-7, drops 0-2)


class PaperScore(BaseModel):
    index: int
    title: str = Field(default="")
    score: int = Field(ge=0, le=7)


class FilterResult(BaseModel):
    papers: list[PaperScore]


def _parse_paper_blocks(text: str) -> dict[int, str]:
    """Parse formatted tool output into {index: block_text} mapping."""
    matches = list(re.finditer(r"\[(\d+)\] Title:", text))
    if not matches:
        return {}
    blocks = {}
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        idx = int(match.group(1))
        blocks[idx] = text[start:end].strip()
    return blocks


def _extract_header(text: str) -> str:
    """Extract the header line(s) before the first paper block."""
    match = re.search(r"\[1\] Title:", text)
    if match:
        return text[: match.start()].strip()
    return ""


def _avg_score(paper: PaperScore) -> float:
    return float(paper.score)


async def _score_papers(
    model_name: str,
    api_key: Optional[str],
    research_topic: str,
    papers_text: str,
) -> Optional[FilterResult]:
    """Ask one model to score all papers. Returns None on failure."""
    try:
        model = init_chat_model(
            model=model_name,
            max_tokens=2048,
            api_key=api_key,
            tags=["langsmith:nostream"],
        ).with_structured_output(FilterResult)

        # Sanitize: remove null bytes and non-printable control chars that break JSON
        clean_text = "".join(c for c in papers_text if c >= " " or c in "\n\t")
        prompt = paper_filter_prompt.format(
            research_topic=research_topic,
            papers_text=clean_text[:8000],  # cap to avoid oversized payloads
        )
        return await model.ainvoke([HumanMessage(content=prompt)])
    except Exception as e:
        logger.warning(f"[paper_filter] {model_name} scoring failed: {e}")
        return None


async def ensemble_filter(
    tool_name: str,
    tool_output: str,
    research_topic: str,
) -> tuple[str, list[dict]]:
    """Filter a tool's paper results using a 2-model ensemble.

    Returns:
        filtered_output: formatted string containing only passing papers
        filter_log: list of dicts with scoring details for all papers
    """
    blocks = _parse_paper_blocks(tool_output)
    if not blocks:
        return tool_output, []

    header = _extract_header(tool_output)
    papers_text = "\n\n".join(blocks[i] for i in sorted(blocks))

    haiku_result, gpt_result = await asyncio.gather(
        _score_papers(
            "anthropic:claude-haiku-4-5-20251001",
            os.getenv("ANTHROPIC_API_KEY"),
            research_topic,
            papers_text,
        ),
        _score_papers(
            "openai:gpt-4.1-mini",
            os.getenv("OPENAI_API_KEY"),
            research_topic,
            papers_text,
        ),
    )

    # If both models failed, pass everything through
    if haiku_result is None and gpt_result is None:
        logger.warning(f"[paper_filter] Both models failed for {tool_name} — passing all papers")
        return tool_output, []

    # Index scores by paper index for each model
    haiku_scores: dict[int, PaperScore] = {}
    gpt_scores: dict[int, PaperScore] = {}

    if haiku_result:
        haiku_scores = {p.index: p for p in haiku_result.papers}
    if gpt_result:
        gpt_scores = {p.index: p for p in gpt_result.papers}

    passing_blocks: list[str] = []
    filter_log: list[dict] = []

    for idx in sorted(blocks):
        haiku_paper = haiku_scores.get(idx)
        gpt_paper = gpt_scores.get(idx)

        haiku_avg = _avg_score(haiku_paper) if haiku_paper else None
        gpt_avg = _avg_score(gpt_paper) if gpt_paper else None

        available_avgs = [a for a in [haiku_avg, gpt_avg] if a is not None]
        overall_avg = mean(available_avgs) if available_avgs else 3.0  # default pass if no scores

        passed = overall_avg > _PASS_THRESHOLD

        title = (
            (haiku_paper and haiku_paper.title) or
            (gpt_paper and gpt_paper.title) or
            f"Paper [{idx}]"
        )

        log_entry = {
            "tool": tool_name,
            "index": idx,
            "title": title,
            "decision": "PASS" if passed else "DROP",
            "overall_avg": round(overall_avg, 2),
            "haiku_score": haiku_paper.score if haiku_paper else None,
            "gpt_score": gpt_paper.score if gpt_paper else None,
        }
        filter_log.append(log_entry)

        if passed:
            passing_blocks.append(blocks[idx])

    if not passing_blocks:
        # Safety: if filter drops everything, pass all through (something went wrong)
        logger.warning(f"[paper_filter] All papers dropped for {tool_name} — passing all through as safety fallback")
        return tool_output, filter_log

    # Reconstruct output with renumbered passing papers
    renumbered = []
    for new_idx, block in enumerate(passing_blocks, 1):
        renumbered.append(re.sub(r"^\[\d+\]", f"[{new_idx}]", block))

    passed_count = len(passing_blocks)
    dropped_count = len(blocks) - passed_count
    filtered_output = (
        f"{header}\n\n" if header else ""
    ) + f"[Filter: {passed_count} passed, {dropped_count} dropped — avg score >{_PASS_THRESHOLD}/7]\n\n" + "\n\n".join(renumbered)

    return filtered_output, filter_log
