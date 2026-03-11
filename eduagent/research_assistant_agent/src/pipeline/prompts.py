"""LLM prompt constants for the research pipeline."""

OUTLINE_PROMPT = """You are helping structure an academic research report. Based on the query and context below, propose a clear report outline with 4-7 section headings.

Research Query: {query}
Context: {context}

Return ONLY the section headings in markdown format (## for each section), one per line. No introductions, no numbering, no extra text — just the headings.

Example:
## Overview
## Key Findings
## Evidence by Student Population
## Limitations and Research Gaps
## Implications for Practice
"""

CLARIFY_PROMPT = """You are analyzing a research query to extract structured context across four dimensions.

The user's research query is:
"{query}"

Today's date is {date}.

Extract the following dimensions from the query. If a dimension is clearly stated or strongly implied by the query, extract it. If it is not mentioned, return an empty string — do NOT invent or assume details.

Respond in valid JSON with these exact keys:
{{
  "who": "<target population, audience, or subject — e.g. 'K-12 students', 'classroom teachers', 'adults with dyslexia' — or empty string if not mentioned>",
  "what": "<the core topic, intervention, or phenomenon being studied — or empty string if not mentioned>",
  "where": "<geographic location, school type, or setting — e.g. 'U.S. public schools', 'rural districts', 'low-income communities' — or empty string if not mentioned>",
  "when": "<time period or recency requirement — e.g. 'last 10 years', '2015–2025' — or empty string if not mentioned>"
}}
"""
