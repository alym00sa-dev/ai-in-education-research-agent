import { NextRequest, NextResponse } from "next/server";

const RENDER_URL = process.env.RENDER_API_URL || "http://127.0.0.1:2024";

export async function GET(req: NextRequest) {
  const limit = req.nextUrl.searchParams.get("limit") ?? "50";
  try {
    const res = await fetch(`${RENDER_URL}/sessions?limit=${limit}`, {
      next: { revalidate: 30 }, // cache 30s
    });
    if (!res.ok) return NextResponse.json({ sessions: [] }, { status: res.status });
    const data = await res.json();
    return NextResponse.json(data);
  } catch {
    return NextResponse.json({ sessions: [] }, { status: 500 });
  }
}
