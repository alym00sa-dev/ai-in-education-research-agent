# KG Ingest Queue — Postgres Migration Design

## Problem

The current queue mechanism is entirely file-based. After each Deep Research run, the `kg_write` node writes extracted paper profiles as JSON files to `KG-src/ingested_papers/queue/{session_id}/` on the local filesystem. The weekly batch script reads from that same directory.

This works locally but breaks in production for two reasons:

1. **Ephemeral disk** — Render (and most container platforms including Nomad) does not persist the local filesystem across container restarts or redeployments. Any papers queued between restarts are silently lost.
2. **Container isolation** — The LangGraph service and the weekly batch Cron Job run in separate containers. Even if the disk persisted, Container A's filesystem is invisible to Container B unless they share a mounted volume, which requires explicit infrastructure configuration.

Redis and Postgres (already provisioned by the LangGraph runtime) do not help with this — neither stores file-based paper data by default.

---

## Proposed Solution

Replace the file-based queue with a `kg_queue` table in the existing Postgres instance. Both the LangGraph service (`kg_write` node) and the weekly batch script connect to the same database, so the queue is durable, shared, and infrastructure-agnostic.

---

## Schema

```sql
CREATE TABLE kg_queue (
    id               SERIAL PRIMARY KEY,
    session_id       TEXT         NOT NULL,
    doi              TEXT,
    title            TEXT         NOT NULL,
    url              TEXT,
    extended_summary TEXT,
    profile          JSONB        NOT NULL,
    status           TEXT         NOT NULL DEFAULT 'queued',
    queued_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    processed_at     TIMESTAMPTZ,
    batch_date       TEXT,
    error            TEXT,

    UNIQUE (doi)
);

CREATE INDEX ON kg_queue (status);
CREATE INDEX ON kg_queue (queued_at);
```

### Column Notes

| Column | Purpose |
|---|---|
| `session_id` | Which research run produced this paper |
| `doi` | Primary deduplication key |
| `title` | Fallback slug and logging |
| `url` | Required for re-extraction in the weekly batch |
| `extended_summary` | Passed as `topic` to the LLM extractor |
| `profile` | Full `PaperProfileV2` as JSONB — preserved even if re-extraction fails |
| `status` | Lifecycle state: `queued → processing → done / failed` |
| `batch_date` | Which weekly run processed this entry (e.g. `"2026-04-14"`) |
| `error` | Populated on failure for debugging |

---

## Status Lifecycle

```
Research run ends
  kg_write node
    → INSERT INTO kg_queue ... ON CONFLICT (doi) DO NOTHING
      status = 'queued'

Weekly batch fires (Monday)
  run_weekly_batch.py
    → SELECT * FROM kg_queue WHERE status = 'queued'
    → UPDATE status = 'processing'
    → For each paper:
        re-extract (pdf_extractor_kg)
        citation chase (citation_chaser --incremental)
    → CCM retrain
    → Neo4j write (--skip-wipe)
    → UPDATE status = 'done', processed_at = NOW(), batch_date = today
    → On failure: UPDATE status = 'failed', error = '...'
```

The `ON CONFLICT (doi) DO NOTHING` on insert is the key deduplication mechanism — if the same paper appears in three separate research runs before Monday's batch fires, only the first entry is kept. Papers without a DOI fall back to title-based deduplication handled in application code.

The `status = 'done'` update replaces the current `shutil.move()` archive step entirely. History is preserved in the table rather than scattered across dated archive folders.

---

## What Changes in Code

### `deep-research-src/nodes/kg_write.py`
Instead of `session_dir.mkdir()` and `out_path.write_text(...)`, opens a Postgres connection and runs:
```sql
INSERT INTO kg_queue (session_id, doi, title, url, extended_summary, profile)
VALUES (%s, %s, %s, %s, %s, %s)
ON CONFLICT (doi) DO NOTHING
```

### `KG-src/run_weekly_batch.py`
Instead of iterating `QUEUE_DIR.iterdir()`, queries:
```sql
SELECT * FROM kg_queue WHERE status = 'queued' ORDER BY queued_at ASC
```
The `archive_queue()` function is replaced by:
```sql
UPDATE kg_queue
SET status = 'done', processed_at = NOW(), batch_date = %s
WHERE id = ANY(%s)
```

### Connection
Both scripts read `DATABASE_URL` from the environment — already set by Render for the LangGraph service. No new infrastructure required.

---

## What Does Not Change

- The weekly batch pipeline logic (extraction → citation chase → CCM → Neo4j write) is unchanged
- The `PaperProfileV2` data model is unchanged
- Neo4j is still written to only during the weekly batch, never during live research runs
- The existing Postgres instance (provisioned by LangGraph) is reused — no new database needed

---

## On Nomad

This approach is infrastructure-agnostic. On Nomad, both the LangGraph service job and the periodic batch job would receive `DATABASE_URL` via Vault, pointing at the same enterprise Postgres instance. No filesystem sharing, no persistent disk configuration required.

The weekly batch would be defined as a Nomad periodic job:

```hcl
periodic {
  cron             = "0 6 * * 1"   # Every Monday at 6am UTC
  prohibit_overlap = true
}
```

---

## Migration Steps (when ready to implement)

1. Run the `CREATE TABLE` DDL against the production Postgres instance
2. Update `kg_write.py` to write to `kg_queue` instead of disk
3. Update `run_weekly_batch.py` to read from `kg_queue` and update status on completion
4. Deploy updated backend — new research runs will queue to Postgres immediately
5. Manually process any existing `queue/` folder contents (one-time migration of backlog)
6. Set up Render Cron Job (or Nomad periodic job) to run `run_weekly_batch.py` on schedule
