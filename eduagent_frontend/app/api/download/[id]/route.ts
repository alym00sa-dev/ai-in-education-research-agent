import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";
import getRedis from "@/lib/redis";

const BACKEND_ROOT = path.join(
  process.env.HOME || "",
  "Documents/A-Moosa-Dev/AI-EDU-Dev/eduagent/eduagent_backend/deep-research-output"
);

const OUTPUT_DIRS = [
  BACKEND_ROOT,
  path.join(BACKEND_ROOT, "final-test"),
];

function findFolder(id: string): string | null {
  for (const dir of OUTPUT_DIRS) {
    const candidate = path.join(dir, id);
    if (fs.existsSync(candidate) && fs.statSync(candidate).isDirectory()) {
      return candidate;
    }
  }
  return null;
}

function findFile(folderPath: string, prefix: string, ext: string): string | null {
  const files = fs.readdirSync(folderPath);
  const match = files.find((f) => f.startsWith(prefix) && f.endsWith(ext));
  return match ? path.join(folderPath, match) : null;
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const file = request.nextUrl.searchParams.get("file");

  if (!id || !file) {
    return NextResponse.json({ error: "Missing id or file param" }, { status: 400 });
  }

  if (file !== "report" && file !== "qa" && file !== "log" && file !== "snapshot") {
    return NextResponse.json({ error: "Unknown file type" }, { status: 400 });
  }

  // ── Try disk first (local dev) ──────────────────────────────────────────────
  const folderPath = findFolder(id);
  if (folderPath) {
    let filePath: string | null = null;
    let contentType = "text/plain";
    let downloadName = file;

    switch (file) {
      case "report":
        filePath = findFile(folderPath, "final_report_", ".md");
        contentType = "text/markdown";
        downloadName = "final_report.md";
        break;
      case "qa":
        filePath = findFile(folderPath, "qa_report_", ".md");
        contentType = "text/markdown";
        downloadName = "qa_report.md";
        break;
      case "log":
        filePath = path.join(folderPath, "run.log");
        if (!fs.existsSync(filePath)) filePath = null;
        contentType = "text/plain";
        downloadName = "run.log";
        break;
      case "snapshot":
        filePath = findFile(folderPath, "state_snapshot_", ".json");
        contentType = "application/json";
        downloadName = "state_snapshot.json";
        break;
    }

    if (filePath && fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath);
      return new NextResponse(content, {
        headers: {
          "Content-Type": contentType,
          "Content-Disposition": `attachment; filename="${downloadName}"`,
        },
      });
    }
  }

  // ── Fall back to Redis (Vercel / production) ────────────────────────────────
  const redis = getRedis();
  if (!redis) {
    return NextResponse.json({ error: "Session not found" }, { status: 404 });
  }

  try {
    const raw = await redis.get(`run:${id}`);
    if (!raw) return NextResponse.json({ error: "Session not found" }, { status: 404 });

    const run = JSON.parse(raw) as { report?: string; qaReport?: string; query?: string };

    let content: string | null = null;
    let contentType = "text/plain";
    let downloadName = file;

    switch (file) {
      case "report":
        content = run.report ?? null;
        contentType = "text/markdown";
        downloadName = "final_report.md";
        break;
      case "qa":
        content = run.qaReport ?? null;
        contentType = "text/markdown";
        downloadName = "qa_report.md";
        break;
      default:
        // log and snapshot are only available from disk output
        return NextResponse.json({ error: "File not available for this session" }, { status: 404 });
    }

    if (!content) {
      return NextResponse.json({ error: "File not found" }, { status: 404 });
    }

    return new NextResponse(content, {
      headers: {
        "Content-Type": contentType,
        "Content-Disposition": `attachment; filename="${downloadName}"`,
      },
    });
  } catch (e) {
    console.error("[download] Redis error", e);
    return NextResponse.json({ error: "Internal error" }, { status: 500 });
  }
}
