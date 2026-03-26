"""Prompts package — re-exports all prompt variables."""

from prompts.education_discovery import research_brief_prompt
from prompts.supervisor import lead_researcher_prompt
from prompts.researcher import (
    keyword_generation_prompt,
    compress_research_prompt,
    compress_research_human,
    researcher_reflect_prompt,
)
from prompts.executive_summary import executive_summary_prompt
from prompts.critique import critique_prompt
from prompts.report import final_report_prompt, citation_normalize_prompt
from prompts.qa import qa_audit_prompt

__all__ = [
    "research_brief_prompt",
    "lead_researcher_prompt",
    "keyword_generation_prompt",
    "compress_research_prompt",
    "compress_research_human",
    "researcher_reflect_prompt",
    "executive_summary_prompt",
    "critique_prompt",
    "final_report_prompt",
    "citation_normalize_prompt",
    "qa_audit_prompt",
]
