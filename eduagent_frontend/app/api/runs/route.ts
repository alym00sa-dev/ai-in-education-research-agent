import { NextRequest, NextResponse } from "next/server";
import getRedis from "@/lib/redis";
import fs from "fs";
import path from "path";

// ── Disk fallback (local dev only) ────────────────────────────────────────────

const DISK_ROOT = path.join(
  process.env.HOME || "",
  "Documents/A-Moosa-Dev/AI-EDU-Dev/eduagent/eduagent_backend/deep-research-output"
);

function extractQuery(reportText: string): string {
  const match = reportText.match(/\*\*Query:\*\*\s*(.+)/);
  return match ? match[1].trim() : "Unknown query";
}

function stripHeader(reportText: string): string {
  const lines = reportText.split("\n");
  const hrIdx = lines.findIndex((l) => l.startsWith("---"));
  return hrIdx >= 0 ? lines.slice(hrIdx + 1).join("\n").trimStart() : reportText;
}

function loadDiskRuns() {
  const dirs = [DISK_ROOT, path.join(DISK_ROOT, "final-test")];
  const runs = [];
  const seen = new Set<string>();

  for (const dir of dirs) {
    if (!fs.existsSync(dir)) continue;
    for (const folder of fs.readdirSync(dir, { withFileTypes: true }).filter((d) => d.isDirectory()).map((d) => d.name)) {
      if (seen.has(folder)) continue;
      const folderPath = path.join(dir, folder);
      const files = fs.readdirSync(folderPath);
      const reportFile = files.find((f) => f.startsWith("final_report_") && f.endsWith(".md"));
      if (!reportFile) continue;
      const reportRaw = fs.readFileSync(path.join(folderPath, reportFile), "utf-8");
      const qaFile = files.find((f) => f.startsWith("qa_report_") && f.endsWith(".md"));
      const snapFile = files.find((f) => f.startsWith("state_snapshot_") && f.endsWith(".json"));
      let paperCount, qaScore, model = "gpt-4.1", maxSources = 30, elapsed;
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
      seen.add(folder);
      runs.push({
        id: folder,
        query: extractQuery(reportRaw),
        report: stripHeader(reportRaw),
        qaReport: qaFile ? fs.readFileSync(path.join(folderPath, qaFile), "utf-8") : undefined,
        paperCount,
        qaScore,
        createdAt: Date.now(),
        status: "complete",
        elapsed,
        config: { taskType: "research-basic", model, depth: "standard", maxSources },
      });
    }
  }
  return runs;
}

// ── Redis helpers ─────────────────────────────────────────────────────────────

async function getRunIndex(redis: NonNullable<ReturnType<typeof getRedis>>): Promise<string[]> {
  const raw = await redis.get("runs_index");
  return raw ? JSON.parse(raw) : [];
}

async function setRunIndex(redis: NonNullable<ReturnType<typeof getRedis>>, ids: string[]) {
  await redis.set("runs_index", JSON.stringify(ids));
}

// ── Routes ────────────────────────────────────────────────────────────────────

export async function GET() {
  const redis = getRedis();

  if (!redis) {
    // Local dev fallback: read from disk
    const runs = loadDiskRuns().sort((a, b) => b.createdAt - a.createdAt);
    return NextResponse.json({ runs });
  }

  try {
    const ids = await getRunIndex(redis);
    if (ids.length === 0) return NextResponse.json({ runs: [] });

    const pipeline = redis.pipeline();
    for (const id of ids) pipeline.get(`run:${id}`);
    const results = await pipeline.exec();

    const runs = (results ?? [])
      .map((r) => (r[1] ? JSON.parse(r[1] as string) : null))
      .filter(Boolean);

    return NextResponse.json({ runs });
  } catch (e) {
    console.error("[runs] GET error", e);
    return NextResponse.json({ runs: [] });
  }
}

export async function POST(req: NextRequest) {
  const redis = getRedis();
  if (!redis) return NextResponse.json({ ok: false, error: "No Redis" }, { status: 503 });

  try {
    const run = await req.json();
    if (!run?.id) return new Response("Missing id", { status: 400 });

    await redis.set(`run:${run.id}`, JSON.stringify(run));

    const ids = await getRunIndex(redis);
    if (!ids.includes(run.id)) {
      await setRunIndex(redis, [run.id, ...ids]);
    }

    return NextResponse.json({ ok: true });
  } catch (e) {
    console.error("[runs] POST error", e);
    return NextResponse.json({ ok: false }, { status: 500 });
  }
}
