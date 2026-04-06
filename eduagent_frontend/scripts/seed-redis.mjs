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

const GRAPH_DISK_DIR = path.join(
  os.homedir(),
  "Documents/A-Moosa-Dev/AI-EDU-Dev/eduagent/eduagent_backend/graph-traversal-output"
);

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

      // Use folder birthtime as createdAt (actual run start time)
      const folderStat = fs.statSync(folderPath);
      const createdAt = folderStat.birthtimeMs || folderStat.mtimeMs;

      // Estimate elapsed from folder birth → report file mtime
      let elapsed;
      try {
        const reportStat = fs.statSync(path.join(folderPath, reportFile));
        const ms = reportStat.mtimeMs - createdAt;
        if (ms > 0) {
          const totalSec = Math.round(ms / 1000);
          const m = Math.floor(totalSec / 60);
          const s = totalSec % 60;
          elapsed = m > 0 ? `${m}m ${s}s` : `${s}s`;
        }
      } catch {}

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
        elapsed,
        status: "complete",
        config: { taskType: "research-basic", model, depth: "standard", maxSources },
      });
    }
  }

  return runs;
}

function loadDiskGraphSessions() {
  if (!fs.existsSync(GRAPH_DISK_DIR)) return [];
  return fs.readdirSync(GRAPH_DISK_DIR)
    .filter(f => f.endsWith(".json"))
    .map(f => {
      try { return JSON.parse(fs.readFileSync(path.join(GRAPH_DISK_DIR, f), "utf-8")); }
      catch { return null; }
    })
    .filter(Boolean);
}

// ── Main ─────────────────────────────────────────────────────────────────────

const REDIS_URL = process.env.REDIS_URL;
if (!REDIS_URL) {
  console.error("Error: REDIS_URL environment variable is not set.");
  console.error('Usage: REDIS_URL="redis://..." node scripts/seed-redis.mjs');
  process.exit(1);
}

const redis = new Redis(REDIS_URL, { maxRetriesPerRequest: 3, connectTimeout: 10000 });

// ── Migrate deep research runs ────────────────────────────────────────────────

const runs = loadDiskRuns();
console.log(`\nDeep Research: found ${runs.length} local session(s).`);

const existingRunsRaw = await redis.get("runs_index");
const existingRunIds = new Set(existingRunsRaw ? JSON.parse(existingRunsRaw) : []);

let migrated = 0;
let skipped = 0;

for (const run of runs) {
  const alreadyExists = existingRunIds.has(run.id);
  await redis.set(`run:${run.id}`, JSON.stringify(run));
  existingRunIds.add(run.id);
  if (alreadyExists) {
    console.log(`  update ${run.id} — "${run.query.slice(0, 60)}"`);
  } else {
    console.log(`  wrote  ${run.id} — "${run.query.slice(0, 60)}"`);
  }
  migrated++;
}

await redis.set("runs_index", JSON.stringify(Array.from(existingRunIds)));
console.log(`Deep Research done. Migrated: ${migrated}, Skipped: ${skipped}`);

// ── Migrate graph traversal sessions ─────────────────────────────────────────

const graphSessions = loadDiskGraphSessions();
console.log(`\nGraph Traversal: found ${graphSessions.length} local session(s).`);

const existingGraphRaw = await redis.get("graph_sessions_index");
const existingGraphIds = new Set(existingGraphRaw ? JSON.parse(existingGraphRaw) : []);

let gMigrated = 0;
let gSkipped = 0;

for (const session of graphSessions) {
  if (!session.id) continue;
  if (existingGraphIds.has(session.id)) {
    console.log(`  skip  ${session.id} (already in Redis)`);
    gSkipped++;
    continue;
  }
  await redis.set(`graph:session:${session.id}`, JSON.stringify(session));
  existingGraphIds.add(session.id);
  console.log(`  wrote ${session.id} — "${String(session.firstQuery ?? "").slice(0, 60)}"`);
  gMigrated++;
}

await redis.set("graph_sessions_index", JSON.stringify(Array.from(existingGraphIds)));
console.log(`Graph Traversal done. Migrated: ${gMigrated}, Skipped: ${gSkipped}`);

await redis.quit();
