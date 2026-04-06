"""run_weekly_batch.py — Weekly KG update pipeline (B9).

Flow:
  1. Find all queued paper JSONs in scripts/ingested_papers/queue/
     (written by kg_write node after each research run)
  2. Re-extract each paper using pdf_extractor_kg (3-call KG extraction:
     metadata + tool taxonomy + citations) using the url from the queued profile
  3. Save PaperProfileV2 JSONs to ingested_papers/{YYYY-MM-DD}/
  4. Run citation_chaser on new papers + existing merged network
  5. Retrain CCM on the updated network
  6. Write new papers to Neo4j with --skip-wipe (upsert only)
  7. Archive processed queue dirs with date stamp

Usage:
    python scripts/run_weekly_batch.py
    python scripts/run_weekly_batch.py --dry-run
    python scripts/run_weekly_batch.py --skip-extraction  # if already extracted
"""

import argparse
import asyncio
import json
import logging
import os
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "deep-research-src"
sys.path.insert(0, str(SRC_DIR))

from dotenv import load_dotenv
load_dotenv(REPO_ROOT / ".env")

SCRIPTS_DIR  = Path(__file__).resolve().parent
INGEST_BASE  = SCRIPTS_DIR / "ingested_papers"
QUEUE_DIR    = INGEST_BASE / "queue"
MERGED_DIR   = INGEST_BASE / "merged"
ARCHIVE_DIR  = INGEST_BASE / "archive"

TODAY = date.today().isoformat()  # e.g. "2026-04-07"
NEW_PAPERS_DIR = INGEST_BASE / TODAY

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("weekly_batch")


# ── Step 1+2: Extract queued papers using pdf_extractor_kg ────────────────────

async def extract_queued_papers(dry_run: bool) -> list[Path]:
    """Find all queued paper JSONs, re-extract with pdf_extractor_kg, save to NEW_PAPERS_DIR.

    Returns list of output JSON paths written.
    """
    from utils.pdf_extractor_kg import extract_paper_profile_v2

    queue_sessions = [d for d in QUEUE_DIR.iterdir() if d.is_dir()] if QUEUE_DIR.exists() else []
    if not queue_sessions:
        log.info("[Step 1] No queued sessions found — nothing to process.")
        return []

    all_papers = []
    for session_dir in queue_sessions:
        for json_path in session_dir.glob("*.json"):
            all_papers.append(json_path)

    log.info(f"[Step 1] Found {len(all_papers)} queued paper(s) across {len(queue_sessions)} session(s).")

    if dry_run:
        log.info("[DRY RUN] Skipping extraction.")
        return []

    NEW_PAPERS_DIR.mkdir(parents=True, exist_ok=True)

    model = os.getenv("WEEKLY_BATCH_MODEL", "openai:gpt-5.4-mini-2026-03-17")
    written: list[Path] = []
    skipped = 0

    async def process_one(paper_path: Path):
        try:
            queued = json.loads(paper_path.read_text())
            url   = queued.get("url", "")
            doi   = queued.get("doi") or ""
            title = queued.get("title", "unknown")
            topic = queued.get("extended_summary", title)[:200]

            if not url:
                log.warning(f"  [skip] No URL for '{title[:60]}' — cannot re-extract.")
                return None

            log.info(f"  → Extracting: '{title[:70]}'")
            profile = await extract_paper_profile_v2(
                block=f"Title: {title}\nDOI: {doi}\nURL: {url}",
                pdf_url=url,
                abstract_url=url,
                research_topic=topic,
                tool_name="weekly_batch",
                metadata_model=model,
                taxonomy_model=model,
            )

            if profile.extraction_status != "full_text":
                log.info(f"  [abstract-only] '{title[:60]}' — {profile.extraction_note}")
                return None

            slug = re.sub(r"[^a-z0-9]+", "_", (doi or title).lower()).strip("_")[:80]
            out_path = NEW_PAPERS_DIR / f"{slug}.json"
            out_path.write_text(json.dumps(profile.model_dump(), indent=2, default=str))
            log.info(f"  ✓ Saved: {out_path.name}")
            return out_path

        except Exception as e:
            log.error(f"  [error] {paper_path.name}: {e}")
            return None

    import re
    results = await asyncio.gather(*[process_one(p) for p in all_papers])
    written = [r for r in results if r is not None]
    skipped = len(all_papers) - len(written)

    log.info(f"[Step 2] Extracted {len(written)} full-text papers, {skipped} skipped.")
    return written


# ── Step 3: Run citation_chaser on new papers ──────────────────────────────────

def run_citation_chaser(dry_run: bool):
    if not NEW_PAPERS_DIR.exists() or not any(NEW_PAPERS_DIR.glob("*.json")):
        log.info("[Step 3] No new papers to chase citations for — skipping.")
        return

    log.info(f"[Step 3] Running citation_chaser on {NEW_PAPERS_DIR} ...")
    cmd = [
        sys.executable,
        str(SCRIPTS_DIR / "citation_chaser.py"),
        "--papers-dir", str(NEW_PAPERS_DIR),
        "--output-dir", str(MERGED_DIR),
        "--incremental",
    ]
    if dry_run:
        cmd.append("--dry-run")

    result = subprocess.run(cmd, cwd=str(REPO_ROOT))
    if result.returncode != 0:
        log.error("[Step 3] citation_chaser failed — aborting batch.")
        sys.exit(1)
    log.info("[Step 3] Citation chase complete.")


# ── Step 4: Retrain CCM ────────────────────────────────────────────────────────

def run_ccm_trainer(dry_run: bool):
    chase_network = MERGED_DIR / "_chase_network.json"
    if not chase_network.exists():
        log.warning(f"[Step 4] No chase network found at {chase_network} — skipping CCM retrain.")
        return

    log.info("[Step 4] Retraining CCM ...")
    cmd = [
        sys.executable,
        str(SCRIPTS_DIR / "ccm_trainer.py"),
        "--network-dir", str(MERGED_DIR),
    ]
    if dry_run:
        cmd.append("--dry-run")

    result = subprocess.run(cmd, cwd=str(REPO_ROOT))
    if result.returncode != 0:
        log.error("[Step 4] CCM trainer failed.")
        sys.exit(1)
    log.info("[Step 4] CCM retrain complete.")


# ── Step 5: Write to Neo4j ─────────────────────────────────────────────────────

def run_neo4j_writer(dry_run: bool):
    if not NEW_PAPERS_DIR.exists() or not any(NEW_PAPERS_DIR.glob("*.json")):
        log.info("[Step 5] No new papers to write to Neo4j — skipping.")
        return

    chase_network = MERGED_DIR / "_chase_network.json"

    log.info("[Step 5] Writing new papers to Neo4j (--skip-wipe) ...")
    cmd = [
        sys.executable,
        str(SCRIPTS_DIR / "neo4j_writer.py"),
        "--skip-wipe",
        "--papers-dirs", str(NEW_PAPERS_DIR),
    ]
    if chase_network.exists():
        cmd += ["--chase-network", str(chase_network)]
    if dry_run:
        cmd.append("--dry-run")

    result = subprocess.run(cmd, cwd=str(REPO_ROOT))
    if result.returncode != 0:
        log.error("[Step 5] neo4j_writer failed.")
        sys.exit(1)
    log.info("[Step 5] Neo4j write complete.")


# ── Step 6: Archive processed queue ───────────────────────────────────────────

def archive_queue(dry_run: bool):
    if not QUEUE_DIR.exists():
        return

    sessions = [d for d in QUEUE_DIR.iterdir() if d.is_dir()]
    if not sessions:
        log.info("[Step 6] Queue is empty — nothing to archive.")
        return

    archive_dest = ARCHIVE_DIR / TODAY
    if dry_run:
        log.info(f"[DRY RUN] Would archive {len(sessions)} session(s) → {archive_dest}")
        return

    archive_dest.mkdir(parents=True, exist_ok=True)
    for session_dir in sessions:
        shutil.move(str(session_dir), str(archive_dest / session_dir.name))

    log.info(f"[Step 6] Archived {len(sessions)} session(s) → {archive_dest}")


# ── Main ───────────────────────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(description="Weekly KG update batch (B9)")
    parser.add_argument("--dry-run", action="store_true", help="Log actions without executing them")
    parser.add_argument("--skip-extraction", action="store_true", help="Skip re-extraction, use existing NEW_PAPERS_DIR")
    args = parser.parse_args()

    log.info(f"{'='*60}")
    log.info(f"Weekly KG Batch — {TODAY}{' [DRY RUN]' if args.dry_run else ''}")
    log.info(f"{'='*60}")

    if not args.skip_extraction:
        await extract_queued_papers(args.dry_run)
    else:
        log.info("[Step 1-2] Skipping extraction (--skip-extraction).")

    run_citation_chaser(args.dry_run)
    run_ccm_trainer(args.dry_run)
    run_neo4j_writer(args.dry_run)
    archive_queue(args.dry_run)

    log.info(f"{'='*60}")
    log.info("Weekly batch complete.")
    log.info(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
