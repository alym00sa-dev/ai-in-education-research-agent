import { NextRequest } from "next/server";

export const maxDuration = 300; // 5 minutes — pipeline can take 5-8 min

const RENDER_URL = process.env.RENDER_API_URL || "http://127.0.0.1:2024";

const MODEL_MAP: Record<string, string> = {
  // OpenAI
  "gpt-5.2":       "openai:gpt-5.2-2025-12-11",
  "gpt-5.4":       "openai:gpt-5.4-2026-03-05",
  "gpt-5-mini":    "openai:gpt-5-mini-2025-08-07",
  "gpt-4.1":       "openai:gpt-4.1",
  "gpt-4o":        "openai:gpt-4o",
  // Anthropic
  "claude-sonnet-4-6": "anthropic:claude-sonnet-4-6",
  "claude-opus-4-6":   "anthropic:claude-opus-4-6",
  "claude-sonnet-4-5": "anthropic:claude-sonnet-4-5",
  "claude-opus-4-5":   "anthropic:claude-opus-4-5",
  "claude-haiku-4-5":  "anthropic:claude-haiku-4-5-20251001",
};

const DEPTH_ITERATIONS: Record<string, number> = {
  standard: 5,
  deep: 9,
  comprehensive: 14,
};

export async function POST(req: NextRequest) {
  const { query, config } = await req.json();

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

  const mappedModel = MODEL_MAP[config.model] ?? "openai:gpt-5.2-2025-12-11";
  const searchApi = mappedModel.startsWith("anthropic:") ? "anthropic" : "openai";

  const payload = {
    input: { messages: [{ role: "user", content: messageContent }] },
    config: {
      configurable: {
        research_model: mappedModel,
        search_api: searchApi,
        max_researcher_iterations: DEPTH_ITERATIONS[config.depth] ?? 5,
        max_sources: config.maxSources ?? 30,
        allow_clarification: false,
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
