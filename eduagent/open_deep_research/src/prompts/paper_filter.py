"""Prompt for scoring academic papers for relevance to a research sub-question."""

paper_filter_prompt = """You are scoring academic papers for relevance to a research sub-question.

Research sub-question: {research_topic}

Papers:
{papers_text}

Score every paper [N] on a 0–7 scale:

0 = completely irrelevant (wrong domain, no connection to the topic)
1 = very tangential (mentions a related term but different field or context)
2 = tangentially related (same broad domain, but wrong intervention or wrong population)
3 = indirect evidence (right domain, but different population, age group, or study design)
4 = somewhat relevant — addresses the topic but with methodological or population gaps
5 = relevant — addresses the sub-question with some empirical evidence
6 = directly relevant — strong match on topic, population, and design; useful evidence
7 = direct hit — precisely addresses the sub-question with rigorous empirical evidence (RCT, quasi-experiment, meta-analysis)

Return a score for every paper listed."""
