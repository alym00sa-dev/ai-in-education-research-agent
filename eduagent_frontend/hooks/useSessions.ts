"use client";
import { useEffect, useState } from "react";
import { Job } from "@/lib/types";

interface RawSession {
  session_id: string;
  query: string;
  created_at: string;
  model_provider: string;
  search_depth: string;
  paper_count: number | null;
  status: string;
  research_report: string | null;
}

function toJob(s: RawSession): Job {
  // Parse ISO string or epoch from Neo4j
  const createdAt = isNaN(Number(s.created_at))
    ? new Date(s.created_at).getTime()
    : Number(s.created_at);

  return {
    id: s.session_id,
    query: s.query,
    config: {
      taskType: "research-basic",
      model: s.model_provider?.replace(/^(openai:|anthropic:)/, "") ?? "gpt-4.1",
      depth: (s.search_depth as "standard" | "deep" | "comprehensive") ?? "standard",
      maxSources: 30,
      agentVersion: "v1",
    },
    status: s.status === "active" ? "complete" : (s.status as Job["status"]) ?? "complete",
    createdAt: isNaN(createdAt) ? Date.now() : createdAt,
    report: s.research_report ?? undefined,
    paperCount: s.paper_count ?? undefined,
  };
}

export function useSessions() {
  const [sessions, setSessions] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/sessions")
      .then((r) => r.json())
      .then((data) => {
        const jobs = (data.sessions ?? []).map(toJob);
        setSessions(jobs);
      })
      .catch(() => setSessions([]))
      .finally(() => setLoading(false));
  }, []);

  return { sessions, loading };
}
