"use client";
import { useState, useCallback, useMemo, useEffect } from "react";
import { useRouter } from "next/navigation";
import { v4 as uuidv4 } from "uuid";
import { AppMode, Job, ResearchConfig } from "@/lib/types";
import { useJobs } from "@/hooks/useJobs";
import { useResearch } from "@/hooks/useResearch";
import { useSessions } from "@/hooks/useSessions";
import Navbar from "@/components/layout/Navbar";
import QueryBar from "@/components/agent/QueryBar";
import JobsFeed from "@/components/agent/JobsFeed";
import ReportDrawer from "@/components/agent/ReportDrawer";
import CanvasShell from "@/components/canvas/CanvasShell";

export default function AgentPage() {
  const router = useRouter();
  const [mode, setMode] = useState<AppMode>("research");
  // Drawer only used for the actively running job
  const [runningJob, setRunningJob] = useState<Job | null>(null);

  const { jobs: localJobs, addJob, updateJob } = useJobs();
  const { sessions, loading: sessionsLoading } = useSessions();

  const allJobs = useMemo(() => {
    const localIds = new Set(localJobs.map((j) => j.id));
    const historical = sessions.filter((s) => !localIds.has(s.id));
    return [...localJobs, ...historical];
  }, [localJobs, sessions]);

  const handleUpdate = useCallback((id: string, patch: Partial<Job>) => {
    updateJob(id, patch);
    setRunningJob((prev) => (prev?.id === id ? { ...prev, ...patch } : prev));
  }, [updateJob]);

  const { activeJobId, startResearch, cancel } = useResearch(handleUpdate);

  // Auto-navigate to full session page when job completes or fails
  useEffect(() => {
    if (!runningJob) return;
    if (runningJob.status === "complete" || runningJob.status === "failed") {
      const id = runningJob.id;
      setRunningJob(null);
      router.push(`/agent/${id}`);
    }
  }, [runningJob?.status]);

  const handleSubmit = useCallback((query: string, config: ResearchConfig) => {
    const job: Job = {
      id: uuidv4(),
      query,
      config,
      status: "running",
      createdAt: Date.now(),
    };
    addJob(job);
    setRunningJob(job);
    startResearch(job.id, query, config);
  }, [addJob, startResearch]);

  const handleSelect = useCallback((job: Job) => {
    if (job.status === "running") {
      // Keep drawer open for live streaming jobs
      setRunningJob(job);
    } else {
      router.push(`/agent/${job.id}`);
    }
  }, [router]);

  return (
    <div className="min-h-screen" style={{ background: "var(--bg)" }}>
      <Navbar mode={mode} onModeChange={setMode} />

      <main className="mx-auto max-w-3xl px-6 pt-10 pb-24">
        {mode === "research" ? (
          <>
            <QueryBar onSubmit={handleSubmit} isRunning={!!activeJobId} />

            <div className="mt-10">
              {sessionsLoading && localJobs.length === 0 ? (
                <LoadingSkeleton />
              ) : (
                <JobsFeed
                  jobs={allJobs}
                  activeJobId={activeJobId}
                  selectedJobId={runningJob?.id ?? null}
                  onSelect={handleSelect}
                />
              )}
            </div>
          </>
        ) : (
          <CanvasShell />
        )}
      </main>

      {/* Drawer only for the live running job */}
      <ReportDrawer
        job={runningJob?.status === "running" ? runningJob : null}
        onClose={() => setRunningJob(null)}
        onCancel={() => { cancel(); setRunningJob(null); }}
      />
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="space-y-2">
      {[...Array(4)].map((_, i) => (
        <div
          key={i}
          className="h-16 w-full rounded-xl animate-pulse"
          style={{ background: "var(--surface-alt)", opacity: 1 - i * 0.15 }}
        />
      ))}
    </div>
  );
}
