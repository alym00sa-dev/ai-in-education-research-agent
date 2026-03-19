"""Single-model relevance filter for academic paper results (0-7 scale)."""

import logging
import os
import re

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

FILTERABLE_TOOLS = {
    "eric_search",
    "openalex_search",
    "arxiv_search",
    "elsevier_search",
    "semantic_scholar_search",
}

_PASS_THRESHOLD = 1.0
_DEFAULT_MODEL = "gpt-5.4-mini-2026-03-17"

paper_filter_prompt = """You are scoring academic papers for relevance to a research sub-question.

Research sub-question: {research_topic}

Papers:
{papers_text}

Score every paper [N] on a 0-7 scale:

0 = completely irrelevant (wrong domain, no connection to the topic)
1 = very tangential (mentions a related term but different field or context)
2 = tangentially related (same broad domain, but wrong intervention or population)
3 = indirect evidence (right domain, but different population, age group, or study design)
4 = somewhat relevant — addresses the topic but with methodological or population gaps
5 = relevant — addresses the sub-question with some empirical evidence
6 = directly relevant — strong match on topic, population, and design
7 = direct hit — precisely addresses the sub-question with rigorous empirical evidence

Return a score for every paper listed."""


class PaperScore(BaseModel):
    index: int
    title: str = Field(default="")
    score: int = Field(ge=0, le=7)


class FilterResult(BaseModel):
    papers: list[PaperScore]


def _parse_paper_blocks(text: str) -> dict[int, str]:
    matches = list(re.finditer(r"\[(\d+)\] Title:", text))
    if not matches:
        return {}
    blocks = {}
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        blocks[int(match.group(1))] = text[start:end].strip()
    return blocks


def _extract_header(text: str) -> str:
    match = re.search(r"\[1\] Title:", text)
    return text[:match.start()].strip() if match else ""


async def relevance_filter(
    tool_name: str,
    tool_output: str,
    research_topic: str,
    model_name: str = _DEFAULT_MODEL,
) -> tuple[str, list[dict]]:
    """Filter paper results using a single model on the 0-7 scale.

    Returns:
        filtered_output: string with only passing papers
        filter_log: list of scoring details per paper
    """
    blocks = _parse_paper_blocks(tool_output)
    if not blocks:
        return tool_output, []

    header = _extract_header(tool_output)
    papers_text = "\n\n".join(blocks[i] for i in sorted(blocks))
    clean_text = "".join(c for c in papers_text if c >= " " or c in "\n\t")

    try:
        model = init_chat_model(
            model=model_name,
            max_tokens=4096,
            api_key=os.getenv("OPENAI_API_KEY"),
            tags=["langsmith:nostream"],
        ).with_structured_output(FilterResult)

        prompt = paper_filter_prompt.format(
            research_topic=research_topic,
            papers_text=clean_text[:8000],
        )
        result: FilterResult = await model.ainvoke([HumanMessage(content=prompt)])
    except Exception as e:
        logger.warning(f"[paper_filter] Scoring failed for {tool_name}: {e} — passing all through")
        return tool_output, []

    scores_by_index = {p.index: p for p in result.papers}

    passing_blocks: list[str] = []
    filter_log: list[dict] = []

    for idx in sorted(blocks):
        paper = scores_by_index.get(idx)
        score = float(paper.score) if paper else 3.0  # default pass if not scored
        passed = score > _PASS_THRESHOLD

        filter_log.append({
            "tool": tool_name,
            "index": idx,
            "title": (paper.title if paper else f"Paper [{idx}]"),
            "decision": "PASS" if passed else "DROP",
            "score": score,
        })

        if passed:
            passing_blocks.append(blocks[idx])

    if not passing_blocks:
        logger.warning(f"[paper_filter] All papers dropped for {tool_name} — safety passthrough")
        return tool_output, filter_log

    renumbered = [re.sub(r"^\[\d+\]", f"[{i + 1}]", block)
                  for i, block in enumerate(passing_blocks)]

    passed_count = len(passing_blocks)
    dropped_count = len(blocks) - passed_count
    filtered_output = (
        (f"{header}\n\n" if header else "") +
        f"[Filter: {passed_count} passed, {dropped_count} dropped — threshold >{_PASS_THRESHOLD}/7]\n\n" +
        "\n\n".join(renumbered)
    )

    return filtered_output, filter_log
