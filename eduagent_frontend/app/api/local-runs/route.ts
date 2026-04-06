import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

const BACKEND_ROOT = path.join(
  process.env.HOME || "",
  "Documents/A-Moosa-Dev/AI-EDU-Dev/eduagent/eduagent_backend/deep-research-output"
);

// Scan both frontend runs (deep-research-output/) and CLI runs (deep-research-output/final-test/)
const OUTPUT_DIRS = [
  BACKEND_ROOT,
  path.join(BACKEND_ROOT, "final-test"),
];

function parseTimestamp(slug: string, snapshotTimestamp?: string): number {
  // Try snapshot timestamp first (from output_saver.py: "YYYYMMDD_HHMMSS")
  const tsStr = snapshotTimestamp ?? slug;
  const match = tsStr.match(/(\d{8})_(\d{6})/);
  if (match) {
    const [, date, time] = match;
    const iso = `${date.slice(0, 4)}-${date.slice(4, 6)}-${date.slice(6, 8)}T${time.slice(0, 2)}:${time.slice(2, 4)}:${time.slice(4, 6)}`;
    return new Date(iso).getTime();
  }
  return Date.now();
}

function extractQuery(reportText: string): string {
  const match = reportText.match(/\*\*Query:\*\*\s*(.+)/);
  return match ? match[1].trim() : "Unknown query";
}

function stripReportHeader(reportText: string): string {
  // Remove the first 6 lines (# Run, blank, **Query:**, blank, **Date:**, blank, ---)
  const lines = reportText.split("\n");
  const hrIdx = lines.findIndex((l) => l.startsWith("---"));
  return hrIdx >= 0 ? lines.slice(hrIdx + 1).join("\n").trimStart() : reportText;
}

export async function GET() {
  const runs = [];
  const seenIds = new Set<string>();

  for (const OUTPUT_DIR of OUTPUT_DIRS) {
    if (!fs.existsSync(OUTPUT_DIR)) continue;

    const folders = fs
      .readdirSync(OUTPUT_DIR, { withFileTypes: true })
      .filter((d) => d.isDirectory())
      .map((d) => d.name);

  for (const folder of folders) {
    if (seenIds.has(folder)) continue;
    const folderPath = path.join(OUTPUT_DIR, folder);
    const files = fs.readdirSync(folderPath);

    const reportFile = files.find((f) => f.startsWith("final_report_") && f.endsWith(".md"));
    const qaFile = files.find((f) => f.startsWith("qa_report_") && f.endsWith(".md"));
    const snapshotFile = files.find((f) => f.startsWith("state_snapshot_") && f.endsWith(".json"));
    const logFile = files.find((f) => f === "run.log");

    if (!reportFile) continue;

    const reportRaw = fs.readFileSync(path.join(folderPath, reportFile), "utf-8");
    const query = extractQuery(reportRaw);
    const report = stripReportHeader(reportRaw);

    const qaReport = qaFile
      ? fs.readFileSync(path.join(folderPath, qaFile), "utf-8")
      : undefined;

    const runLog = logFile
      ? fs.readFileSync(path.join(folderPath, logFile), "utf-8")
      : undefined;

    let paperCount: number | undefined;
    let qaScore: number | undefined;
    let snapshotTimestamp: string | undefined;
    let snapshotModel: string = "gpt-5.4";
    let snapshotMaxSources: number = 30;
    let elapsed: string | undefined;

    if (runLog) {
      // Frontend runs: "Run complete — total time: 32m52s"
      const m1 = runLog.match(/Run complete[^:]*total time: (\S+)/);
      if (m1 && m1[1] !== "unknown") {
        elapsed = m1[1];
      }
      // CLI runs: "Total time           : 2847.1s"
      if (!elapsed) {
        const m2 = runLog.match(/Total time\s*:\s*([\d.]+)s/);
        if (m2) {
          const secs = Math.round(parseFloat(m2[1]));
          const m = Math.floor(secs / 60);
          const s = secs % 60;
          elapsed = `${m}m${String(s).padStart(2, "0")}s`;
        }
      }
      // Fallback: parse elapsed from last log line prefix "[+32m12s] ..."
      if (!elapsed) {
        const lastPrefix = [...runLog.matchAll(/\[\+(\d+)m(\d+)s\]/g)].pop();
        if (lastPrefix) {
          elapsed = `${lastPrefix[1]}m${lastPrefix[2]}s`;
        }
      }
    }
    if (snapshotFile) {
      try {
        const snap = JSON.parse(fs.readFileSync(path.join(folderPath, snapshotFile), "utf-8"));
        paperCount = snap.paper_profiles?.length ?? undefined;
        qaScore = snap.qa_score ?? undefined;
        snapshotTimestamp = snap.timestamp ?? undefined;
        // Read model from run_config saved by output_saver
        const rc = snap.run_config ?? {};
        if (rc.model) {
          // Strip provider prefix: "openai:gpt-5.4-mini-2026-03-17" → "gpt-5.4-mini-2026-03-17"
          const raw: string = rc.model;
          snapshotModel = raw.includes(":") ? raw.split(":")[1] : raw;
        }
        if (rc.max_sources) snapshotMaxSources = rc.max_sources;
      } catch {}
    }

    seenIds.add(folder);
    runs.push({
      id: folder,
      query,
      report,
      qaReport,
      runLog,
      paperCount,
      qaScore,
      createdAt: parseTimestamp(folder, snapshotTimestamp),
      status: "complete",
      elapsed,
      config: {
        taskType: "research-basic",
        model: snapshotModel,
        depth: "standard",
        maxSources: snapshotMaxSources,
      },
    });
  }
  } // end OUTPUT_DIRS loop

  // Most recent first
  runs.sort((a, b) => b.createdAt - a.createdAt);

  return NextResponse.json({ runs });
}
