from . import brave_search, claude_search, exa_search, openai_search, serper_search, tavily_search
from . import openalex_search, eric_search, semantic_scholar_search

ALL_SEARCHERS = {
    "claude": claude_search.search,
    "openai": openai_search.search,
    "exa": exa_search.search,
    "brave": brave_search.search,
    "serper": serper_search.search,
    "tavily": tavily_search.search,
}

PAPER_DB_SEARCHERS = {
    "openalex": openalex_search.search,
    "eric": eric_search.search,
    "semantic_scholar": semantic_scholar_search.search,
}
