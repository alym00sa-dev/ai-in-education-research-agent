"use client";
import { useState, useCallback, useMemo, useEffect, useRef, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { v4 as uuidv4 } from "uuid";
import { Job, ResearchConfig, GraphSession } from "@/lib/types";
import { useJobs } from "@/hooks/useJobs";
import { useResearch } from "@/hooks/useResearch";
import { useLocalRuns } from "@/hooks/useLocalRuns";
import { useGraphSessions } from "@/hooks/useGraphSessions";
import Navbar from "@/components/layout/Navbar";
import QueryBar from "@/components/agent/QueryBar";
import JobsFeed from "@/components/agent/JobsFeed";
import ReportDrawer from "@/components/agent/ReportDrawer";

type AgentTab = "deep-research" | "graph-traversal";

export default function AgentPage() {
  return (
    <Suspense fallback={null}>
      <AgentPageInner />
    </Suspense>
  );
}

function AgentPageInner() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialTab = searchParams.get("tab") === "graph-traversal" ? "graph-traversal" : "deep-research";
  const [agentTab, setAgentTab] = useState<AgentTab>(initialTab as AgentTab);
  const [runningJob, setRunningJob] = useState<Job | null>(null);

  const { sessions: graphSessions, addSession: addGraphSession, removeSession: removeGraphSession } = useGraphSessions();

  const { jobs: localJobs, addJob, updateJob, removeJob } = useJobs();
  const { localRuns, loading: runsLoading } = useLocalRuns();

  const allJobs = useMemo(() => {
    // Build a map: id → job, preferring complete over running
    // This handles the case where user closed tab mid-run and pipeline completed
    const byId = new Map<string, Job>();

    // Add local pipeline runs saved to disk (complete)
    for (const r of localRuns) {
      byId.set(r.id, r);
    }

    // Add local in-memory jobs — merge with disk version when both exist,
    // preferring localStorage's config (has the real model selection)
    for (const j of localJobs) {
      const existing = byId.get(j.id);
      if (!existing) {
        byId.set(j.id, j);
      } else if (existing.status !== "complete") {
        byId.set(j.id, j);
      } else {
        // Disk run is complete — keep disk data but use localStorage config for model accuracy
        byId.set(j.id, { ...existing, config: j.config });
      }
    }

    return Array.from(byId.values())
      .sort((a, b) => (b.createdAt ?? 0) - (a.createdAt ?? 0));
  }, [localJobs, localRuns]);

  const handleUpdate = useCallback(
    (id: string, patch: Partial<Job>) => {
      updateJob(id, patch);
      setRunningJob((prev) => (prev?.id === id ? { ...prev, ...patch } : prev));
    },
    [updateJob]
  );

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

  const handleSubmit = useCallback(
    (query: string, config: ResearchConfig) => {
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
    },
    [addJob, startResearch]
  );

  const handleSelect = useCallback(
    (job: Job) => {
      if (job.status === "running") {
        setRunningJob(job);
      } else {
        router.push(`/agent/${job.id}`);
      }
    },
    [router]
  );

  const handleRerun = useCallback(
    (job: Job) => {
      handleSubmit(job.query, job.config);
    },
    [handleSubmit]
  );

  const handleDelete = useCallback(
    (id: string) => {
      removeJob(id);
    },
    [removeJob]
  );

  return (
    <div className="min-h-screen" style={{ background: "var(--bg)" }}>
      <Navbar />

      {/* Query bar + tabs — constrained width */}
      <div className="mx-auto max-w-5xl px-6 pt-8">
        {/* Tab bar */}
        <div
          className="mb-8 flex items-center gap-0 border-b"
          style={{ borderColor: "var(--border)" }}
        >
          {(["deep-research", "graph-traversal"] as AgentTab[]).map((tab) => (
            <button
              key={tab}
              onClick={() => setAgentTab(tab)}
              className="px-4 py-2.5 text-sm font-medium transition-colors duration-150"
              style={{
                color:
                  agentTab === tab
                    ? "var(--text-primary)"
                    : "var(--text-muted)",
                borderBottom:
                  agentTab === tab
                    ? "2px solid var(--text-primary)"
                    : "2px solid transparent",
                marginBottom: "-1px",
              }}
            >
              {tab === "deep-research" ? "Deep Research" : (
                <>
                  Graph Traversal
                  <span style={{ fontSize: "10px", fontWeight: 600, color: "var(--text-muted)", marginLeft: "6px", letterSpacing: "0.05em" }}>BETA</span>
                </>
              )}
            </button>
          ))}
        </div>

        {agentTab === "deep-research" && (
          <QueryBar onSubmit={handleSubmit} isRunning={!!activeJobId} />
        )}
        {agentTab === "graph-traversal" && (
          <GraphTraversalQueryBar
            onSubmit={(query, model) => {
              const id = uuidv4();
              const session: GraphSession = {
                id,
                firstQuery: query,
                createdAt: Date.now(),
                updatedAt: Date.now(),
                messages: [],
                model,
              };
              addGraphSession(session);
              router.push(`/agent/graph/${id}`);
            }}
          />
        )}
      </div>

      {/* Sessions — wider container */}
      <div className="mx-auto max-w-7xl px-6 mt-10 pb-24">
        {agentTab === "deep-research" && (
          runsLoading && allJobs.length === 0 ? (
            <LoadingSkeleton />
          ) : (
            <JobsFeed
              jobs={allJobs}
              activeJobId={activeJobId}
              selectedJobId={runningJob?.id ?? null}
              onSelect={handleSelect}
              onRerun={handleRerun}
              onDelete={handleDelete}
            />
          )
        )}
        {agentTab === "graph-traversal" && (
          <GraphSessionsFeed
            sessions={graphSessions}
            onSelect={(s) => router.push(`/agent/graph/${s.id}`)}
            onDelete={removeGraphSession}
          />
        )}
      </div>

      {/* Drawer only for the live running job */}
      <ReportDrawer
        job={runningJob?.status === "running" ? runningJob : null}
        onClose={() => setRunningJob(null)}
        onCancel={() => {
          cancel();
          setRunningJob(null);
        }}
      />
    </div>
  );
}

function GraphTraversalQueryBar({
  onSubmit,
}: {
  onSubmit: (query: string, model: string) => void;
}) {
  const [query, setQuery] = useState("");
  const [model, setModel] = useState("gpt-5.4-mini");

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      if (query.trim()) onSubmit(query.trim(), model);
    },
    [query, model, onSubmit]
  );

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div
        className="flex items-center gap-3 rounded-xl border px-4 py-3"
        style={{ borderColor: "var(--border)", background: "var(--surface)" }}
      >
        {/* Graph icon */}
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ color: "var(--text-muted)", flexShrink: 0 }}>
          <circle cx="18" cy="5" r="3" /><circle cx="6" cy="12" r="3" /><circle cx="18" cy="19" r="3" />
          <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" /><line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
        </svg>
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Ask about the research corpus — e.g. What RCT evidence exists for ChatGPT in K-12?"
          className="flex-1 bg-transparent text-sm outline-none"
          style={{ color: "var(--text-primary)" }}
          autoFocus
        />
        <select
          value={model}
          onChange={e => setModel(e.target.value)}
          className="text-xs rounded-md px-2 py-1 outline-none border"
          style={{ background: "var(--surface-alt)", color: "var(--text-secondary)", borderColor: "var(--border)" }}
        >
          <option value="gpt-5.4-mini">GPT-5.4 Mini</option>
          <option value="gpt-5.4">GPT-5.4</option>
          <option value="claude-sonnet-4-6">Claude Sonnet</option>
          <option value="claude-haiku-4-5">Claude Haiku</option>
        </select>
        <button
          type="submit"
          disabled={!query.trim()}
          className="rounded-lg px-3 py-1.5 text-xs font-medium transition-colors disabled:opacity-40"
          style={{ background: "var(--text-primary)", color: "var(--bg)" }}
        >
          Ask
        </button>
      </div>

    </form>
  );
}

function GraphSessionsFeed({
  sessions,
  onSelect,
  onDelete,
}: {
  sessions: GraphSession[];
  onSelect: (s: GraphSession) => void;
  onDelete: (id: string) => void;
}) {
  if (sessions.length === 0) {
    return (
      <p className="text-sm text-center py-12" style={{ color: "var(--text-muted)" }}>
        No conversations yet. Ask a question above to start exploring.
      </p>
    );
  }

  return (
    <div>
      <p className="text-xs mb-3" style={{ color: "var(--text-muted)" }}>
        Past conversations
      </p>
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr style={{ borderBottom: "1px solid var(--border)" }}>
            {["Query", "Model", "Messages", "Date"].map(h => (
              <th key={h} className="text-left py-2 px-3 text-xs font-medium" style={{ color: "var(--text-muted)" }}>
                {h}
              </th>
            ))}
            <th />
          </tr>
        </thead>
        <tbody>
          {sessions.map(s => (
            <tr
              key={s.id}
              onClick={() => onSelect(s)}
              className="group cursor-pointer transition-colors duration-100"
              style={{ borderBottom: "1px solid var(--border)" }}
              onMouseEnter={e => (e.currentTarget.style.background = "var(--surface-alt)")}
              onMouseLeave={e => (e.currentTarget.style.background = "transparent")}
            >
              <td className="py-2.5 px-3 max-w-xs truncate" style={{ color: "var(--text-primary)" }}>
                {s.firstQuery}
              </td>
              <td className="py-2.5 px-3 text-xs" style={{ color: "var(--text-muted)" }}>
                {s.model}
              </td>
              <td className="py-2.5 px-3 text-xs" style={{ color: "var(--text-muted)" }}>
                {Math.ceil(s.messages.length / 2)} turn{Math.ceil(s.messages.length / 2) !== 1 ? "s" : ""}
              </td>
              <td className="py-2.5 px-3 text-xs whitespace-nowrap" style={{ color: "var(--text-muted)" }}>
                {new Date(s.createdAt).toLocaleDateString()}
              </td>
              <td className="py-2.5 px-3">
                <div className="flex items-center justify-end opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={e => { e.stopPropagation(); onDelete(s.id); }}
                    title="Delete"
                    className="rounded-md p-1.5 transition-colors"
                    style={{ color: "var(--text-muted)" }}
                    onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = "#fff1f2"; (e.currentTarget as HTMLElement).style.color = "#dc2626"; }}
                    onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = "transparent"; (e.currentTarget as HTMLElement).style.color = "var(--text-muted)"; }}
                  >
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="space-y-2">
      {[...Array(4)].map((_, i) => (
        <div
          key={i}
          className="h-10 w-full rounded-lg animate-pulse"
          style={{ background: "var(--surface-alt)", opacity: 1 - i * 0.15 }}
        />
      ))}
    </div>
  );
}
