"""Test queries and evaluation config."""

# Education research queries — realistic inputs for your system
TEST_QUERIES = [
    "effect size of retrieval practice on long-term retention in K-12 students",
    "AI tutoring systems versus human tutoring academic outcomes meta-analysis",
    "socioeconomic achievement gap interventions evidence randomized controlled trial",
]

# How many results to request from each API
NUM_RESULTS = 10

# Scoring dimensions used by the LLM evaluator
SCORING_DIMENSIONS = {
    "relevance": "How well do the results match the research query? (1=off-topic, 5=highly relevant)",
    "source_quality": "Are sources academic, institutional, or peer-reviewed? (1=mostly blogs/SEO, 5=mostly journals/edu/gov)",
    "snippet_usefulness": "Do the snippets contain enough context for an LLM to extract research findings? (1=useless, 5=rich excerpts)",
}
