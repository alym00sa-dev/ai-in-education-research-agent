"""Prompt templates package — imports all prompts for backward compatibility."""

from prompts.clarify import clarify_with_user_instructions
from prompts.education_discovery import transform_messages_into_research_topic_prompt
from prompts.lead_researcher import lead_researcher_prompt
from prompts.research_system import research_system_prompt
from prompts.compress_research import compress_research_system_prompt, compress_research_simple_human_message
from prompts.pdf_extraction import pdf_extraction_prompt
from prompts.paper_filter import paper_filter_prompt
from prompts.researcher_reflect import researcher_reflect_prompt
from prompts.keyword_generation import keyword_generation_prompt
from prompts.critique_agent import critique_agent_prompt, critique_agent_search_prompt
from prompts.final_report import final_report_generation_prompt
from prompts.swanson_abc import swanson_abc_prompt
from prompts.qa_review import qa_review_prompt
from prompts.summarize_webpage import summarize_webpage_prompt

__all__ = [
    "clarify_with_user_instructions",
    "transform_messages_into_research_topic_prompt",
    "lead_researcher_prompt",
    "research_system_prompt",
    "compress_research_system_prompt",
    "compress_research_simple_human_message",
    "pdf_extraction_prompt",
    "paper_filter_prompt",
    "researcher_reflect_prompt",
    "keyword_generation_prompt",
    "critique_agent_prompt",
    "critique_agent_search_prompt",
    "final_report_generation_prompt",
    "swanson_abc_prompt",
    "qa_review_prompt",
    "summarize_webpage_prompt",
]
