# Backward-compatibility shim — do not import from here in new code.
from src.pipeline import SyncResearchPipeline, ResearchPipeline
from src.pipeline.orchestrator import _build_graph_data as build_graph_data_from_papers

__all__ = ["SyncResearchPipeline", "ResearchPipeline", "build_graph_data_from_papers"]
