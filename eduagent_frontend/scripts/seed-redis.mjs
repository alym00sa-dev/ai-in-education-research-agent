/**
 * One-time migration: seeds Redis with all local disk sessions.
 *
 * Usage:
 *   REDIS_URL="redis://..." node scripts/seed-redis.mjs
 *
 * Get REDIS_URL from Vercel dashboard → Storage → your KV store → .env.local tab.
 */

import { createRequire } from "module";
import fs from "fs";
import path from "path";
import os from "os";

const require = createRequire(import.meta.url);
const Redis = require("ioredis");

// ── Config ───────────────────────────────────────────────────────────────────

const DISK_ROOT = path.join(
  os.homedir(),
  "Documents/A-Moosa-Dev/AI-EDU-Dev/eduagent/eduagent_backend/deep-research-output"
);

const SCAN_DIRS = [DISK_ROOT, path.join(DISK_ROOT, "final-test")];

// ── Helpers (mirrors api/runs/route.ts) ──────────────────────────────────────

function extractQuery(reportText) {
  const match = reportText.match(/\*\*Query:\*\*\s*(.+)/);
  return match ? match[1].trim() : "Unknown query";
}

function stripHeader(reportText) {
  const lines = reportText.split("\n");
  const hrIdx = lines.findIndex((l) => l.startsWith("---"));
  return hrIdx >= 0 ? lines.slice(hrIdx + 1).join("\n").trimStart() : reportText;
}

function loadDiskRuns() {
  const runs = [];
  const seen = new Set();

  for (const dir of SCAN_DIRS) {
    if (!fs.existsSync(dir)) continue;

    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      const folder = entry.name;
      if (seen.has(folder)) continue;

      const folderPath = path.join(dir, folder);
      const files = fs.readdirSync(folderPath);

      const reportFile = files.find((f) => f.startsWith("final_report_") && f.endsWith(".md"));
      if (!reportFile) continue;

      const reportRaw = fs.readFileSync(path.join(folderPath, reportFile), "utf-8");
      const qaFile = files.find((f) => f.startsWith("qa_report_") && f.endsWith(".md"));
      const snapFile = files.find((f) => f.startsWith("state_snapshot_") && f.endsWith(".json"));

      let paperCount, qaScore, model = "gpt-4.1", maxSources = 30;
      if (snapFile) {
        try {
          const snap = JSON.parse(fs.readFileSync(path.join(folderPath, snapFile), "utf-8"));
          paperCount = snap.paper_profiles?.length;
          qaScore = snap.qa_score;
          const rc = snap.run_config ?? {};
          if (rc.model) model = rc.model.includes(":") ? rc.model.split(":")[1] : rc.model;
          if (rc.max_sources) maxSources = rc.max_sources;
        } catch {}
      }

      // Use folder mtime as createdAt
      const stat = fs.statSync(folderPath);
      const createdAt = stat.mtimeMs;

      seen.add(folder);
      runs.push({
        id: folder,
        query: extractQuery(reportRaw),
        report: stripHeader(reportRaw),
        qaReport: qaFile
          ? fs.readFileSync(path.join(folderPath, qaFile), "utf-8")
          : undefined,
        paperCount,
        qaScore,
        createdAt,
        status: "complete",
        config: { taskType: "research-basic", model, depth: "standard", maxSources },
      });
    }
  }

  return runs;
}

// ── Main ─────────────────────────────────────────────────────────────────────

const REDIS_URL = process.env.REDIS_URL;
if (!REDIS_URL) {
  console.error("Error: REDIS_URL environment variable is not set.");
  console.error('Usage: REDIS_URL="redis://..." node scripts/seed-redis.mjs');
  process.exit(1);
}

const redis = new Redis(REDIS_URL, { maxRetriesPerRequest: 3, connectTimeout: 10000 });

const runs = loadDiskRuns();
if (runs.length === 0) {
  console.log("No local disk sessions found — nothing to migrate.");
  await redis.quit();
  process.exit(0);
}

console.log(`Found ${runs.length} local session(s). Migrating to Redis...`);

// Read existing index so we don't clobber runs already in Redis
const existingRaw = await redis.get("runs_index");
const existingIds = new Set(existingRaw ? JSON.parse(existingRaw) : []);

let migrated = 0;
let skipped = 0;

for (const run of runs) {
  if (existingIds.has(run.id)) {
    console.log(`  skip  ${run.id} (already in Redis)`);
    skipped++;
    continue;
  }

  await redis.set(`run:${run.id}`, JSON.stringify(run));
  existingIds.add(run.id);
  console.log(`  wrote ${run.id} — "${run.query.slice(0, 60)}"`);
  migrated++;
}

// Write updated index (newest first)
const allIds = Array.from(existingIds);
await redis.set("runs_index", JSON.stringify(allIds));

console.log(`\nDone. Migrated: ${migrated}, Skipped: ${skipped}`);
await redis.quit();
