"""Prompts for the researcher subgraph nodes."""

keyword_generation_prompt = """You are an academic search strategist.

Research thread: {research_topic}
Tier: {tier}
Context: {context}
Today: {date}

Generate three search query strings optimized for different databases:

1. primary_query — formal academic query with quoted key phrases + academic signal words
   Example: "high school students" "generative AI" "skill formation" randomized controlled trial

2. variation_query — synonyms and alternative terminology for broader coverage
   Example: secondary school artificial intelligence tools competency development United States

3. web_query — natural language for web search and grey literature
   Example: effectiveness of AI writing tools for high school student skills US evidence
"""

compress_research_prompt = """You are a research assistant that has conducted research on a topic by calling several academic database tools. Your job is now to clean up the findings, but preserve all of the relevant statements and information that was gathered. For context, today's date is {date}.

<Task>
You need to clean up information gathered from tool calls and database searches in the existing messages.
All relevant information should be repeated and rewritten verbatim, but in a cleaner format.
The purpose of this step is just to remove any obviously irrelevant or duplicative information.
Only these fully comprehensive cleaned findings are going to be returned to the user, so it's crucial that you don't lose any information from the raw messages.
</Task>

<Guidelines>
1. Your output findings should be fully comprehensive and include ALL of the information and sources gathered. It is expected that you repeat key information verbatim.
2. This report can be as long as necessary to return ALL of the information that was gathered.
3. In your report, you should return inline citations for each source found.
4. You should include a "Sources" section at the end of the report that lists all of the sources with corresponding citations.
5. Make sure to include ALL sources in the report, and how they were used to answer the question!
6. It's really important not to lose any sources. A later LLM will be used to merge this report with others, so having all of the sources is critical.
7. Include study design labels where reported (RCT, meta-analysis, quasi-experimental, observational, report).
8. Preserve effect sizes, sample sizes, and confidence intervals verbatim — do not round or paraphrase statistics.
</Guidelines>

<Output Format>
The report should be structured like this:
**Databases and Queries Used**
**Fully Comprehensive Findings**
**List of All Relevant Sources (with citations in the report)**
</Output Format>

<Citation Rules — MANDATORY>
CRITICAL: The ### Sources section is not optional. You MUST end every response with it.
- Cite inline as [N] throughout the findings text
- The final ### Sources section must list EVERY source with its number
- Number sources sequentially without gaps: 1, 2, 3, 4...
- For each source include ALL of the following fields — never omit URL:
  [N] Author(s), Year. Title. Journal/Source. URL: <full url or doi link>
- If a URL was returned by the database tool, copy it exactly — do not drop it
- If no URL was returned, write: URL: not available
- Do NOT end with questions, offers to help, or next-step suggestions. End with ### Sources only.
</Citation Rules>

Critical Reminder: It is extremely important that any information that is even remotely relevant to the research thread is preserved verbatim. Do not summarize, do not paraphrase, do not drop sources. This output feeds directly into a downstream synthesis pipeline — do not address the user, do not offer further assistance.
"""

compress_research_human = """All above messages are research gathered from academic databases. Clean up these findings for a downstream synthesis pipeline.

DO NOT summarize. Return raw information in a cleaner format. Preserve all findings verbatim. Do not lose any sources. End ONLY with the ### Sources section — no questions, no offers to help, no next steps."""

researcher_reflect_prompt = """You are auditing the coverage of a research sweep.

Research thread: {research_topic}

Findings so far:
{findings_summary}

Decide: does this sweep provide sufficient coverage to answer the research thread?

- PASS: coverage is adequate — key studies found, main angles addressed
- NEEDS_WORK: important gaps remain (specific populations missing, key study types absent, core questions unanswered)

If NEEDS_WORK, provide targeted follow-up queries that address specifically what is missing.
Do not simply repeat the original queries.
"""
