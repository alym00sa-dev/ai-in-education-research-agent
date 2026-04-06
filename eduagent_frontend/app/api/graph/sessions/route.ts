import { NextRequest, NextResponse } from "next/server";
import getRedis from "@/lib/redis";
import fs from "fs";
import path from "path";

// ── Disk fallback (local dev only) ────────────────────────────────────────────

const DISK_DIR = path.join(
  process.env.HOME || "",
  "Documents/A-Moosa-Dev/AI-EDU-Dev/eduagent/eduagent_backend/graph-traversal-output"
);

function ensureDir() {
  if (!fs.existsSync(DISK_DIR)) fs.mkdirSync(DISK_DIR, { recursive: true });
}

// ── Redis helpers ─────────────────────────────────────────────────────────────

async function getIndex(redis: NonNullable<ReturnType<typeof getRedis>>): Promise<string[]> {
  const raw = await redis.get("graph_sessions_index");
  return raw ? JSON.parse(raw) : [];
}

async function setIndex(redis: NonNullable<ReturnType<typeof getRedis>>, ids: string[]) {
  await redis.set("graph_sessions_index", JSON.stringify(ids));
}

// ── Routes ────────────────────────────────────────────────────────────────────

export async function GET() {
  const redis = getRedis();

  if (!redis) {
    ensureDir();
    const sessions = fs.readdirSync(DISK_DIR)
      .filter((f) => f.endsWith(".json"))
      .map((f) => { try { return JSON.parse(fs.readFileSync(path.join(DISK_DIR, f), "utf-8")); } catch { return null; } })
      .filter(Boolean)
      .sort((a: { updatedAt: number }, b: { updatedAt: number }) => b.updatedAt - a.updatedAt);
    return NextResponse.json({ sessions });
  }

  try {
    const ids = await getIndex(redis);
    if (ids.length === 0) return NextResponse.json({ sessions: [] });
    const pipeline = redis.pipeline();
    for (const id of ids) pipeline.get(`graph:session:${id}`);
    const results = await pipeline.exec();
    const sessions = (results ?? [])
      .map((r) => (r[1] ? JSON.parse(r[1] as string) : null))
      .filter(Boolean)
      .sort((a: { updatedAt: number }, b: { updatedAt: number }) => b.updatedAt - a.updatedAt);
    return NextResponse.json({ sessions });
  } catch (e) {
    console.error("[graph/sessions] GET error", e);
    return NextResponse.json({ sessions: [] });
  }
}

export async function POST(req: NextRequest) {
  const session = await req.json();
  if (!session?.id) return new Response("Missing id", { status: 400 });

  const redis = getRedis();
  if (!redis) {
    ensureDir();
    fs.writeFileSync(path.join(DISK_DIR, `${session.id}.json`), JSON.stringify(session, null, 2), "utf-8");
    return NextResponse.json({ ok: true });
  }

  try {
    await redis.set(`graph:session:${session.id}`, JSON.stringify(session));
    const ids = await getIndex(redis);
    if (!ids.includes(session.id)) await setIndex(redis, [session.id, ...ids]);
    return NextResponse.json({ ok: true });
  } catch (e) {
    console.error("[graph/sessions] POST error", e);
    return NextResponse.json({ ok: false }, { status: 500 });
  }
}

export async function DELETE(req: NextRequest) {
  const { id } = await req.json();
  if (!id) return new Response("Missing id", { status: 400 });

  const redis = getRedis();
  if (!redis) {
    const filePath = path.join(DISK_DIR, `${id}.json`);
    if (fs.existsSync(filePath)) fs.unlinkSync(filePath);
    return NextResponse.json({ ok: true });
  }

  try {
    await redis.del(`graph:session:${id}`);
    const ids = await getIndex(redis);
    await setIndex(redis, ids.filter((i: string) => i !== id));
    return NextResponse.json({ ok: true });
  } catch (e) {
    console.error("[graph/sessions] DELETE error", e);
    return NextResponse.json({ ok: false }, { status: 500 });
  }
}
