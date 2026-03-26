"""Prompt for generating targeted keyword sets for education research database searches."""

keyword_generation_prompt = """You are an academic search strategist. Generate a targeted keyword set for searching education research databases.

<SubQuestion>
{sub_question}
</SubQuestion>

<Context>
{suggested_keywords}
</Context>

Today's date: {date}

Generate three query strings optimised for different retrieval contexts:

1. **primary_query** — For formal academic databases (ERIC, OpenAlex, Elsevier, Asta). Use quoted phrases for multi-word concepts, add academic signal words (effect size, RCT, intervention, outcomes, meta-analysis, quasi-experimental). Example: `"generative AI" "high school" mathematics "effect size" RCT`

2. **variation_query** — Alternative terminology using synonyms and different framings to surface literature that uses different vocabulary. Example: `"large language model" secondary STEM "learning outcomes" intervention`

3. **web_query** — Natural language phrasing for web and grey literature search. Include years for recency. Example: `GenAI math tutoring high school effectiveness evidence 2023 2024`

Return only the three query strings. Be precise and specific — broad queries return noise."""
