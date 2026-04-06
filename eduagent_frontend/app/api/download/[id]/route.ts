import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

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

  const folderPath = findFolder(id);
  if (!folderPath) {
    return NextResponse.json({ error: "Session not found" }, { status: 404 });
  }

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
    default:
      return NextResponse.json({ error: "Unknown file type" }, { status: 400 });
  }

  if (!filePath || !fs.existsSync(filePath)) {
    return NextResponse.json({ error: "File not found" }, { status: 404 });
  }

  const content = fs.readFileSync(filePath);
  return new NextResponse(content, {
    headers: {
      "Content-Type": contentType,
      "Content-Disposition": `attachment; filename="${downloadName}"`,
    },
  });
}
