"use client";
import { useState, useEffect, useCallback } from "react";
import { Job } from "@/lib/types";

const STORAGE_KEY = "eduagent_jobs";

export function useJobs() {
  const [jobs, setJobs] = useState<Job[]>([]);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed: Job[] = JSON.parse(stored);
        const STALE_MS = 45 * 60 * 1000; // 45 minutes
        const now = Date.now();
        const cleaned = parsed.map((j) =>
          j.status === "running" && now - (j.createdAt ?? 0) > STALE_MS
            ? { ...j, status: "failed" as const, error: "Run timed out — the connection was lost." }
            : j
        );
        setJobs(cleaned);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(cleaned));
      }
    } catch {}
  }, []);

  const persist = useCallback((updated: Job[]) => {
    setJobs(updated);
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(updated)); } catch {}
  }, []);

  const addJob = useCallback((job: Job) => {
    setJobs(prev => {
      const updated = [job, ...prev];
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(updated)); } catch {}
      return updated;
    });
  }, []);

  const updateJob = useCallback((id: string, patch: Partial<Job>) => {
    setJobs(prev => {
      const updated = prev.map(j => j.id === id ? { ...j, ...patch } : j);
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(updated)); } catch {}
      return updated;
    });
  }, []);

  const removeJob = useCallback((id: string) => {
    setJobs(prev => {
      const updated = prev.filter(j => j.id !== id);
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(updated)); } catch {}
      return updated;
    });
  }, []);

  const clearJobs = useCallback(() => {
    persist([]);
  }, [persist]);

  return { jobs, addJob, updateJob, removeJob, clearJobs };
}
