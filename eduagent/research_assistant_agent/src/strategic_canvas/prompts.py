"""Prompts for Strategic Canvas mode."""

KG_CONTEXT_INJECTION = """
---KNOWLEDGE BASE RESULTS---
{kg_summary}
---END KG CONTEXT---

The user has already approved the research questions. Using the knowledge base results above, briefly narrate what you found in 2 to 3 plain sentences — what's well-covered, what's sparse, what's missing. No formatting, no bullets, no bold. The research buttons will appear automatically after your response.
"""
