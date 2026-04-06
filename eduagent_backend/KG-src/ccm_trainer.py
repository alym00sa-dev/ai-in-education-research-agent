"""ccm_trainer.py — Community Citation Model trainer for the AI-in-education KG.

Implements the core outputs of the Community Citation Model (Kojaku et al., 2025,
arXiv:2501.15552) on the citation chase network:

  u_j  (K=128)    — fastRP embeddings from the paper authors' own implementation
                    (Kojaku et al., community_citation_model repo, fastRP.py)
  cluster_id       — K-means on u_j vectors (faithful: CCM assigns clusters post-hoc on embeddings)
  η (fitness)      — Weighted PageRank (proxy for CCM's NCE-learned fitness; full NCE requires
                      per-citation timestamps which we don't have — only publication years)
  SB_coef          — Sleeping beauty coefficient: exact Ke et al. (2015) formula, ported from
                    (Kojaku et al., community_citation_model repo, utils.py)
  field_momentum   — Per-cluster: fraction of in-edges from 2024+ sources (our metric for A8)

Scores are written to Neo4j for corpus Paper nodes only (in_corpus=True).
Non-corpus nodes contribute to the graph structure but receive no Neo4j writes.

Usage:
    python3.13 ccm_trainer.py
    python3.13 ccm_trainer.py --dry-run
    python3.13 ccm_trainer.py --network-dir ingested_papers/merged
    python3.13 ccm_trainer.py --n-clusters 15 --window-size 5
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.cluster import KMeans


# ── fastRP — ported from Kojaku et al. community_citation_model/fastRP.py ─────
# Source: https://github.com/skojaku/community_citation_model (fastRP.py)
# Original authors: Sadamori Kojaku et al.

def _fastrp_inner(net, window_size, X, beta=-1):
    """Inner fastRP loop. net must be a scipy sparse matrix."""
    outdeg = np.array(net.sum(axis=1)).reshape(-1)
    indeg  = np.array(net.sum(axis=0)).reshape(-1)
    P = sparse.diags(1 / np.maximum(1, outdeg)) @ net
    L = sparse.diags(np.power(np.maximum(indeg.astype(float), 1.0), beta))
    X0 = X.copy()
    X1 = (P @ L) @ X.copy()
    h  = np.ones((net.shape[0], 1))
    h0 = h.copy()
    for _ in range(window_size):
        X = P @ X + X1
        h = P @ h + h0
    X = X + X0
    h = h + 1
    X = sparse.diags(1.0 / np.maximum(np.array(h).reshape(-1), 1e-8)) @ X
    return X


def fastRP(net, dim, window_size, beta=-1, s=3.0, edge_direction=False, seed=42):
    """Fast Random Projection embedding (Kojaku et al., fastRP.py).

    Args:
        net:          scipy sparse adjacency matrix (n × n), values = edge weights
        dim:          embedding dimension (K=128 for CCM)
        window_size:  number of propagation steps (captures k-hop neighbourhood)
        beta:         degree normalisation (-1 = strongest, 0 = none)
        edge_direction: if True, returns (emb_out, emb_in) for directed graphs
        seed:         random seed for reproducibility
    Returns:
        ndarray (n, dim), or tuple (emb_out, emb_in) if edge_direction=True
    """
    rng = np.random.default_rng(seed)
    n = net.shape[0]
    X = rng.standard_normal((n, dim))
    X = np.einsum("ij,i->ij", X, 1 / np.linalg.norm(X, axis=1))
    emb = _fastrp_inner(net, window_size, X.copy(), beta=beta)
    if edge_direction:
        emb_in = _fastrp_inner(sparse.csr_matrix(net.T), window_size, X.copy(), beta=beta)
        return emb, emb_in
    return emb


# ── Sleeping Beauty coefficient — ported from Kojaku et al. utils.py ──────────
# Source: https://github.com/skojaku/community_citation_model (utils.py)
# Original authors: Sadamori Kojaku et al.
# Based on: Ke et al. (2015) "Defining and identifying Sleeping Beauties in science"

def calc_SB_coefficient(net, t0):
    """Calculate sleeping beauty coefficient and awakening time per paper.

    Args:
        net: scipy sparse citation matrix (citing × cited), binary or weighted
        t0:  array of publication years (length n_nodes); NaN for unknown years
    Returns:
        pd.DataFrame with columns [paper_id, SB_coef, awakening_time, t0]
        Only papers with ≥1 citation in the network are included.
    """
    def _sb_for_paper(dts, dct):
        T  = int(np.max(dts) + 1)
        ct = np.bincount(dts.astype(int), weights=dct, minlength=T)
        t_m   = np.argmax(ct)
        ct_m  = np.max(ct)
        if t_m == 0:
            return 0, 0
        c0 = ct[0]
        m  = (ct_m - c0) / t_m
        ct_slice = ct[:t_m]
        t  = np.arange(len(ct_slice))
        B  = np.sum((m * t + c0 - ct_slice) / np.maximum(1, ct_slice))
        d  = (ct_m - c0) * t - t_m * ct_slice + t_m * c0
        td = np.argmax(np.abs(d))
        return B, td

    source, target, _ = sparse.find(net)
    nr = int(np.maximum(np.max(source), np.max(target)) + 1)
    t0_arr = np.array(t0, dtype=float)
    valid  = ~np.isnan(t0_arr[source]) & ~np.isnan(t0_arr[target])
    source, target = source[valid], target[valid]
    dt = t0_arr[source] - t0_arr[target]
    keep = dt >= 0
    source, target, dt = source[keep], target[keep], dt[keep]
    if len(source) == 0:
        return pd.DataFrame(columns=["paper_id", "SB_coef", "awakening_time", "t0"])

    nc = int(np.nanmax(t0_arr) + 1)
    paper2dt = sparse.csr_matrix(
        (np.ones(len(target)), (target, dt + 1)), shape=(nr, nc + 1)
    )
    results = []
    for i in range(paper2dt.shape[0]):
        dts = paper2dt.indices[paper2dt.indptr[i]:paper2dt.indptr[i + 1]] - 1
        dct = paper2dt.data[paper2dt.indptr[i]:paper2dt.indptr[i + 1]]
        if len(dts) == 0:
            continue
        coef, awake = _sb_for_paper(dts, dct)
        results.append({"SB_coef": coef, "awakening_time": awake,
                        "paper_id": i, "t0": t0_arr[i]})
    return pd.DataFrame(results)


# ── Neo4j ──────────────────────────────────────────────────────────────────────

def _neo4j_driver():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    from neo4j import GraphDatabase
    uri      = os.environ["NEO4J_URI"]
    user     = os.environ.get("NEO4J_USER", "neo4j")
    password = os.environ["NEO4J_PASSWORD"]
    database = os.environ.get("NEO4J_DATABASE", "neo4j")
    return GraphDatabase.driver(uri, auth=(user, password)), database


# ── Load network ───────────────────────────────────────────────────────────────

def load_network(network_dir: Path) -> tuple[list[dict], list[dict]]:
    path = network_dir / "_chase_network.json"
    if not path.exists():
        sys.exit(f"[error] Not found: {path}")
    data = json.loads(path.read_text())
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    print(f"  Loaded {len(nodes)} nodes, {len(edges)} edges")
    return nodes, edges


# ── Build graph + sparse matrix ────────────────────────────────────────────────

def build_graph(nodes: list[dict], edges: list[dict]):
    """Returns (G, node_info, node_list, net_sparse, t0_array).

    node_list:   ordered list of node keys (index → key)
    net_sparse:  scipy CSR matrix (n × n), values = citation_level weights
    t0_array:    publication years per node (NaN if unknown)
    """
    node_info: dict[str, dict] = {}
    for n in nodes:
        key = n.get("doi") or n.get("title", "").strip()
        if not key:
            continue
        node_info[key] = {
            "doi":       n.get("doi"),
            "title":     n.get("title", ""),
            "year":      n.get("year"),
            "in_corpus": bool(n.get("in_corpus")),
        }

    # Consistent node ordering for the sparse matrix
    node_list   = list(node_info.keys())
    node_to_idx = {k: i for i, k in enumerate(node_list)}
    n_nodes     = len(node_list)

    # Build networkx graph and sparse matrix simultaneously
    G = nx.DiGraph()
    G.add_nodes_from(node_list)
    rows, cols, data = [], [], []

    for e in edges:
        src   = e.get("source", "").strip()
        tgt   = e.get("target", "").strip()
        level = int(e.get("citation_level", 1))
        if not src or not tgt or src not in node_to_idx or tgt not in node_to_idx:
            continue
        if G.has_edge(src, tgt):
            if G[src][tgt]["weight"] < level:
                G[src][tgt]["weight"] = level
                i, j = node_to_idx[src], node_to_idx[tgt]
                # update sparse matrix entry (handled via max at build time below)
        else:
            G.add_edge(src, tgt, weight=float(level), citation_level=level,
                       citation_context=e.get("citation_context", ""))
            rows.append(node_to_idx[src])
            cols.append(node_to_idx[tgt])
            data.append(float(level))

    net_sparse = sparse.csr_matrix((data, (rows, cols)), shape=(n_nodes, n_nodes))

    # t0 array: publication year per node (NaN if missing)
    t0 = np.array([
        float(node_info[k]["year"]) if node_info[k]["year"] else np.nan
        for k in node_list
    ])

    print(f"  Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    print(f"  Sparse matrix: {net_sparse.shape}, {net_sparse.nnz} non-zeros")
    return G, node_info, node_list, net_sparse, t0


# ── η: Weighted PageRank ───────────────────────────────────────────────────────

def compute_eta(G: nx.DiGraph, node_info: dict) -> dict[str, float]:
    """Weighted PageRank → η, normalised to [0, 1].

    Proxy for CCM's intrinsic fitness η_j. Full NCE requires c_j(t_i) —
    citation count of paper j at exact publication time of paper i — which
    requires per-citation timestamps we don't have (only publication years).
    """
    pr     = nx.pagerank(G, alpha=0.85, weight="weight", max_iter=300, tol=1e-7)
    max_pr = max(pr.values()) if pr else 1.0
    return {k: round(v / max_pr, 6) for k, v in pr.items()}


# ── u_j: fastRP embeddings ─────────────────────────────────────────────────────

def compute_embeddings(
    net_sparse, node_list: list[str], dim: int, window_size: int
) -> dict[str, np.ndarray]:
    """fastRP embeddings (K=dim) from Kojaku et al.'s own implementation.

    Uses the L-weighted directed adjacency matrix. edge_direction=True gives
    separate out-embedding (based on what a paper cites) and in-embedding
    (based on who cites a paper). We use the out-embedding as u_j since it
    captures what intellectual territory a paper draws from — matching CCM's
    citation-space positioning concept.
    """
    print(f"  Running fastRP (dim={dim}, window_size={window_size})...")
    emb_out, emb_in = fastRP(net_sparse, dim=dim, window_size=window_size,
                              edge_direction=True, seed=42)
    # Normalise rows to unit vectors (CCM embeds on hypersphere)
    def _normalise(X):
        norms = np.linalg.norm(X, axis=1, keepdims=True)
        return X / np.maximum(norms, 1e-8)

    emb_out = _normalise(emb_out)
    return {node_list[i]: emb_out[i] for i in range(len(node_list))}


# ── cluster_id: K-means on u_j ────────────────────────────────────────────────

def compute_clusters(embeddings: dict[str, np.ndarray], n_clusters: int) -> dict[str, int]:
    """K-means on u_j embeddings → cluster_id. Identical to CCM's post-hoc step."""
    keys = list(embeddings.keys())
    X    = np.stack([embeddings[k] for k in keys])
    km   = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labs = km.fit_predict(X)
    print(f"  K-means: {n_clusters} clusters over {len(keys)} nodes")
    return {keys[i]: int(labs[i]) for i in range(len(keys))}


# ── Sleeping beauties via SB coefficient ──────────────────────────────────────

def compute_sleeping_beauties(
    net_sparse, node_list: list[str], node_info: dict, t0: np.ndarray,
    sb_threshold: float = 1.0,
) -> tuple[set[str], pd.DataFrame]:
    """Sleeping beauty coefficient (Ke et al. 2015) via Kojaku et al.'s formula.

    Papers with SB_coef >= sb_threshold are flagged as sleeping beauties.
    For a 2023-2026 corpus the citation lag is short, so we also report the
    raw SB_coef so the threshold can be tuned post-hoc.

    Returns: (set of sleeping beauty keys, full SB DataFrame)
    """
    print(f"  Computing SB coefficients (threshold={sb_threshold})...")
    sb_df = calc_SB_coefficient(net_sparse, t0)
    if sb_df.empty:
        return set(), sb_df

    sb_above = sb_df[sb_df["SB_coef"] >= sb_threshold]
    sb_keys  = {node_list[int(i)] for i in sb_above["paper_id"]
                if int(i) < len(node_list)}
    # Only flag corpus papers as sleeping beauties
    sb_keys  = {k for k in sb_keys if node_info.get(k, {}).get("in_corpus")}
    print(f"  SB_coef ≥ {sb_threshold}: {len(sb_keys)} corpus papers flagged")
    return sb_keys, sb_df


# ── field_momentum ─────────────────────────────────────────────────────────────

def compute_field_momentum(
    G: nx.DiGraph, node_info: dict, node_cluster: dict
) -> dict[int, float]:
    """Per-cluster: fraction of in-edges from 2024+ source papers."""
    recent = defaultdict(int)
    total  = defaultdict(int)
    for src, tgt in G.edges():
        cid = node_cluster.get(tgt)
        if cid is None:
            continue
        total[cid] += 1
        src_year = node_info.get(src, {}).get("year")
        if src_year and src_year >= 2024:
            recent[cid] += 1
    all_cids = set(node_cluster.values())
    return {cid: round(recent[cid] / total[cid], 4) if total[cid] > 0 else 0.0
            for cid in all_cids}


# ── Print summary ──────────────────────────────────────────────────────────────

def print_summary(G, node_info, eta, node_cluster, field_momentum, sleeping_beauties, sb_df):
    corpus = [k for k, info in node_info.items() if info["in_corpus"]]

    print(f"\n{'='*68}")
    print(f"Community Citation Model — {date.today()}")
    print(f"{'='*68}")
    print(f"  Corpus papers scored:    {len(corpus)}")
    print(f"  Clusters (k-means):      {len(set(node_cluster.values()))}")
    print(f"  Sleeping beauties (SB):  {len(sleeping_beauties)}")

    top = sorted(corpus, key=lambda k: eta.get(k, 0), reverse=True)[:15]
    print(f"\nTop 15 corpus papers by η (fitness):")
    for k in top:
        info  = node_info[k]
        cid   = node_cluster.get(k, -1)
        fm    = field_momentum.get(cid, 0)
        sb    = "★" if k in sleeping_beauties else " "
        title = (info.get("title") or k)[:55]
        print(f"  {sb} η={eta.get(k,0):.4f}  C{cid:2d}  fm={fm:.2f}  {title}")

    cluster_corpus = defaultdict(int)
    for k in corpus:
        cluster_corpus[node_cluster.get(k, -1)] += 1

    print(f"\nCluster overview (≥3 corpus papers):")
    for cid, cnt in sorted(cluster_corpus.items(), key=lambda x: -x[1]):
        if cnt < 3:
            continue
        fm = field_momentum.get(cid, 0)
        print(f"  C{cid:2d}  corpus={cnt:3d}  field_momentum={fm:.3f}")

    if not sb_df.empty:
        print(f"\nTop sleeping beauties by SB coefficient:")
        top_sb = sb_df.nlargest(8, "SB_coef")
        for _, row in top_sb.iterrows():
            idx = int(row["paper_id"])
            # find key from node_list position — printed separately in caller
            print(f"  SB_coef={row['SB_coef']:.2f}  awake_at+{int(row['awakening_time'])}yr"
                  f"  node_idx={idx}")


# ── Neo4j write ────────────────────────────────────────────────────────────────

def write_to_neo4j(node_info, eta, node_cluster, field_momentum,
                   sleeping_beauties, sb_df, node_list, driver, database):
    corpus = [(k, info) for k, info in node_info.items() if info["in_corpus"]]
    print(f"\nWriting CCM scores to Neo4j ({len(corpus)} corpus Paper nodes)...")

    # Build SB_coef lookup: node_key → SB_coef
    sb_coef_lookup = {}
    if not sb_df.empty:
        for _, row in sb_df.iterrows():
            idx = int(row["paper_id"])
            if idx < len(node_list):
                sb_coef_lookup[node_list[idx]] = float(row["SB_coef"])

    written = skipped = 0
    with driver.session(database=database) as session:
        for k, info in corpus:
            doi   = info.get("doi")
            title = info.get("title", "")
            cid   = node_cluster.get(k, -1)
            params = {
                "eta":               eta.get(k, 0.0),
                "cluster_id":        cid,
                "field_momentum":    field_momentum.get(cid, 0.0),
                "is_sleeping_beauty": k in sleeping_beauties,
                "sb_coef":           sb_coef_lookup.get(k, 0.0),
                "ccm_run_date":      str(date.today()),
            }
            cypher = """
                SET p.eta = $eta,
                    p.cluster_id = $cluster_id,
                    p.field_momentum = $field_momentum,
                    p.is_sleeping_beauty = $is_sleeping_beauty,
                    p.sb_coef = $sb_coef,
                    p.ccm_run_date = $ccm_run_date
                RETURN count(p) AS n
            """
            if doi:
                result = session.run(f"MATCH (p:Paper {{doi: $doi}}) {cypher}",
                                     {"doi": doi, **params})
            else:
                result = session.run(f"MATCH (p:Paper {{title: $title}}) {cypher}",
                                     {"title": title, **params})

            if result.single()["n"] > 0:
                written += 1
            else:
                skipped += 1

    print(f"  Written: {written}  |  Not matched in Neo4j: {skipped}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main(network_dir: Path, dry_run: bool, n_clusters: int,
         embedding_dim: int, window_size: int, sb_threshold: float) -> None:
    print(f"\nCommunity Citation Model Trainer")
    print(f"Run date:    {date.today()}")
    print(f"Network dir: {network_dir}")
    print(f"Config: K={embedding_dim}, k={n_clusters} clusters, "
          f"fastRP window={window_size}, SB threshold={sb_threshold}\n")

    # 1. Load
    nodes, edges = load_network(network_dir)

    # 2. Build graph + sparse matrix
    G, node_info, node_list, net_sparse, t0 = build_graph(nodes, edges)
    corpus_count = sum(1 for info in node_info.values() if info["in_corpus"])
    print(f"  Corpus nodes (in_corpus=True): {corpus_count}")

    # 3. η — Weighted PageRank
    print("\n[1/5] Computing η (weighted PageRank)...")
    eta = compute_eta(G, node_info)
    corpus_eta = [eta[k] for k, info in node_info.items() if info["in_corpus"]]
    print(f"  η range (corpus): {min(corpus_eta):.6f} – {max(corpus_eta):.6f}")
    print(f"  η mean  (corpus): {sum(corpus_eta)/len(corpus_eta):.6f}")

    # 4. u_j — fastRP embeddings (Kojaku et al.)
    print(f"\n[2/5] Computing fastRP embeddings (K={embedding_dim})...")
    embeddings = compute_embeddings(net_sparse, node_list, embedding_dim, window_size)

    # 5. cluster_id — K-means on u_j
    print(f"\n[3/5] Clustering embeddings (k={n_clusters})...")
    node_cluster = compute_clusters(embeddings, n_clusters)

    # 6. Sleeping beauties — Ke et al. SB coefficient (Kojaku et al. port)
    print(f"\n[4/5] Computing sleeping beauty coefficients...")
    sleeping_beauties, sb_df = compute_sleeping_beauties(
        net_sparse, node_list, node_info, t0, sb_threshold
    )

    # 7. field_momentum per cluster
    print(f"\n[5/5] Computing field_momentum per cluster...")
    field_momentum = compute_field_momentum(G, node_info, node_cluster)
    active = sum(1 for v in field_momentum.values() if v > 0)
    print(f"  Clusters with 2024+ in-edges: {active}/{len(field_momentum)}")

    # 8. Summary
    print_summary(G, node_info, eta, node_cluster, field_momentum, sleeping_beauties, sb_df)

    # 9. Save scores JSON (always — useful for A8 + debugging)
    sb_coef_lookup = {}
    if not sb_df.empty:
        for _, row in sb_df.iterrows():
            idx = int(row["paper_id"])
            if idx < len(node_list):
                sb_coef_lookup[node_list[idx]] = float(row["SB_coef"])

    corpus_scores = []
    for k, info in node_info.items():
        if not info["in_corpus"]:
            continue
        cid = node_cluster.get(k, -1)
        corpus_scores.append({
            "key":                k,
            "doi":                info.get("doi"),
            "title":              info.get("title", ""),
            "year":               info.get("year"),
            "eta":                eta.get(k, 0.0),
            "cluster_id":         cid,
            "field_momentum":     field_momentum.get(cid, 0.0),
            "is_sleeping_beauty": k in sleeping_beauties,
            "sb_coef":            sb_coef_lookup.get(k, 0.0),
            "in_degree":          G.in_degree(k),
            "out_degree":         G.out_degree(k),
        })
    corpus_scores.sort(key=lambda x: -x["eta"])

    scores_path = network_dir / "_ccm_scores.json"
    scores_path.write_text(json.dumps(corpus_scores, indent=2))
    print(f"\nScores saved:     {scores_path}  ({len(corpus_scores)} corpus papers)")

    # Save embeddings for corpus papers (for A8 similarity search)
    emb_out = {k: embeddings[k].tolist() for k, info in node_info.items()
               if info["in_corpus"] and k in embeddings}
    emb_path = network_dir / "_ccm_embeddings.json"
    emb_path.write_text(json.dumps(emb_out))
    print(f"Embeddings saved: {emb_path}  ({len(emb_out)} corpus papers, K={embedding_dim})")

    # 10. Neo4j write
    if not dry_run:
        try:
            driver, database = _neo4j_driver()
        except KeyError as e:
            sys.exit(f"\n[error] Missing env var: {e}. Set NEO4J_URI and NEO4J_PASSWORD.")
        write_to_neo4j(node_info, eta, node_cluster, field_momentum,
                       sleeping_beauties, sb_df, node_list, driver, database)
        driver.close()
    else:
        print("\n[dry-run] Skipping Neo4j writes.")

    print("\nDone.")


if __name__ == "__main__":
    default_dir = Path(__file__).parent / "ingested_papers" / "merged"
    parser = argparse.ArgumentParser(description="Community Citation Model trainer")
    parser.add_argument("--network-dir",   type=Path,  default=default_dir)
    parser.add_argument("--dry-run",       action="store_true",
                        help="Compute scores, skip Neo4j writes")
    parser.add_argument("--n-clusters",    type=int,   default=15,
                        help="K-means clusters (default: 15)")
    parser.add_argument("--embedding-dim", type=int,   default=128,
                        help="fastRP embedding dim K (default: 128)")
    parser.add_argument("--window-size",   type=int,   default=5,
                        help="fastRP propagation window (default: 5)")
    parser.add_argument("--sb-threshold",  type=float, default=1.0,
                        help="Min SB coefficient to flag as sleeping beauty (default: 1.0)")
    args = parser.parse_args()
    main(args.network_dir, args.dry_run,
         args.n_clusters, args.embedding_dim, args.window_size, args.sb_threshold)
