"""Shared data structures for all searchers."""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str


@dataclass
class SearchResponse:
    searcher: str
    query: str
    results: List[SearchResult] = field(default_factory=list)
    latency_s: float = 0.0
    llm_answer: Optional[str] = None   # synthesized answer for LLM-native searchers
    error: Optional[str] = None

    @property
    def academic_ratio(self) -> float:
        """Fraction of results from academic/institutional domains."""
        academic_tlds = (".edu", ".gov", ".org")
        academic_domains = ("arxiv.org", "pubmed.ncbi", "scholar.google", "doi.org",
                            "semanticscholar.org", "jstor.org", "springer.com",
                            "wiley.com", "tandfonline.com", "sage", "elsevier.com",
                            "eric.ed.gov", "ncbi.nlm.nih.gov", "researchgate.net")
        if not self.results:
            return 0.0
        count = sum(
            1 for r in self.results
            if any(r.url.lower().endswith(t) or t in r.url.lower() for t in academic_tlds + academic_domains)
        )
        return count / len(self.results)

    @property
    def avg_snippet_length(self) -> int:
        if not self.results:
            return 0
        return int(sum(len(r.snippet) for r in self.results) / len(self.results))
