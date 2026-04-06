"""citation_chaser.py — 1.5-hop L2/L3 citation traversal on ingested KG papers.

Starting from papers already in the corpus (seed papers), this script:

  Pre-hop: For seed papers with NO citations in their JSON (legacy papers),
           look them up on Semantic Scholar and fetch their reference list.
           References are mapped to L1/L2/L3 via S2 `intents` field.
           Only L2+L3 refs are kept for traversal.

  Hop 1:   Collect all L2 + L3 citations from each seed paper.
           Look each one up via Semantic Scholar (by DOI, then title fallback).

  Hop 1.5: For every hop-1 paper published 2023+, fetch its own reference list
           from Semantic Scholar. These are lightweight nodes — no full extraction.
           Semantic Scholar's `intents` field is mapped to our L1/L2/L3 taxonomy
           as a best-effort approximation.

Supports multiple input directories (e.g. merging legacy + SCALE + query-ingest corpora).
Outputs are written to --output-dir.

  _chase_network.json  — full citation graph: nodes (seed, hop1, hop1_5) + edges
  _ingest_queue.json   — 2023+ papers not yet in corpus → candidates for next ingest

Usage:
    python citation_chaser.py
    python citation_chaser.py --papers-dir ingested_papers/2026-04-01 ingested_papers/legacy
    python citation_chaser.py --output-dir ingested_papers/merged --dry-run
"""

import asyncio
import json
import os
import re
import sys
import argparse
from datetime import date
from pathlib import Path
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(REPO_ROOT / ".env")
sys.path.insert(0, str(REPO_ROOT / "deep-research-src"))

import httpx

# ── Config ─────────────────────────────────────────────────────────────────────

MIN_YEAR_KG    = 2023   # papers below this year are lightweight nodes only, never KG
S2_FIELDS      = "title,authors,year,venue,externalIds,openAccessPdf,abstract"
S2_REF_FIELDS  = "title,authors,year,externalIds,intents,isInfluential"
S2_BASE        = "https://api.semanticscholar.org/graph/v1"
CROSSREF_BASE  = "https://api.crossref.org/works"
_SS_API_KEY    = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
_CONTACT_EMAIL = "aly.moosa@gatesfoundation.org"
_HEADERS       = {"User-Agent": f"EduResearchTool/2.0 (academic citation analysis; contact: {_CONTACT_EMAIL})"}
if _SS_API_KEY:
    _HEADERS["x-api-key"] = _SS_API_KEY
_CR_HEADERS    = {"User-Agent": f"EduResearchTool/2.0 (mailto:{_CONTACT_EMAIL})"}
# With API key: 1 req/sec. Without: 8s/req (anonymous tier).

# Map Semantic Scholar citation intents → our L1/L2/L3 taxonomy (best-effort)
# S2 intents: "background", "methodology", "result"
_INTENT_TO_LEVEL: dict[str, int] = {
    "background":  2,   # conceptual/grounded → L2
    "methodology": 3,   # foundational → L3
    "result":      1,   # referential → L1
}


# ── Semantic Scholar helpers ───────────────────────────────────────────────────

_s2_consecutive_429s = 0   # global counter — triggers hard cooldown on storms

async def _s2_get(client: httpx.AsyncClient, url: str, params: dict, sem: asyncio.Semaphore) -> dict | None:
    """Rate-limited GET with 429-storm detection.
    - Normal throttle: 8s between requests (anonymous tier: ~7 req/min, well under 100/5min)
    - Single 429: sleep 60s and retry (full window reset)
    - Storm (3+ consecutive 429s globally): hard 5-minute cooldown before next attempt
    """
    global _s2_consecutive_429s
    _throttle = 2.0 if _SS_API_KEY else 8.0

    # If we're in a storm, wait for the window to fully clear before acquiring semaphore
    if _s2_consecutive_429s >= 3:
        cooldown = 300  # 5 minutes — full S2 rate window
        print(f"  [s2] 429 storm detected ({_s2_consecutive_429s} consecutive) — cooling down {cooldown}s")
        await asyncio.sleep(cooldown)
        _s2_consecutive_429s = 0

    async with sem:
        for attempt in range(3):
            try:
                resp = await client.get(url, params=params)
                if resp.status_code == 429:
                    _s2_consecutive_429s += 1
                    wait = 60 * (attempt + 1)  # 60s, 120s, 180s
                    print(f"  [s2] 429 rate limit — sleeping {wait}s (attempt {attempt+1}/3, consecutive={_s2_consecutive_429s})")
                    await asyncio.sleep(wait)
                    continue
                if resp.status_code == 403:
                    print(f"  [s2] 403 Forbidden — check SEMANTIC_SCHOLAR_API_KEY in .env")
                    await asyncio.sleep(_throttle)
                    return None
                if resp.status_code == 404:
                    await asyncio.sleep(_throttle)
                    return None
                resp.raise_for_status()
                data = resp.json()
                _s2_consecutive_429s = 0   # successful request — reset storm counter
                await asyncio.sleep(_throttle)
                return data
            except Exception as e:
                print(f"  [s2] error attempt {attempt}: {type(e).__name__}: {str(e)[:80]}")
                if attempt == 2:
                    await asyncio.sleep(_throttle)
                    return None
                await asyncio.sleep(2 ** attempt)
        # All retries exhausted — still throttle before releasing semaphore
        await asyncio.sleep(_throttle)
    return None


async def lookup_by_doi(doi: str, client: httpx.AsyncClient, sem: asyncio.Semaphore) -> dict | None:
    """Look up a paper by DOI. Returns normalized metadata dict or None."""
    data = await _s2_get(client, f"{S2_BASE}/paper/DOI:{doi}", {"fields": S2_FIELDS}, sem)
    return _normalize_s2_paper(data) if data else None


_cr_sem = asyncio.Semaphore(5)  # cap concurrent CrossRef calls — avoids pool exhaustion

async def _crossref_resolve_doi(title: str, client: httpx.AsyncClient) -> str | None:
    """Resolve a title to a DOI via CrossRef (polite pool — no throttle needed).
    Returns a DOI string if a high-confidence match is found, else None.
    Never hits the S2 /paper/search endpoint.
    """
    try:
        params = {
            "query.bibliographic": title[:120],
            "rows": 1,
            "mailto": _CONTACT_EMAIL,
        }
        async with _cr_sem:
            resp = await client.get(CROSSREF_BASE, params=params, headers=_CR_HEADERS)
        if resp.status_code != 200:
            return None
        items = resp.json().get("message", {}).get("items", [])
        if not items:
            return None
        item = items[0]
        result_title = (item.get("title") or [""])[0]
        doi = item.get("DOI", "").strip().lower() or None
        if not doi:
            return None
        # Title similarity gate — CrossRef always returns something, even if wrong
        if _title_sim(title, result_title) < 0.5:
            return None
        return doi
    except Exception:
        return None


async def lookup_by_title(title: str, client: httpx.AsyncClient, sem: asyncio.Semaphore) -> dict | None:
    """Resolve title → DOI via CrossRef, then fetch from S2 by DOI.
    Avoids S2 /paper/search entirely (which is separately throttled).
    """
    doi = await _crossref_resolve_doi(title, client)
    if not doi:
        return None
    return await lookup_by_doi(doi, client, sem)


async def fetch_references(s2_id: str, client: httpx.AsyncClient, sem: asyncio.Semaphore) -> list[dict]:
    """Fetch the references of a paper (for hop 1.5). Returns list of edge dicts."""
    data = await _s2_get(
        client,
        f"{S2_BASE}/paper/{s2_id}/references",
        {"fields": S2_REF_FIELDS, "limit": 100},
        sem,
    )
    if not data:
        return []

    edges = []
    for ref in data.get("data") or []:
        cited = ref.get("citedPaper") or {}
        if not cited.get("title"):
            continue
        intents = ref.get("intents") or []
        # Map intents to citation level: take the highest (most specific) intent
        level = 1
        for intent in intents:
            mapped = _INTENT_TO_LEVEL.get(intent, 1)
            level = max(level, mapped)
        is_influential = ref.get("isInfluential", False)
        if is_influential and level < 2:
            level = 2  # S2 marks it influential → at least L2

        doi = ((cited.get("externalIds") or {}).get("DOI") or "").strip().lower() or None
        edges.append({
            "title": cited.get("title", ""),
            "doi": doi,
            "year": cited.get("year"),
            "s2_id": cited.get("paperId"),
            "authors": _fmt_authors(cited.get("authors") or []),
            "citation_level": level,
            "citation_context": None,   # not available from S2 references API
        })
    return edges


def _normalize_s2_paper(p: dict) -> dict:
    """Normalize a raw S2 paper dict to our internal format."""
    doi = ((p.get("externalIds") or {}).get("DOI") or "").strip().lower() or None
    pdf_url = (p.get("openAccessPdf") or {}).get("url") or ""
    return {
        "s2_id":    p.get("paperId") or "",
        "title":    p.get("title") or "",
        "year":     p.get("year"),
        "venue":    p.get("venue") or "",
        "doi":      doi,
        "authors":  _fmt_authors(p.get("authors") or []),
        "abstract": (p.get("abstract") or "")[:300],
        "pdf_url":  pdf_url,
    }


def _fmt_authors(authors: list) -> str:
    names = [a.get("name", "") for a in authors[:3]]
    suffix = " et al." if len(authors) > 3 else ""
    return ", ".join(n for n in names if n) + suffix


def _title_sim(a: str, b: str) -> float:
    """Rough Jaccard similarity on word sets."""
    wa = set(re.sub(r"[^a-z0-9 ]", "", a.lower()).split())
    wb = set(re.sub(r"[^a-z0-9 ]", "", b.lower()).split())
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


def _doi_key(doi: str | None) -> str | None:
    """Normalize a DOI to a consistent lowercase key."""
    if not doi:
        return None
    return re.sub(r"\s+", "", doi.strip().lower())


# ── Seed paper loading ─────────────────────────────────────────────────────────

def load_seed_papers(papers_dirs: list[Path]) -> list[dict]:
    """Load all paper JSON files from one or more corpus directories.

    Deduplicates across directories by DOI (then title). Returns list of dicts:
      doi, title, year, file, l2l3_citations, needs_fetch

    needs_fetch=True  → paper has no citations in JSON (legacy papers).
                        Pre-hop will fetch their reference list from S2.
    needs_fetch=False → paper has citations extracted by pdf_extractor_v2.
                        Normal Hop 1 path.
    """
    seeds = []
    seen_dois: set[str] = set()
    seen_titles: set[str] = set()

    for papers_dir in papers_dirs:
        if not papers_dir.exists():
            print(f"  [warn] papers-dir not found, skipping: {papers_dir}")
            continue
        for fp in sorted(papers_dir.glob("*.json")):
            if fp.name.startswith("_"):
                continue
            try:
                data = json.loads(fp.read_text())
            except Exception:
                continue
            if not isinstance(data, dict):
                continue

            doi = _doi_key(data.get("doi"))
            title = data.get("title", "").strip()
            title_key = title.lower()[:80]
            year = data.get("year")

            # Deduplicate
            if doi and doi in seen_dois:
                continue
            if title_key and title_key in seen_titles:
                continue
            if doi:
                seen_dois.add(doi)
            if title_key:
                seen_titles.add(title_key)

            citations = data.get("citations") or []
            l2l3 = [
                c for c in citations
                if isinstance(c, dict) and c.get("citation_level", 1) >= 2
            ]
            needs_fetch = len(citations) == 0  # legacy paper — no citations extracted

            seeds.append({
                "doi":            doi,
                "title":          title,
                "year":           year,
                "file":           fp.name,
                "source_dir":     str(papers_dir),
                "l2l3_citations": l2l3,
                "needs_fetch":    needs_fetch,
            })

    return seeds


# ── Core traversal ─────────────────────────────────────────────────────────────

async def chase(
    papers_dirs: list[Path],
    output_dir: Path,
    concurrency: int = 1,
    dry_run: bool = False,
    skip_prehop: bool = False,
) -> tuple[dict, list[dict]]:
    """
    Run 1.5-hop citation traversal across one or more corpus directories.

    Returns:
        network  — dict with nodes and edges lists
        ingest_queue — list of 2023+ papers not yet in corpus
    """
    seeds = load_seed_papers(papers_dirs)
    print(f"\nLoaded {len(seeds)} seed papers from {len(papers_dirs)} director(ies)")

    needs_fetch_count = sum(1 for s in seeds if s["needs_fetch"])
    has_citations_count = len(seeds) - needs_fetch_count
    print(f"  {has_citations_count} with extracted citations, {needs_fetch_count} legacy (needs S2 ref fetch)")

    # Existing corpus DOI set (so we don't re-queue them)
    corpus_dois: set[str] = {s["doi"] for s in seeds if s["doi"]}
    corpus_titles: set[str] = {s["title"].lower()[:80] for s in seeds}

    total_l2l3 = sum(len(s["l2l3_citations"]) for s in seeds)
    print(f"Total L2/L3 citations to chase (pre-fetch): {total_l2l3}")

    if dry_run:
        seeds = seeds[:3]
        print("[dry-run] capped to first 3 seed papers")

    sem = asyncio.Semaphore(concurrency)
    nodes: dict[str, dict] = {}   # key → node dict (key = doi or title_key)
    edges: list[dict] = []

    # Add seed papers as nodes
    for s in seeds:
        key = s["doi"] or s["title"].lower()[:80]
        nodes[key] = {
            "doi":       s["doi"],
            "title":     s["title"],
            "year":      s["year"],
            "node_type": "seed",
            "in_corpus": True,
        }

    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, headers=_HEADERS) as client:

        # ── Pre-hop: Fetch S2 refs for legacy seeds with no citations ──────────
        legacy_seeds = [s for s in seeds if s["needs_fetch"]]
        if skip_prehop:
            print(f"\n── Pre-hop: SKIPPED (--skip-prehop) — {len(legacy_seeds)} legacy seeds will contribute no citations ──")
            legacy_seeds = []
        if legacy_seeds:
            print(f"\n── Pre-hop: Fetching S2 references for {len(legacy_seeds)} legacy seeds ──")

            # Step 1: resolve each legacy seed to an S2 paper ID
            resolve_tasks = []
            for s in legacy_seeds:
                if s["doi"]:
                    resolve_tasks.append(lookup_by_doi(s["doi"], client, sem))
                else:
                    resolve_tasks.append(lookup_by_title(s["title"], client, sem))
            resolve_results = await asyncio.gather(*resolve_tasks)

            # Step 2: fetch references for each resolved seed
            ref_tasks = []
            ref_seed_indices = []
            for i, (seed, resolved) in enumerate(zip(legacy_seeds, resolve_results)):
                if resolved is None:
                    print(f"  [pre-hop] not found on S2: {seed['title'][:60]}")
                    continue
                s2_id = resolved.get("s2_id") or (f"DOI:{resolved['doi']}" if resolved.get("doi") else None)
                if not s2_id:
                    continue
                ref_tasks.append(fetch_references(s2_id, client, sem))
                ref_seed_indices.append(i)

            ref_results = await asyncio.gather(*ref_tasks)

            # Step 3: inject L2/L3 refs back into each legacy seed's l2l3_citations
            injected_total = 0
            for idx, ref_list in zip(ref_seed_indices, ref_results):
                seed = legacy_seeds[idx]
                l2l3_from_s2 = [r for r in ref_list if r["citation_level"] >= 2]
                seed["l2l3_citations"] = l2l3_from_s2
                injected_total += len(l2l3_from_s2)
                print(f"  [pre-hop] {seed['title'][:50]}: {len(l2l3_from_s2)} L2/L3 refs injected")

            total_l2l3_after = sum(len(s["l2l3_citations"]) for s in seeds)
            print(f"  Pre-hop complete: injected {injected_total} L2/L3 citations from S2")
            print(f"  Total L2/L3 citations to chase (post-fetch): {total_l2l3_after}")

        # ── Hop 1: Resolve all L2/L3 citations ────────────────────────────────
        print("\n── Hop 1: Resolving L2/L3 citations via Semantic Scholar ──")

        hop1_tasks = []
        hop1_meta  = []   # parallel list of (seed_doi_or_title, citation_dict)

        for seed in seeds:
            seed_key = seed["doi"] or seed["title"].lower()[:80]
            for c in seed["l2l3_citations"]:
                cit_doi = _doi_key(c.get("doi"))
                cit_title = (c.get("title") or "").strip()
                hop1_tasks.append(
                    lookup_by_doi(cit_doi, client, sem) if cit_doi
                    else lookup_by_title(cit_title, client, sem)
                )
                hop1_meta.append({
                    "seed_key":        seed_key,
                    "citation_level":  c.get("citation_level", 2),
                    "citation_context":c.get("citation_context"),
                    "orig_doi":        cit_doi,
                    "orig_title":      cit_title,
                })

        _hop1_total = len(hop1_tasks)
        _hop1_done = 0

        async def _tracked_hop1(coro):
            nonlocal _hop1_done
            result = await coro
            _hop1_done += 1
            if _hop1_done % 50 == 0 or _hop1_done == _hop1_total:
                found_so_far = _hop1_done  # rough — final count comes after
                print(f"  [hop1] {_hop1_done}/{_hop1_total} resolved...", flush=True)
            return result

        hop1_results = await asyncio.gather(*[_tracked_hop1(t) for t in hop1_tasks])

        hop1_2023_plus: list[dict] = []   # nodes found in hop 1 that are 2023+

        for result, meta in zip(hop1_results, hop1_meta):
            if result is None:
                continue
            key = result["doi"] or result["title"].lower()[:80]
            if not key:
                continue

            in_corpus = (result["doi"] in corpus_dois) or (result["title"].lower()[:80] in corpus_titles)

            if key not in nodes:
                nodes[key] = {
                    "doi":       result["doi"],
                    "s2_id":     result.get("s2_id"),
                    "title":     result["title"],
                    "year":      result["year"],
                    "venue":     result["venue"],
                    "authors":   result["authors"],
                    "abstract":  result["abstract"],
                    "pdf_url":   result["pdf_url"],
                    "node_type": "hop1",
                    "in_corpus": in_corpus,
                }

            edges.append({
                "source":          meta["seed_key"],
                "target":          key,
                "citation_level":  meta["citation_level"],
                "citation_context":meta["citation_context"],
                "hop":             1,
            })

            year = result.get("year") or 0
            if year >= MIN_YEAR_KG and not in_corpus:
                hop1_2023_plus.append({**result, "node_key": key})

        hop1_found = sum(1 for n in nodes.values() if n["node_type"] == "hop1")
        print(f"  Found {hop1_found} hop-1 papers ({len(hop1_2023_plus)} are 2023+ and not in corpus)")

        # ── Hop 1.5: References of 2023+ hop-1 papers ─────────────────────────
        print("\n── Hop 1.5: Fetching references of 2023+ hop-1 papers ──")

        hop1_5_tasks = []
        hop1_5_sources = []

        for p in hop1_2023_plus:
            s2_id = p.get("s2_id")
            if not s2_id:
                # Try to get S2 ID by DOI
                if p.get("doi"):
                    s2_id = f"DOI:{p['doi']}"
                else:
                    continue
            hop1_5_tasks.append(fetch_references(s2_id, client, sem))
            hop1_5_sources.append(p["node_key"])

        hop1_5_results = await asyncio.gather(*hop1_5_tasks)

        for ref_list, source_key in zip(hop1_5_results, hop1_5_sources):
            for ref in ref_list:
                key = ref.get("doi") or ref["title"].lower()[:80]
                if not key:
                    continue
                if key not in nodes:
                    in_corpus = (ref.get("doi") in corpus_dois) if ref.get("doi") else False
                    nodes[key] = {
                        "doi":       ref.get("doi"),
                        "s2_id":     ref.get("s2_id"),
                        "title":     ref["title"],
                        "year":      ref.get("year"),
                        "authors":   ref.get("authors", ""),
                        "node_type": "hop1_5",
                        "in_corpus": in_corpus,
                    }
                edges.append({
                    "source":          source_key,
                    "target":          key,
                    "citation_level":  ref["citation_level"],
                    "citation_context":ref.get("citation_context"),
                    "hop":             1.5,
                })

        hop1_5_found = sum(1 for n in nodes.values() if n["node_type"] == "hop1_5")
        print(f"  Found {hop1_5_found} hop-1.5 papers")

    # ── Build ingest queue: 2023+ papers not yet in corpus ────────────────────
    ingest_queue = []
    for key, node in nodes.items():
        if node.get("in_corpus"):
            continue
        year = node.get("year") or 0
        if year < MIN_YEAR_KG:
            continue
        ingest_queue.append({
            "doi":       node.get("doi"),
            "title":     node["title"],
            "year":      year,
            "authors":   node.get("authors", ""),
            "venue":     node.get("venue", ""),
            "pdf_url":   node.get("pdf_url", ""),
            "node_type": node["node_type"],
            "s2_id":     node.get("s2_id"),
        })

    ingest_queue.sort(key=lambda x: x["year"], reverse=True)

    network = {
        "run_date":       str(date.today()),
        "papers_dirs":    [str(d) for d in papers_dirs],
        "seed_count":     len(seeds),
        "hop1_found":     hop1_found,
        "hop1_5_found":   hop1_5_found,
        "total_nodes":    len(nodes),
        "total_edges":    len(edges),
        "ingest_candidates": len(ingest_queue),
        "nodes": list(nodes.values()),
        "edges": edges,
    }

    return network, ingest_queue


# ── Output helpers ─────────────────────────────────────────────────────────────

def _print_summary(network: dict, ingest_queue: list[dict]) -> None:
    print(f"\n{'='*60}")
    print(f"Citation chase complete")
    print(f"  Seed papers:        {network['seed_count']}")
    print(f"  Hop-1 papers found: {network['hop1_found']}")
    print(f"  Hop-1.5 papers:     {network['hop1_5_found']}")
    print(f"  Total nodes:        {network['total_nodes']}")
    print(f"  Total edges:        {network['total_edges']}")
    print(f"  Ingest candidates:  {network['ingest_candidates']} (2023+, not in corpus)")

    if ingest_queue:
        print(f"\nTop ingest candidates (2023+):")
        for p in ingest_queue[:15]:
            hop = p["node_type"]
            print(f"  [{hop}] ({p['year']}) {p['title'][:65]}")
            if p.get("doi"):
                print(f"          doi: {p['doi']}")

    # Edge level distribution
    from collections import Counter
    level_counts = Counter(e["citation_level"] for e in network["edges"])
    hop_counts   = Counter(str(e["hop"]) for e in network["edges"])
    print(f"\nEdge citation levels: {dict(sorted(level_counts.items()))}")
    print(f"Edge by hop:          {dict(sorted(hop_counts.items()))}")


# ── Main ───────────────────────────────────────────────────────────────────────

def _load_existing_network(output_dir: Path) -> dict | None:
    """Load existing _chase_network.json if it exists. Returns None if missing or corrupt."""
    network_path = output_dir / "_chase_network.json"
    if not network_path.exists():
        return None
    try:
        data = json.loads(network_path.read_text())
        if "nodes" in data and "edges" in data:
            return data
    except Exception as e:
        print(f"  [incremental] Warning: could not load existing network: {e}")
    return None


def _merge_networks(existing: dict, new_network: dict) -> dict:
    """Merge new_network nodes+edges into existing network. Deduplicates by node key."""
    # Index existing nodes by key (doi or title_key)
    existing_nodes: dict[str, dict] = {
        (n.get("doi") or n["title"].lower()[:80]): n
        for n in existing.get("nodes", [])
        if n.get("title") or n.get("doi")
    }
    existing_edges: list[dict] = existing.get("edges", [])
    existing_edge_sigs: set[tuple] = {
        (e["source"], e["target"], e.get("hop", 1))
        for e in existing_edges
    }

    added_nodes = 0
    added_edges = 0

    for node in new_network.get("nodes", []):
        key = node.get("doi") or (node.get("title") or "").lower()[:80]
        if not key:
            continue
        if key not in existing_nodes:
            existing_nodes[key] = node
            added_nodes += 1

    for edge in new_network.get("edges", []):
        sig = (edge["source"], edge["target"], edge.get("hop", 1))
        if sig not in existing_edge_sigs:
            existing_edges.append(edge)
            existing_edge_sigs.add(sig)
            added_edges += 1

    print(f"  [incremental] Merged: +{added_nodes} nodes, +{added_edges} edges")

    merged = dict(existing)
    merged["nodes"] = list(existing_nodes.values())
    merged["edges"] = existing_edges
    merged["total_nodes"] = len(merged["nodes"])
    merged["total_edges"] = len(merged["edges"])
    merged["seed_count"] = existing.get("seed_count", 0) + new_network.get("seed_count", 0)
    merged["run_date"] = str(date.today())
    return merged


async def main(papers_dirs: list[Path], output_dir: Path, concurrency: int, dry_run: bool, incremental: bool, skip_prehop: bool) -> None:
    print(f"Citation chaser{'  [INCREMENTAL]' if incremental else ''}")
    print(f"  Input dirs:  {[str(d) for d in papers_dirs]}")
    print(f"  Output dir:  {output_dir}")
    print(f"  Concurrency: {concurrency} | MIN_YEAR_KG: {MIN_YEAR_KG} | dry_run: {dry_run}")
    key_status = f"ACTIVE (2s/req) key=...{_SS_API_KEY[-6:]}" if _SS_API_KEY else "anonymous (8s/req)"
    print(f"  S2 API key:  {key_status}")
    print(f"  Title→DOI:   CrossRef polite pool (mailto={_CONTACT_EMAIL})")

    existing_network = None
    known_seed_keys: set[str] = set()

    if incremental:
        existing_network = _load_existing_network(output_dir)
        if existing_network:
            # Build set of already-processed seed keys so we skip them
            known_seed_keys = {
                (n.get("doi") or (n.get("title") or "").lower()[:80])
                for n in existing_network.get("nodes", [])
                if n.get("node_type") == "seed"
            }
            print(f"  [incremental] Loaded existing network: "
                  f"{existing_network['total_nodes']} nodes, {existing_network['total_edges']} edges")
            print(f"  [incremental] Known seeds: {len(known_seed_keys)} — will skip these")
        else:
            print("  [incremental] No existing network found — running full chase")

    # Filter seeds to only new ones when running incrementally
    if incremental and known_seed_keys:
        all_seeds = load_seed_papers(papers_dirs)
        new_seeds = [
            s for s in all_seeds
            if (s["doi"] or s["title"].lower()[:80]) not in known_seed_keys
        ]
        print(f"  [incremental] New seeds to process: {len(new_seeds)} / {len(all_seeds)} total")
        if not new_seeds:
            print("  [incremental] Nothing new to chase — exiting.")
            return
        # Write new seeds to a temp dir for chase() to consume
        import tempfile, shutil
        tmp = Path(tempfile.mkdtemp(prefix="citation_chaser_inc_"))
        try:
            for s in new_seeds:
                src = Path(s["source_dir"]) / s["file"]
                shutil.copy(src, tmp / s["file"])
            network, ingest_queue = await chase([tmp], output_dir, concurrency=concurrency, dry_run=dry_run, skip_prehop=skip_prehop)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    else:
        network, ingest_queue = await chase(papers_dirs, output_dir, concurrency=concurrency, dry_run=dry_run, skip_prehop=skip_prehop)

    # Merge with existing network if incremental
    if incremental and existing_network:
        network = _merge_networks(existing_network, network)
        # Rebuild ingest queue from full merged network (exclude already-in-corpus nodes)
        merged_corpus_dois = {n.get("doi") for n in network["nodes"] if n.get("in_corpus") and n.get("doi")}
        ingest_queue = [
            {
                "doi": n.get("doi"), "title": n["title"], "year": n.get("year", 0),
                "authors": n.get("authors", ""), "venue": n.get("venue", ""),
                "pdf_url": n.get("pdf_url", ""), "node_type": n["node_type"],
                "s2_id": n.get("s2_id"),
            }
            for n in network["nodes"]
            if not n.get("in_corpus") and (n.get("year") or 0) >= MIN_YEAR_KG
        ]
        ingest_queue.sort(key=lambda x: x.get("year") or 0, reverse=True)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_network = output_dir / "_chase_network.json"
    out_queue   = output_dir / "_ingest_queue.json"

    out_network.write_text(json.dumps(network, indent=2))
    out_queue.write_text(json.dumps(ingest_queue, indent=2))

    _print_summary(network, ingest_queue)
    print(f"\nWrote: {out_network}")
    print(f"Wrote: {out_queue}")


if __name__ == "__main__":
    default_dir = Path(__file__).resolve().parent / "ingested_papers" / str(date.today())
    default_output = Path(__file__).resolve().parent / "ingested_papers" / "merged"

    parser = argparse.ArgumentParser(description="1.5-hop L2/L3 citation chaser")
    parser.add_argument(
        "--papers-dir", type=Path, nargs="+", default=[default_dir],
        help=f"One or more directories of ingested paper JSONs (default: {default_dir})",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=default_output,
        help=f"Directory to write _chase_network.json and _ingest_queue.json (default: {default_output})",
    )
    parser.add_argument(
        "--concurrency", type=int, default=1,
        help="Max concurrent S2 requests (default: 1 — anonymous S2 allows ~1 req/3s)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Process only first 3 seed papers for testing",
    )
    parser.add_argument(
        "--skip-prehop", action="store_true",
        help="Skip the pre-hop S2 reference fetch for legacy seeds (saves quota)",
    )
    parser.add_argument(
        "--incremental", action="store_true",
        help="Load existing _chase_network.json, chase only new seeds, merge results back in",
    )
    args = parser.parse_args()
    asyncio.run(main(args.papers_dir, args.output_dir, args.concurrency, args.dry_run, args.incremental, args.skip_prehop))
