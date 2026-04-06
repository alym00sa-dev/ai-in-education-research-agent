import { NextRequest, NextResponse } from "next/server";
import fs from "fs";
import path from "path";

const OUTPUT_DIR = path.join(
  process.env.HOME || "",
  "Documents/A-Moosa-Dev/AI-EDU-Dev/eduagent/eduagent_backend/graph-traversal-output"
);

function ensureDir() {
  if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// GET — list all sessions
export async function GET() {
  ensureDir();
  const files = fs.readdirSync(OUTPUT_DIR).filter(f => f.endsWith(".json"));
  const sessions = files
    .map(f => {
      try {
        return JSON.parse(fs.readFileSync(path.join(OUTPUT_DIR, f), "utf-8"));
      } catch {
        return null;
      }
    })
    .filter(Boolean)
    .sort((a, b) => b.updatedAt - a.updatedAt);

  return NextResponse.json({ sessions });
}

// POST — save/upsert a session
export async function POST(req: NextRequest) {
  ensureDir();
  const session = await req.json();
  if (!session?.id) return new Response("Missing id", { status: 400 });
  fs.writeFileSync(
    path.join(OUTPUT_DIR, `${session.id}.json`),
    JSON.stringify(session, null, 2),
    "utf-8"
  );
  return NextResponse.json({ ok: true });
}

// DELETE — remove a session
export async function DELETE(req: NextRequest) {
  const { id } = await req.json();
  if (!id) return new Response("Missing id", { status: 400 });
  const filePath = path.join(OUTPUT_DIR, `${id}.json`);
  if (fs.existsSync(filePath)) fs.unlinkSync(filePath);
  return NextResponse.json({ ok: true });
}
