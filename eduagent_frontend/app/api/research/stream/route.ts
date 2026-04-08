import { NextRequest } from "next/server";

export const runtime = "edge";
export const maxDuration = 300; // 5 minutes — Pro plan required for > 10s

const RENDER_URL = process.env.RENDER_API_URL || "http://127.0.0.1:2024";

// Fast mode: GPT 5.4 Mini for research nodes
// Slow mode: GPT 5.4 for research nodes
// Report always uses GPT 5.4 regardless of speed
const SPEED_MODEL_MAP: Record<string, string> = {
  "gpt-5.4-mini": "openai:gpt-5.4-mini-2026-03-17",
  "gpt-5.4":      "openai:gpt-5.4-2026-03-05",
};

const REPORT_MODEL = "openai:gpt-5.4-2026-03-05";

const RESEARCH_ITERATIONS = 3;

export async function POST(req: NextRequest) {
  const { query, config, jobId } = await req.json();

  // Append keywords to query content if provided
  const keywords = (config.keywords ?? "").trim();
  const messageContent = keywords
    ? `${query}\nKeywords: ${keywords}`
    : query;

  // Create thread
  const threadRes = await fetch(`${RENDER_URL}/threads`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
  if (!threadRes.ok) {
    return new Response("Failed to create thread", { status: 502 });
  }
  const { thread_id } = await threadRes.json();

  const mainModel = SPEED_MODEL_MAP[config.model] ?? SPEED_MODEL_MAP["gpt-5.4-mini"];

  const payload = {
    assistant_id: "agent",
    input: { messages: [{ role: "user", content: messageContent }] },
    stream_mode: ["values", "updates", "custom"],
    config: {
      // Must match run_pipeline.py CONFIG exactly
      recursion_limit: 200,
      configurable: {
        model: mainModel,
        report_model: REPORT_MODEL,
        research_iterations: RESEARCH_ITERATIONS,
        max_concurrent_researchers: 5,
        max_sweep_cycles: 2,
        tavily_budget: 8,
        serp_budget: 2,
        enable_pdf_extraction: true,
        max_sources: 30,
        allow_clarification: false,
        ...(jobId ? { session_id: jobId } : {}),
      },
    },
  };

  const upstream = await fetch(`${RENDER_URL}/threads/${thread_id}/runs/stream`, {
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
