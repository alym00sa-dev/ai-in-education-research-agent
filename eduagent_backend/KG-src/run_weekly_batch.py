"""run_weekly_batch.py — Weekly KG update pipeline.

Flow:
  1a. Run ingest_papers.py batch 1 → ingested_papers/{YYYY-MM-DD}/papers/
  1b. Run ingest_papers.py batch 2 → ingested_papers/{YYYY-MM-DD}/papers/ (same dir)
  1c. Run ingest_scale.py        → ingested_papers/{YYYY-MM-DD}/scale/
  2.  Run citation_chaser on both dirs together → merged/
  3.  Retrain CCM on the updated network
  4.  Write new papers to Neo4j with --skip-wipe (upsert only)

NOTE: the legacy kg_write queue step (extract_queued_papers) is preserved
below but no longer invoked from main(). To re-enable, uncomment the call
in main().

Usage:
    python KG-src/run_weekly_batch.py
    python KG-src/run_weekly_batch.py --dry-run
    python KG-src/run_weekly_batch.py --skip-ingest  # skip search + scale, run downstream only
"""

import argparse
import asyncio
import json
import logging
import os
import re
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

TODAY = date.today().isoformat()  # e.g. "2026-05-05"
NEW_PAPERS_DIR = INGEST_BASE / TODAY            # base for today's batch
PAPERS_DIR     = NEW_PAPERS_DIR / "papers"      # ingest_papers.py output
SCALE_DIR      = NEW_PAPERS_DIR / "scale"       # ingest_scale.py output

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

    # ── Neo4j preflight: load existing paper keys + intervention names ─────────
    existing_dois: set[str] = set()
    existing_titles: set[str] = set()
    existing_interventions: list[str] = []
    try:
        from neo4j import GraphDatabase as _GDB
        _driver = _GDB.driver(
            os.getenv("NEO4J_URI"),
            auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD")),
        )
        with _driver.session(database=os.getenv("NEO4J_DATABASE", "neo4j")) as db:
            for record in db.run("MATCH (p:Paper) RETURN p.doi AS doi, p.title AS title"):
                if record["doi"]:
                    existing_dois.add(record["doi"].strip().lower())
                if record["title"]:
                    existing_titles.add(re.sub(r"\s+", " ", record["title"].lower())[:80])
            existing_interventions = [
                r["name"] for r in db.run("MATCH (i:Intervention) RETURN i.name AS name") if r["name"]
            ]
        _driver.close()
        log.info(
            f"[Neo4j preflight] {len(existing_dois)} paper DOIs, "
            f"{len(existing_titles)} paper titles, "
            f"{len(existing_interventions)} interventions loaded."
        )
    except Exception as e:
        log.warning(f"[Neo4j preflight] Could not connect — dedup/intervention list unavailable: {e}")

    NEW_PAPERS_DIR.mkdir(parents=True, exist_ok=True)

    model = os.getenv("WEEKLY_BATCH_MODEL", "openai:gpt-5.5-2026-04-23")

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

            # ── Dedup: skip if paper is already in the KG ──────────────────────
            doi_key   = doi.strip().lower()
            title_key = re.sub(r"\s+", " ", title.lower())[:80]
            if (doi_key and doi_key in existing_dois) or title_key in existing_titles:
                log.info(f"  [duplicate] '{title[:60]}' already in KG — skipping.")
                return None

            log.info(f"  → Extracting: '{title[:70]}'")
            profile = await extract_paper_profile_v2(
                paper_block=f"Title: {title}\nDOI: {doi}\nURL: {url}",
                pdf_url=url,
                abstract_url=url,
                research_topic=topic,
                source_db="weekly_batch",
                metadata_model=model,
                taxonomy_model=model,
                known_interventions=existing_interventions,
            )

            if profile.extraction_status != "full_text":
                log.info(f"  [abstract-only] '{title[:60]}' — {profile.extraction_note}")
                return None

            # ── Quality filters (matching ingest_papers.py guards) ──────────────
            if profile.year is not None and profile.year < 2023:
                log.info(f"  [year] '{title[:60]}' year={profile.year} < 2023 — skipping.")
                return None

            if profile.verdict == "no_tool":
                log.info(f"  [verdict] '{title[:60]}' verdict=no_tool — skipping.")
                return None

            if profile.verdict == "framework_only" and (
                profile.quality_tier == "red" or profile.study_design == "Qualitative"
            ):
                log.info(f"  [verdict] '{title[:60]}' framework_only+{profile.quality_tier} — skipping.")
                return None

            slug = re.sub(r"[^a-z0-9]+", "_", (doi or title).lower()).strip("_")[:80]
            out_path = NEW_PAPERS_DIR / f"{slug}.json"
            out_path.write_text(json.dumps(profile.model_dump(), indent=2, default=str))
            log.info(f"  ✓ Saved: {out_path.name}")
            return out_path

        except Exception as e:
            log.error(f"  [error] {paper_path.name}: {e}")
            return None

    results = await asyncio.gather(*[process_one(p) for p in all_papers])
    written = [r for r in results if r is not None]
    skipped = len(all_papers) - len(written)

    log.info(f"[Step 2] Extracted {len(written)} full-text papers, {skipped} skipped.")
    return written


# ── Step 1a/b: Run ingest_papers.py (both batches) ────────────────────────────

def run_ingest_papers(dry_run: bool):
    for batch in (1, 2):
        log.info(f"[Step 1a] Running ingest_papers.py --batch {batch} → {PAPERS_DIR}")
        cmd = [
            sys.executable,
            str(SCRIPTS_DIR / "ingest_papers.py"),
            "--batch", str(batch),
            "--output-dir", str(PAPERS_DIR),
        ]
        if dry_run:
            cmd += ["--max-queries", "2"]
        result = subprocess.run(cmd, cwd=str(REPO_ROOT))
        if result.returncode != 0:
            log.error(f"[Step 1a] ingest_papers batch {batch} failed — aborting batch.")
            sys.exit(1)
    log.info("[Step 1a] ingest_papers complete (batches 1 + 2).")


# ── Step 1c: Run ingest_scale.py ───────────────────────────────────────────────

def run_ingest_scale(dry_run: bool):
    log.info(f"[Step 1b] Running ingest_scale.py → {SCALE_DIR}")
    cmd = [
        sys.executable,
        str(SCRIPTS_DIR / "ingest_scale.py"),
        "--output-dir", str(SCALE_DIR),
    ]
    if dry_run:
        cmd.append("--dry-run")
    result = subprocess.run(cmd, cwd=str(REPO_ROOT))
    if result.returncode != 0:
        log.error("[Step 1b] ingest_scale failed — aborting batch.")
        sys.exit(1)
    log.info("[Step 1b] ingest_scale complete.")


# ── Step 3: Run citation_chaser on new papers ──────────────────────────────────

def _active_input_dirs() -> list[Path]:
    """Return the subset of {PAPERS_DIR, SCALE_DIR} that exist and contain JSON."""
    return [d for d in (PAPERS_DIR, SCALE_DIR) if d.exists() and any(d.glob("*.json"))]


def run_citation_chaser(dry_run: bool):
    dirs = _active_input_dirs()
    if not dirs:
        log.info("[Step 3] No new papers to chase citations for — skipping.")
        return

    log.info(f"[Step 3] Running citation_chaser on {[str(d) for d in dirs]} ...")
    cmd = [
        sys.executable,
        str(SCRIPTS_DIR / "citation_chaser.py"),
        "--papers-dir", *[str(d) for d in dirs],
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
    dirs = _active_input_dirs()
    if not dirs:
        log.info("[Step 5] No new papers to write to Neo4j — skipping.")
        return

    chase_network = MERGED_DIR / "_chase_network.json"

    log.info(f"[Step 5] Writing {len(dirs)} dir(s) to Neo4j (--skip-wipe) ...")
    cmd = [
        sys.executable,
        str(SCRIPTS_DIR / "neo4j_writer.py"),
        "--skip-wipe",
        "--papers-dirs", *[str(d) for d in dirs],
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
    parser = argparse.ArgumentParser(description="Weekly KG update batch")
    parser.add_argument("--dry-run", action="store_true", help="Log actions without executing them")
    parser.add_argument("--skip-ingest", action="store_true", help="Skip ingest_papers + ingest_scale (run downstream only)")
    args = parser.parse_args()

    log.info(f"{'='*60}")
    log.info(f"Weekly KG Batch — {TODAY}{' [DRY RUN]' if args.dry_run else ''}")
    log.info(f"{'='*60}")

    # Legacy queue extraction — the kg_write queue is no longer the primary
    # ingestion source. Re-enable by uncommenting if needed.
    # await extract_queued_papers(args.dry_run)

    if not args.skip_ingest:
        run_ingest_papers(args.dry_run)
        run_ingest_scale(args.dry_run)
    else:
        log.info("[Step 1] Skipping ingest_papers + ingest_scale (--skip-ingest).")

    run_citation_chaser(args.dry_run)
    run_ccm_trainer(args.dry_run)
    run_neo4j_writer(args.dry_run)
    # archive_queue(args.dry_run)  # disabled — no queue to archive

    log.info(f"{'='*60}")
    log.info("Weekly batch complete.")
    log.info(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
