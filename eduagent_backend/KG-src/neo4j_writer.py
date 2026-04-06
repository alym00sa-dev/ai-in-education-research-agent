"""neo4j_writer.py — Full Neo4j rebuild from the KG corpus.

Wipes the existing graph and writes fresh from three sources:
  1. Ingested paper JSONs (query ingest + SCALE + legacy) — Paper nodes
  2. scripts/tools_final/*.json — Intervention nodes + EVALUATES + EmpiricalFinding
  3. ingested_papers/merged/_chase_network.json — CITES edges

Run AFTER:
  - All corpus sources are ingested (ingest_papers.py, ingest_scale.py, convert_legacy.py)
  - Citation chase is complete (citation_chaser.py → _chase_network.json in --output-dir)

Usage:
    python neo4j_writer.py
    python neo4j_writer.py --dry-run
    python neo4j_writer.py --skip-wipe  # keep existing nodes, upsert only
    python neo4j_writer.py \\
        --papers-dirs ingested_papers/2026-04-01 ingested_papers/scale_2026-04-01 ingested_papers/legacy \\
        --chase-network ingested_papers/merged/_chase_network.json
"""

import json
import os
import re
import sys
import argparse
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT / "deep-research-src"))

# ── Default paths ──────────────────────────────────────────────────────────────

_HERE         = Path(__file__).resolve().parent
TOOLS_DIR     = REPO_ROOT / "KG-src" / "tools_final"
# Fallback to archive location if tools_final hasn't been copied into KG-src yet
if not TOOLS_DIR.exists():
    TOOLS_DIR = Path(__file__).resolve().parent.parent.parent / "archive" / "eduagent-testing" / "old_scripts" / "scripts" / "tools_final"
DEFAULT_PAPERS_DIRS = [
    _HERE / "ingested_papers" / "2026-04-01",
    _HERE / "ingested_papers" / "scale_2026-04-01",
    _HERE / "ingested_papers" / "legacy",
]
DEFAULT_CHASE = _HERE / "ingested_papers" / "merged" / "_chase_network.json"

# ── Quality filter — skip red papers from KG (keep for citation nodes) ─────────
SKIP_VERDICTS  = {"framework_only"}   # don't write Paper nodes for these
SKIP_QUALITY   = {"red"}              # don't write Paper nodes for red papers

# ── Helpers ────────────────────────────────────────────────────────────────────

def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def _doi_norm(doi: str | None) -> str | None:
    if not doi:
        return None
    d = doi.strip().lower()
    return None if d in ("not_reported", "") else d


def _get(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


# ── Load corpus ────────────────────────────────────────────────────────────────

def load_papers(papers_dirs: list[Path]) -> list[dict]:
    """Load all paper JSONs from all corpus dirs, deduplicated by DOI then title."""
    papers = []
    seen_dois: set[str] = set()
    seen_titles: set[str] = set()

    for d in papers_dirs:
        if not d.exists():
            print(f"  [warn] skipping missing dir: {d}")
            continue
        for fp in sorted(d.glob("*.json")):
            if fp.name.startswith("_"):
                continue
            try:
                data = json.loads(fp.read_text())
            except Exception:
                continue
            if not isinstance(data, dict):
                continue

            doi = _doi_norm(data.get("doi"))
            title_key = (data.get("title") or "").strip().lower()[:80]

            if doi and doi in seen_dois:
                continue
            if title_key and title_key in seen_titles:
                continue
            if doi:
                seen_dois.add(doi)
            if title_key:
                seen_titles.add(title_key)

            papers.append(data)

    return papers


def load_tools_final() -> list[dict]:
    """Load all tools_final tool JSON files."""
    tools = []
    for fp in sorted(TOOLS_DIR.glob("*.json")):
        try:
            data = json.loads(fp.read_text())
            if isinstance(data, dict):
                tools.append(data)
        except Exception:
            continue
    return tools


def load_chase_network(chase_path: Path) -> dict:
    """Load _chase_network.json. Returns empty dict if not found."""
    if not chase_path.exists():
        print(f"  [warn] chase network not found: {chase_path} — CITES edges will be skipped")
        return {}
    return json.loads(chase_path.read_text())


# ── Neo4j connection ───────────────────────────────────────────────────────────

def get_driver():
    from neo4j import GraphDatabase
    uri      = os.environ["NEO4J_URI"]
    user     = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ["NEO4J_PASSWORD"]
    return GraphDatabase.driver(uri, auth=(user, password))


# ── Write operations ───────────────────────────────────────────────────────────

def wipe_graph(session) -> None:
    """Delete ALL nodes and relationships. Clean slate."""
    print("  Wiping graph (MATCH (n) DETACH DELETE n) ...")
    session.run("MATCH (n) DETACH DELETE n")
    print("  Graph wiped.")


def ensure_constraints(session) -> None:
    """Create uniqueness constraints if they don't exist."""
    constraints = [
        "CREATE CONSTRAINT paper_doi IF NOT EXISTS FOR (p:Paper) REQUIRE p.doi IS UNIQUE",
        "CREATE CONSTRAINT intervention_id IF NOT EXISTS FOR (i:Intervention) REQUIRE i.intervention_id IS UNIQUE",
        "CREATE CONSTRAINT finding_id IF NOT EXISTS FOR (f:EmpiricalFinding) REQUIRE f.finding_id IS UNIQUE",
        "CREATE CONSTRAINT outcome_name IF NOT EXISTS FOR (o:Outcome) REQUIRE o.name IS UNIQUE",
    ]
    for c in constraints:
        try:
            session.run(c)
        except Exception:
            pass  # constraint may already exist


def write_paper_node(session, paper: dict, added_date: str) -> str | None:
    """Write a single Paper node. Returns the paper's merge key or None if skipped."""
    verdict = paper.get("verdict", "")
    quality = paper.get("quality_tier", "")

    if verdict in SKIP_VERDICTS:
        return None
    if quality in SKIP_QUALITY:
        return None

    doi   = _doi_norm(paper.get("doi"))
    title = (paper.get("title") or "").strip()
    if not doi and not title:
        return None

    params = {
        "title":                   title,
        "doi":                     doi,
        "year":                    paper.get("year"),
        "venue":                   paper.get("venue") or "",
        "url":                     paper.get("url") or "",
        "source_db":               paper.get("source_db") or "",
        "populations":             paper.get("populations") or [],
        "user_types":              paper.get("user_types") or [],
        "study_design":            paper.get("study_design") or "not_reported",
        "extended_summary":        paper.get("extended_summary") or "",
        "limitations":             paper.get("limitations") or [],
        "duration_weeks":          paper.get("duration_weeks") or "not_reported",
        "setting":                 paper.get("setting") or "not_reported",
        "teacher_training":        paper.get("teacher_training") or "not_reported",
        "implementation_fidelity": paper.get("implementation_fidelity") or "not_reported",
        "study_country":           paper.get("study_country") or "not_reported",
        "study_region":            paper.get("study_region") or "not_reported",
        "verdict":                 verdict,
        "quality_tier":            quality,
        "quality_tier_rationale":  paper.get("quality_tier_rationale") or "",
        "impact_tier":             paper.get("impact_tier") or "",
        "impact_tier_rationale":   paper.get("impact_tier_rationale") or "",
        "extraction_status":       paper.get("extraction_status") or "full_text",
        "added_date":              added_date,
    }

    if doi:
        session.run("""
            MERGE (p:Paper {doi: $doi})
            SET p.title = $title, p.year = $year, p.venue = $venue,
                p.url = $url, p.source_db = $source_db,
                p.populations = $populations, p.user_types = $user_types,
                p.study_design = $study_design,
                p.extended_summary = $extended_summary,
                p.limitations = $limitations,
                p.duration_weeks = $duration_weeks, p.setting = $setting,
                p.teacher_training = $teacher_training,
                p.implementation_fidelity = $implementation_fidelity,
                p.study_country = $study_country, p.study_region = $study_region,
                p.verdict = $verdict,
                p.quality_tier = $quality_tier,
                p.quality_tier_rationale = $quality_tier_rationale,
                p.impact_tier = $impact_tier,
                p.impact_tier_rationale = $impact_tier_rationale,
                p.extraction_status = $extraction_status,
                p.added_date = $added_date
        """, params)
        return doi
    else:
        session.run("""
            MERGE (p:Paper {title: $title})
            SET p.year = $year, p.venue = $venue,
                p.url = $url, p.source_db = $source_db,
                p.populations = $populations, p.user_types = $user_types,
                p.study_design = $study_design,
                p.extended_summary = $extended_summary,
                p.limitations = $limitations,
                p.duration_weeks = $duration_weeks, p.setting = $setting,
                p.teacher_training = $teacher_training,
                p.implementation_fidelity = $implementation_fidelity,
                p.study_country = $study_country, p.study_region = $study_region,
                p.verdict = $verdict,
                p.quality_tier = $quality_tier,
                p.quality_tier_rationale = $quality_tier_rationale,
                p.impact_tier = $impact_tier,
                p.impact_tier_rationale = $impact_tier_rationale,
                p.extraction_status = $extraction_status,
                p.added_date = $added_date
        """, params)
        return title


def write_tool_graph(session, tool: dict, paper_title_index: dict[str, str]) -> int:
    """Write Intervention node + EVALUATES edges + EmpiricalFinding nodes from one tools_final entry.

    paper_title_index: lowercase title[:80] → doi_or_title (Paper merge key)

    Returns number of findings written.
    """
    tool_name = tool.get("name", "").strip()
    if not tool_name:
        return 0

    intervention_id = _slug(tool_name)

    session.run("""
        MERGE (i:Intervention {intervention_id: $intervention_id})
        SET i.name = $name,
            i.specificity = $specificity,
            i.category_key = $category_key,
            i.description = $description,
            i.method_id = $method_id
    """, {
        "intervention_id": intervention_id,
        "name":            tool_name,
        "specificity":     tool.get("specificity") or "",
        "category_key":    tool.get("category_key") or [],
        "description":     tool.get("description") or "",
        "method_id":       tool.get("method_id") or "",
    })

    findings_written = 0

    for ev in tool.get("evidence") or []:
        source_title = (ev.get("source_paper") or "").strip()
        if not source_title:
            continue

        title_key = source_title.lower()[:80]
        paper_key = paper_title_index.get(title_key)

        if paper_key:
            # EVALUATES edge: Paper → Intervention
            session.run("""
                MATCH (i:Intervention {intervention_id: $intervention_id})
                OPTIONAL MATCH (p:Paper {doi: $doi})
                OPTIONAL MATCH (p2:Paper {title: $title})
                WITH i, COALESCE(p, p2) AS paper
                WHERE paper IS NOT NULL
                MERGE (paper)-[r:EVALUATES]->(i)
                SET r.use_case = $use_case,
                    r.study_design = $study_design,
                    r.original_name = $original_name
            """, {
                "intervention_id": intervention_id,
                "doi":             paper_key if paper_key.startswith("10.") else None,
                "title":           paper_key if not paper_key.startswith("10.") else source_title,
                "use_case":        ev.get("use_case") or "",
                "study_design":    ev.get("source_paper_design") or "",
                "original_name":   ev.get("original_name_in_paper") or "",
            })

        for idx, finding in enumerate(ev.get("findings") or []):
            import hashlib
            finding_id = "finding_" + hashlib.sha256(f"{tool_name}|{source_title}|{idx}".encode()).hexdigest()[:12]

            session.run("""
                MERGE (f:EmpiricalFinding {finding_id: $finding_id})
                SET f.outcome_category   = $outcome_category,
                    f.finding_type       = $finding_type,
                    f.direction          = $direction,
                    f.finding_summary    = $finding_summary,
                    f.measure            = $measure,
                    f.effect_size        = $effect_size,
                    f.confidence_interval = $confidence_interval,
                    f.sample_size        = $sample_size,
                    f.study_count        = $study_count,
                    f.source_paper       = $source_paper
            """, {
                "finding_id":          finding_id,
                "outcome_category":    finding.get("outcome_category") or "",
                "finding_type":        finding.get("finding_type") or "",
                "direction":           finding.get("direction") or "",
                "finding_summary":     finding.get("finding_summary") or "",
                "measure":             finding.get("measure") or "not_reported",
                "effect_size":         finding.get("effect_size") or "not_reported",
                "confidence_interval": finding.get("confidence_interval") or "not_reported",
                "sample_size":         str(finding.get("sample_size") or "not_reported"),
                "study_count":         str(finding.get("study_count") or "not_reported"),
                "source_paper":        source_title,
            })

            # Link Finding → Intervention
            session.run("""
                MATCH (i:Intervention {intervention_id: $intervention_id})
                MATCH (f:EmpiricalFinding {finding_id: $finding_id})
                MERGE (i)-[:PRODUCES_FINDING]->(f)
            """, {"intervention_id": intervention_id, "finding_id": finding_id})

            # Upsert Outcome node + TARGETS_OUTCOME edge
            outcome_cat = finding.get("outcome_category") or ""
            if outcome_cat:
                session.run("""
                    MERGE (o:Outcome {name: $name})
                    WITH o
                    MATCH (f:EmpiricalFinding {finding_id: $finding_id})
                    MERGE (f)-[:TARGETS_OUTCOME]->(o)
                """, {"name": outcome_cat, "finding_id": finding_id})

            # Link Paper → Finding (if paper exists)
            if paper_key:
                session.run("""
                    MERGE (f:EmpiricalFinding {finding_id: $finding_id})
                    WITH f
                    OPTIONAL MATCH (p:Paper {doi: $doi})
                    OPTIONAL MATCH (p2:Paper {title: $title})
                    WITH f, COALESCE(p, p2) AS paper
                    WHERE paper IS NOT NULL
                    MERGE (paper)-[:REPORTS_FINDING]->(f)
                """, {
                    "finding_id": finding_id,
                    "doi":        paper_key if paper_key.startswith("10.") else None,
                    "title":      paper_key if not paper_key.startswith("10.") else source_title,
                })

                # Paper → Outcome (FOCUSES_ON_OUTCOME) via this finding's outcome
                if outcome_cat:
                    session.run("""
                        MATCH (o:Outcome {name: $name})
                        OPTIONAL MATCH (p:Paper {doi: $doi})
                        OPTIONAL MATCH (p2:Paper {title: $title})
                        WITH o, COALESCE(p, p2) AS paper
                        WHERE paper IS NOT NULL
                        MERGE (paper)-[:FOCUSES_ON_OUTCOME]->(o)
                    """, {
                        "name":  outcome_cat,
                        "doi":   paper_key if paper_key.startswith("10.") else None,
                        "title": paper_key if not paper_key.startswith("10.") else source_title,
                    })

            findings_written += 1

    return findings_written


def write_cites_edges(session, chase_network: dict, dry_run: bool = False) -> int:
    """Write CITES edges from the chase network. Returns edge count written."""
    if not chase_network:
        return 0

    edges = chase_network.get("edges") or []
    nodes = {n.get("doi") or n.get("title", "").lower()[:80]: n
             for n in (chase_network.get("nodes") or [])}

    written = 0
    skipped = 0

    for edge in edges:
        src_key = edge.get("source")
        tgt_key = edge.get("target")
        level   = edge.get("citation_level", 1)
        context = edge.get("citation_context") or ""
        hop     = edge.get("hop", 1)

        if not src_key or not tgt_key:
            continue

        # Get DOI vs title for source and target
        src_node = nodes.get(src_key, {})
        tgt_node = nodes.get(tgt_key, {})

        src_doi   = src_node.get("doi") or (src_key if src_key.startswith("10.") else None)
        src_title = src_node.get("title") or (src_key if not src_key.startswith("10.") else "")
        tgt_doi   = tgt_node.get("doi") or (tgt_key if tgt_key.startswith("10.") else None)
        tgt_title = tgt_node.get("title") or (tgt_key if not tgt_key.startswith("10.") else "")

        if dry_run:
            written += 1
            continue

        try:
            # Only write CITES edge if BOTH nodes already exist as corpus Paper nodes.
            # No stub/lightweight nodes for non-corpus papers — pre-2023 ancestors and
            # non-corpus papers are handled ephemerally by the Citation Connector Agent
            # (A8) at run time via live S2 lookups.
            session.run("""
                OPTIONAL MATCH (src:Paper {doi: $src_doi})
                OPTIONAL MATCH (src2:Paper {title: $src_title})
                OPTIONAL MATCH (tgt:Paper {doi: $tgt_doi})
                OPTIONAL MATCH (tgt2:Paper {title: $tgt_title})
                WITH COALESCE(src, src2) AS s, COALESCE(tgt, tgt2) AS t
                WHERE s IS NOT NULL AND t IS NOT NULL
                MERGE (s)-[r:CITES]->(t)
                SET r.citation_level = $level,
                    r.citation_context = $context,
                    r.hop = $hop
            """, {
                "src_doi":   src_doi,
                "src_title": src_title,
                "tgt_doi":   tgt_doi,
                "tgt_title": tgt_title,
                "level":     level,
                "context":   context,
                "hop":       float(hop),
            })
            written += 1
        except Exception as e:
            skipped += 1
            if skipped <= 5:
                print(f"  [warn] edge write failed: {e}")

    return written


# ── Main ───────────────────────────────────────────────────────────────────────

def main(
    papers_dirs: list[Path],
    chase_path: Path,
    skip_wipe: bool = False,
    dry_run: bool = False,
) -> None:
    print(f"\n{'='*60}")
    print(f"Neo4j KG Writer — {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"{'='*60}")
    print(f"Input dirs: {[str(d) for d in papers_dirs]}")
    print(f"Chase net:  {chase_path}")

    # ── Load all data ──────────────────────────────────────────────────────────
    print("\nLoading corpus ...")
    papers = load_papers(papers_dirs)
    print(f"  {len(papers)} papers (deduplicated)")

    tools  = load_tools_final()
    print(f"  {len(tools)} tools from tools_final")

    chase  = load_chase_network(chase_path)
    edge_count = len(chase.get("edges") or [])
    print(f"  {edge_count} CITES edges in chase network")

    if dry_run:
        print("\n[dry-run] Would write:")
        writeable = [p for p in papers
                     if p.get("verdict") not in SKIP_VERDICTS
                     and p.get("quality_tier") not in SKIP_QUALITY]
        skipped   = len(papers) - len(writeable)
        print(f"  {len(writeable)} Paper nodes ({skipped} skipped — red/framework_only)")
        print(f"  {len(tools)} Intervention nodes")
        findings = sum(
            sum(len(ev.get("findings") or []) for ev in t.get("evidence") or [])
            for t in tools
        )
        print(f"  ~{findings} EmpiricalFinding nodes")
        print(f"  {edge_count} CITES edges")
        print("\nDry-run complete — no changes made.")
        return

    # ── Connect to Neo4j ───────────────────────────────────────────────────────
    try:
        from neo4j import GraphDatabase
        driver = get_driver()
    except Exception as e:
        print(f"\n[error] Neo4j connection failed: {e}")
        print("Check NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD in .env")
        return

    database = os.environ.get("NEO4J_DATABASE", "neo4j")
    added_date = datetime.now().isoformat()

    with driver.session(database=database) as session:

        # ── Step 0: Wipe ───────────────────────────────────────────────────────
        if not skip_wipe:
            wipe_graph(session)
        else:
            print("\n[skip-wipe] Upserting into existing graph.")

        ensure_constraints(session)

        # ── Step 1: Paper nodes ────────────────────────────────────────────────
        print(f"\nWriting {len(papers)} Paper nodes ...")
        paper_keys_written: set[str] = set()
        title_to_key: dict[str, str] = {}   # lowercase title[:80] → merge key
        skipped_papers = 0

        for paper in papers:
            key = write_paper_node(session, paper, added_date)
            if key is None:
                skipped_papers += 1
                continue
            paper_keys_written.add(key)
            title_key = (paper.get("title") or "").strip().lower()[:80]
            title_to_key[title_key] = key

        print(f"  Wrote {len(paper_keys_written)} Paper nodes ({skipped_papers} skipped)")

        # ── Step 2: Intervention + EVALUATES + EmpiricalFinding ───────────────
        print(f"\nWriting {len(tools)} Intervention nodes + findings ...")
        total_findings = 0
        for tool in tools:
            n = write_tool_graph(session, tool, title_to_key)
            total_findings += n
        print(f"  Wrote {len(tools)} Intervention nodes, {total_findings} EmpiricalFinding nodes")

        # ── Step 3: CITES edges ────────────────────────────────────────────────
        if edge_count > 0:
            print(f"\nWriting {edge_count} CITES edges ...")
            written_edges = write_cites_edges(session, chase)
            print(f"  Wrote {written_edges} CITES edges")
        else:
            print("\n[skip] No CITES edges — run citation_chaser.py first")

        # ── Step 4: Clean up stale Outcome nodes (no TARGETS_OUTCOME edges) ────
        print("\nCleaning up stale Outcome nodes ...")
        result = session.run("""
            MATCH (o:Outcome)
            WHERE NOT (o)<-[:TARGETS_OUTCOME]-()
            WITH count(o) AS cnt
            RETURN cnt
        """).single()
        stale_count = result["cnt"] if result else 0
        if stale_count > 0:
            session.run("""
                MATCH (o:Outcome)
                WHERE NOT (o)<-[:TARGETS_OUTCOME]-()
                DETACH DELETE o
            """)
            print(f"  Deleted {stale_count} stale Outcome nodes")
        else:
            print("  No stale Outcome nodes found")

    driver.close()

    print(f"\n{'='*60}")
    print(f"KG rebuild complete")
    print(f"  Paper nodes:         {len(paper_keys_written)}")
    print(f"  Intervention nodes:  {len(tools)}")
    print(f"  EmpiricalFindings:   {total_findings}")
    print(f"  CITES edges:         {written_edges if edge_count > 0 else 0}")
    print(f"  Stale outcomes del:  {stale_count}")
    print(f"{'='*60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Full Neo4j KG rebuild from corpus")
    parser.add_argument(
        "--papers-dirs", type=Path, nargs="+",
        default=DEFAULT_PAPERS_DIRS,
        help="Corpus directories to load papers from",
    )
    parser.add_argument(
        "--chase-network", type=Path,
        default=DEFAULT_CHASE,
        help=f"Path to _chase_network.json (default: {DEFAULT_CHASE})",
    )
    parser.add_argument(
        "--skip-wipe", action="store_true",
        help="Skip the DETACH DELETE wipe — upsert into existing graph instead",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be written without touching Neo4j",
    )
    args = parser.parse_args()
    main(args.papers_dirs, args.chase_network, args.skip_wipe, args.dry_run)
