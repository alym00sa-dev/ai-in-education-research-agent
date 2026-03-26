"use client";
import { Job } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import { Loader2, AlertCircle } from "lucide-react";

interface JobRowProps {
  job: Job;
  isActive: boolean;
  onClick: () => void;
}

const STATUS_CONFIG = {
  running: { color: "#d97706", bg: "#fef9ee", label: "Running", dot: "#f59e0b" },
  complete: { color: "#16a34a", bg: "#f0fdf4", label: "Complete", dot: "#22c55e" },
  failed: { color: "#dc2626", bg: "#fff1f2", label: "Failed", dot: "#ef4444" },
};

export default function JobRow({ job, isActive, onClick }: JobRowProps) {
  const s = STATUS_CONFIG[job.status];
  const taskType = job.config.taskType || "streamlit-research";
  const agentVersion = job.config.agentVersion || "v1";
  const sessionShort = job.id.slice(0, 8);

  return (
    <button
      onClick={onClick}
      className="w-full text-left rounded-xl px-4 py-3.5 transition-all duration-150"
      style={{
        background: isActive ? "var(--surface-alt)" : "var(--surface)",
        border: `1px solid ${isActive ? "var(--border)" : "var(--border-subtle)"}`,
        boxShadow: isActive ? "0 1px 4px rgba(0,0,0,0.06)" : "none",
      }}
      onMouseEnter={(e) => {
        if (!isActive) (e.currentTarget as HTMLElement).style.background = "var(--surface-hover)";
      }}
      onMouseLeave={(e) => {
        if (!isActive) (e.currentTarget as HTMLElement).style.background = "var(--surface)";
      }}
    >
      <div className="flex items-start justify-between gap-3">
        {/* Left: session ID chip + query */}
        <div className="flex items-start gap-3 min-w-0">
          {/* Session ID / status icon */}
          <div
            className="mt-0.5 flex h-8 flex-shrink-0 items-center justify-center rounded-lg px-2"
            style={{ background: "var(--surface-alt)", border: "1px solid var(--border)", minWidth: "2rem" }}
          >
            {job.status === "running" ? (
              <Loader2 size={13} className="animate-spin" style={{ color: "var(--text-muted)" }} />
            ) : job.status === "failed" ? (
              <AlertCircle size={13} style={{ color: s.color }} />
            ) : (
              <span className="text-[10px] font-mono font-medium" style={{ color: "var(--text-muted)" }}>
                {sessionShort}
              </span>
            )}
          </div>

          {/* Query + meta */}
          <div className="min-w-0">
            <p className="text-sm font-medium leading-snug" style={{ color: "var(--text-primary)" }}>
              {job.query}
            </p>
            <div className="mt-1.5 flex flex-wrap items-center gap-2">
              <Badge>{taskType}</Badge>
              <Badge>{agentVersion}</Badge>
              <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                {formatDate(job.createdAt)}
              </span>
            </div>
          </div>
        </div>

        {/* Right: status pill */}
        <div
          className="flex-shrink-0 flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium"
          style={{ background: s.bg, color: s.color }}
        >
          <span
            className="h-1.5 w-1.5 rounded-full"
            style={{
              background: s.dot,
              animation: job.status === "running" ? "pulse 1.5s infinite" : "none",
            }}
          />
          {s.label}
        </div>
      </div>
    </button>
  );
}

function Badge({ children }: { children: React.ReactNode }) {
  return (
    <span
      className="rounded-md px-1.5 py-0.5 text-[11px] font-medium"
      style={{ background: "var(--surface-alt)", color: "var(--text-secondary)", border: "1px solid var(--border-subtle)" }}
    >
      {children}
    </span>
  );
}
