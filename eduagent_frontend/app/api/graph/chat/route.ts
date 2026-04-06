import { NextRequest } from "next/server";

export const maxDuration = 60;

const RENDER_URL = process.env.RENDER_API_URL || "http://127.0.0.1:2024";

// Model name mapping — graph traversal uses the same model IDs as research
const MODEL_MAP: Record<string, string> = {
  "gpt-5.4-mini":       "openai:gpt-5.4-mini-2026-03-17",
  "gpt-5.4":            "openai:gpt-5.4-2026-03-05",
  "claude-sonnet-4-6":  "anthropic:claude-sonnet-4-6",
  "claude-opus-4-6":    "anthropic:claude-opus-4-6",
  "claude-haiku-4-5":   "anthropic:claude-haiku-4-5-20251001",
};

const DEFAULT_MODEL = "openai:gpt-5.4-mini-2026-03-17";

export async function POST(req: NextRequest) {
  const { sessionId, message, model } = await req.json();

  if (!sessionId || !message) {
    return new Response("Missing sessionId or message", { status: 400 });
  }

  const resolvedModel = MODEL_MAP[model] ?? DEFAULT_MODEL;

  // Create thread with our session ID (POST is idempotent if thread_id already exists — returns 409 which we ignore)
  const threadRes = await fetch(`${RENDER_URL}/threads`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ thread_id: sessionId }),
  });
  if (!threadRes.ok && threadRes.status !== 409) {
    return new Response("Failed to create thread", { status: 502 });
  }

  const payload = {
    assistant_id: "graph_traversal",
    input: { messages: [{ role: "user", content: message }] },
    stream_mode: ["messages"],
    config: {
      configurable: {
        model: resolvedModel,
        session_id: sessionId,
      },
    },
  };

  const upstream = await fetch(`${RENDER_URL}/threads/${sessionId}/runs/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!upstream.ok || !upstream.body) {
    return new Response("Upstream stream failed", { status: 502 });
  }

  return new Response(upstream.body, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      "X-Accel-Buffering": "no",
    },
  });
}
