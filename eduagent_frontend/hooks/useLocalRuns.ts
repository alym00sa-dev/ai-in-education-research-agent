"use client";
import { useState, useEffect, useRef } from "react";
import { Job } from "@/lib/types";

const POLL_INTERVAL_MS = 30_000; // refresh every 30s to pick up background-completed runs

function parseRuns(data: { runs?: unknown[] }): Job[] {
  return (data.runs ?? []).map((r) => {
    const run = r as {
      id: string;
      query: string;
      report?: string;
      qaReport?: string;
      runLog?: string;
      paperCount?: number;
      elapsed?: string;
      createdAt: number;
      status: string;
      config: Job["config"];
    };
    return {
      id: run.id,
      query: run.query,
      report: run.report,
      qaReport: run.qaReport,
      statusLog: run.runLog
        ? run.runLog.split("\n").filter(Boolean).map((line: string, i: number) => ({
            timestamp: i * 1000,
            text: line.replace(/^\[.*?\]\s*/, ""),
            level: "node" as const,
          }))
        : [],
      paperCount: run.paperCount,
      elapsed: run.elapsed,
      status: "complete" as const,
      createdAt: run.createdAt,
      config: run.config,
    };
  });
}

export function useLocalRuns() {
  const [localRuns, setLocalRuns] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const refresh = () =>
    fetch("/api/local-runs")
      .then((r) => r.json())
      .then((data) => setLocalRuns(parseRuns(data)))
      .catch(() => {})
      .finally(() => setLoading(false));

  useEffect(() => {
    refresh();
    timerRef.current = setInterval(refresh, POLL_INTERVAL_MS);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  return { localRuns, loading };
}
