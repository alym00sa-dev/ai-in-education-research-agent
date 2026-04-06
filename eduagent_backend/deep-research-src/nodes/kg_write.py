"""Queue write node — saves paper profiles found during a run to the ingest queue.

Papers are saved to scripts/ingested_papers/queue/{session_id}/ as PaperProfile JSONs.
The weekly batch pipeline picks them up, runs CCM, and MERGEs them into Neo4j.

Neo4j is never written to during a research run — it is read-only at run time.
"""
import json
import logging
import os
from pathlib import Path

from langchain_core.runnables import RunnableConfig

from state import AgentState

log = logging.getLogger(__name__)

# Queue dir relative to this file's repo root (src/../scripts/ingested_papers/queue)
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_QUEUE_DIR = _REPO_ROOT / "KG-src" / "ingested_papers" / "queue"


async def kg_write(state: AgentState, config: RunnableConfig) -> dict:
    """Save full_text paper profiles from this run to the ingest queue directory.

    Profiles are written as individual JSON files to:
        ingested_papers/queue/{session_id}/{doi_or_title_slug}.json

    The weekly batch pipeline processes this directory:
      1. pdf_extractor_kg on any not-yet-extracted papers
      2. citation_chaser --incremental on new papers
      3. CCM retrain → write scores to Neo4j
      4. neo4j_writer --skip-wipe → MERGE new Paper nodes

    Returns empty dict — does not modify any state fields.
    """
    profiles = state.get("paper_profiles", [])
    full_text = [p for p in profiles if _get(p, "extraction_status") == "full_text"]

    if not full_text:
        log.info("[queue_write] No full_text profiles in state — skipping.")
        return {}

    session_id = state.get("session_id", "unknown")
    session_dir = _QUEUE_DIR / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    for profile in full_text:
        try:
            title = _get(profile, "title", "") or ""
            doi = _get(profile, "doi") or ""
            slug = _make_slug(doi or title)
            out_path = session_dir / f"{slug}.json"

            if isinstance(profile, dict):
                data = profile
            else:
                data = profile.model_dump()

            out_path.write_text(json.dumps(data, indent=2, default=str))
            written += 1
        except Exception as e:
            log.error(f"[queue_write] Failed to write profile: {e}")

    log.info(f"[queue_write] Queued {written}/{len(full_text)} papers to {session_dir}")
    return {}


def _get(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _make_slug(s: str) -> str:
    import re
    slug = re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")
    return slug[:80] or "unknown"
