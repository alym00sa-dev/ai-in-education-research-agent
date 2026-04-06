"use client";
import { useState } from "react";
import { Job } from "@/lib/types";
import { formatDate } from "@/lib/utils";
import { Inbox, Loader2, RotateCcw, Trash2 } from "lucide-react";

interface JobsFeedProps {
  jobs: Job[];
  activeJobId: string | null;
  selectedJobId: string | null;
  onSelect: (job: Job) => void;
  onRerun: (job: Job) => void;
  onDelete: (id: string) => void;
}

const STATUS_CONFIG = {
  running: { color: "#d97706", bg: "#fef9ee", label: "Running", dot: "#f59e0b" },
  complete: { color: "#16a34a", bg: "#f0fdf4", label: "Complete", dot: "#22c55e" },
  failed: { color: "#dc2626", bg: "#fff1f2", label: "Failed", dot: "#ef4444" },
};

function getJobType(taskType: string): string {
  if (taskType === "graph-traversal") return "Graph Traversal";
  return "Deep Research";
}

export default function JobsFeed({
  jobs,
  activeJobId,
  selectedJobId,
  onSelect,
  onRerun,
  onDelete,
}: JobsFeedProps) {
  if (jobs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div
          className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl"
          style={{
            background: "var(--surface-alt)",
            border: "1px solid var(--border)",
          }}
        >
          <Inbox size={20} style={{ color: "var(--text-muted)" }} />
        </div>
        <p
          className="text-sm font-medium"
          style={{ color: "var(--text-secondary)" }}
        >
          No sessions yet
        </p>
        <p className="mt-1 text-xs" style={{ color: "var(--text-muted)" }}>
          Submit a query above to start your first research session
        </p>
      </div>
    );
  }

  const running = jobs.filter((j) => j.status === "running");
  const past = jobs.filter((j) => j.status !== "running");

  const [statusFilter, setStatusFilter] = useState<"all" | "complete" | "failed">("all");
  const [search, setSearch] = useState("");

  const filteredPast = past.filter((j) => {
    if (statusFilter !== "all" && j.status !== statusFilter) return false;
    if (search && !j.query.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Running jobs — compact banner rows */}
      {running.length > 0 && (
        <section>
          <SectionLabel label="Active" count={running.length} />
          <div className="space-y-2">
            {running.map((job) => (
              <ActiveJobBanner
                key={job.id}
                job={job}
                isSelected={
                  job.id === selectedJobId || job.id === activeJobId
                }
                onClick={() => onSelect(job)}
              />
            ))}
          </div>
        </section>
      )}

      {/* Past sessions — table */}
      {past.length > 0 && (
        <section>
          <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
            <SectionLabel label="Past Sessions" count={filteredPast.length} />

            {/* Filters */}
            <div className="flex flex-wrap items-center gap-2">
              {/* Search */}
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search queries…"
                className="rounded-lg px-3 py-1.5 text-xs focus:outline-none"
                style={{
                  border: "1px solid var(--border)",
                  background: "var(--surface)",
                  color: "var(--text-primary)",
                  width: "180px",
                }}
              />

              {/* Status filter */}
              <FilterPills
                options={[
                  { value: "all", label: "All" },
                  { value: "complete", label: "Complete" },
                  { value: "failed", label: "Failed" },
                ]}
                value={statusFilter}
                onChange={(v) => setStatusFilter(v as typeof statusFilter)}
              />

            </div>
          </div>

          <table className="w-full text-sm border-collapse">
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border)" }}>
                  <th
                    className="py-2 px-3 text-left text-xs font-medium hidden sm:table-cell w-24"
                    style={{ color: "var(--text-muted)" }}
                  >
                    ID
                  </th>
                  <th
                    className="py-2 px-3 text-left text-xs font-medium"
                    style={{ color: "var(--text-muted)" }}
                  >
                    Query
                  </th>
                  <th
                    className="py-2 px-3 text-left text-xs font-medium hidden sm:table-cell w-20"
                    style={{ color: "var(--text-muted)" }}
                  >
                    Model
                  </th>
                  <th
                    className="py-2 px-3 text-left text-xs font-medium hidden sm:table-cell"
                    style={{ color: "var(--text-muted)" }}
                  >
                    Date
                  </th>
                  <th
                    className="py-2 px-3 text-left text-xs font-medium hidden sm:table-cell w-20"
                    style={{ color: "var(--text-muted)" }}
                  >
                    Time
                  </th>
                  <th
                    className="py-2 px-3 text-left text-xs font-medium hidden sm:table-cell w-32"
                    style={{ color: "var(--text-muted)" }}
                  >
                    Type
                  </th>
                  <th
                    className="py-2 px-3 text-left text-xs font-medium"
                    style={{ color: "var(--text-muted)" }}
                  >
                    Status
                  </th>
                  <th className="py-2 px-3 w-20" />
                </tr>
              </thead>
              <tbody>
                {filteredPast.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-xs" style={{ color: "var(--text-muted)" }}>
                      No sessions match your filters.
                    </td>
                  </tr>
                ) : (
                  filteredPast.map((job, i) => (
                    <SessionRow
                      key={job.id}
                      job={job}
                      isActive={job.id === selectedJobId}
                      isLast={i === filteredPast.length - 1}
                      onClick={() => onSelect(job)}
                      onRerun={() => onRerun(job)}
                      onDelete={() => onDelete(job.id)}
                    />
                  ))
                )}
              </tbody>
            </table>
        </section>
      )}
    </div>
  );
}

function getMode(model: string): string {
  if (!model) return "—";
  const m = model.toLowerCase();
  if (m.includes("mini") || m.includes("haiku")) return "GPT 5.4 Mini";
  if (m.includes("5.4") || m.includes("5.2") || m.includes("opus") || m.includes("sonnet")) return "GPT 5.4";
  return "—";
}

function getModeKey(model: string): "fast" | "slow" | "unknown" {
  if (!model) return "unknown";
  const m = model.toLowerCase();
  if (m.includes("mini") || m.includes("haiku")) return "fast";
  if (m.includes("5.4") || m.includes("5.2") || m.includes("opus") || m.includes("sonnet")) return "slow";
  return "unknown";
}

function SessionRow({
  job,
  isActive,
  isLast,
  onClick,
  onRerun,
  onDelete,
}: {
  job: Job;
  isActive: boolean;
  isLast: boolean;
  onClick: () => void;
  onRerun: () => void;
  onDelete: () => void;
}) {
  const s = STATUS_CONFIG[job.status];
  const mode = getMode(job.config.model);
  const shortId = job.id.replace(/-/g, "").slice(0, 7).toUpperCase();
  const jobType = getJobType(job.config.taskType);

  return (
    <tr
      onClick={onClick}
      className="group cursor-pointer transition-colors duration-100"
      style={{
        background: isActive ? "var(--surface-alt)" : "transparent",
        borderBottom: isLast ? "none" : "1px solid var(--border)",
      }}
      onMouseEnter={(e) => {
        if (!isActive)
          (e.currentTarget as HTMLElement).style.background =
            "var(--surface-alt)";
      }}
      onMouseLeave={(e) => {
        if (!isActive)
          (e.currentTarget as HTMLElement).style.background = "transparent";
      }}
    >
      {/* ID */}
      <td
        className="px-3 py-2.5 hidden sm:table-cell"
        style={{ color: "var(--text-muted)" }}
      >
        <span className="font-mono text-[11px]">{shortId}</span>
      </td>

      {/* Query */}
      <td
        className="px-3 py-2.5 text-sm"
        style={{ color: "var(--text-primary)" }}
      >
        <p className="leading-snug">{job.query}</p>
      </td>

      {/* Model */}
      <td
        className="px-3 py-2.5 text-xs hidden sm:table-cell whitespace-nowrap"
        style={{ color: "var(--text-muted)" }}
      >
        {mode}
      </td>

      {/* Date */}
      <td
        className="px-3 py-2.5 text-xs hidden sm:table-cell whitespace-nowrap"
        style={{ color: "var(--text-muted)" }}
      >
        {formatDate(job.createdAt)}
      </td>

      {/* Time */}
      <td
        className="px-3 py-2.5 text-xs hidden sm:table-cell whitespace-nowrap"
        style={{ color: "var(--text-muted)" }}
      >
        {job.elapsed ?? "—"}
      </td>

      {/* Type */}
      <td
        className="px-3 py-2.5 text-xs hidden sm:table-cell whitespace-nowrap"
        style={{ color: "var(--text-muted)" }}
      >
        {jobType}
      </td>

      {/* Status */}
      <td className="px-3 py-2.5 text-left">
        <span
          className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium"
          style={{ background: s.bg, color: s.color }}
        >
          <span
            className="h-1.5 w-1.5 rounded-full"
            style={{ background: s.dot }}
          />
          {s.label}
        </span>
      </td>

      {/* Actions */}
      <td className="px-3 py-2.5">
        <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={(e) => { e.stopPropagation(); onRerun(); }}
            title="Re-run"
            className="rounded-md p-1.5 transition-colors"
            style={{ color: "var(--text-muted)" }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = "var(--surface-alt)"; (e.currentTarget as HTMLElement).style.color = "var(--text-primary)"; }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = "transparent"; (e.currentTarget as HTMLElement).style.color = "var(--text-muted)"; }}
          >
            <RotateCcw size={13} />
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); onDelete(); }}
            title="Delete"
            className="rounded-md p-1.5 transition-colors"
            style={{ color: "var(--text-muted)" }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = "#fff1f2"; (e.currentTarget as HTMLElement).style.color = "#dc2626"; }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = "transparent"; (e.currentTarget as HTMLElement).style.color = "var(--text-muted)"; }}
          >
            <Trash2 size={13} />
          </button>
        </div>
      </td>
    </tr>
  );
}

function ActiveJobBanner({
  job,
  isSelected,
  onClick,
}: {
  job: Job;
  isSelected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="w-full text-left rounded-xl px-4 py-3 flex items-center gap-3 transition-all duration-150"
      style={{
        background: isSelected ? "var(--surface-alt)" : "var(--surface)",
        border: `1px solid ${isSelected ? "var(--border)" : "var(--border-subtle)"}`,
      }}
    >
      <Loader2
        size={14}
        className="animate-spin flex-shrink-0"
        style={{ color: "#d97706" }}
      />
      <p
        className="flex-1 text-sm font-medium leading-snug"
        style={{ color: "var(--text-primary)" }}
      >
        {job.query}
      </p>
      <span
        className="flex-shrink-0 rounded-full px-2.5 py-1 text-xs font-medium"
        style={{ background: "#fef9ee", color: "#d97706" }}
      >
        Running
      </span>
    </button>
  );
}

function SectionLabel({ label, count }: { label: string; count: number }) {
  return (
    <div className="flex items-center gap-2">
      <span
        className="text-xs font-semibold uppercase tracking-wider"
        style={{ color: "var(--text-muted)" }}
      >
        {label}
      </span>
      <span
        className="rounded-full px-1.5 py-0.5 text-[11px] font-medium"
        style={{
          background: "var(--surface-alt)",
          color: "var(--text-muted)",
        }}
      >
        {count}
      </span>
    </div>
  );
}

function FilterPills({
  options,
  value,
  onChange,
}: {
  options: { value: string; label: string }[];
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div
      className="flex items-center gap-0.5 rounded-lg p-0.5"
      style={{ background: "var(--surface-alt)", border: "1px solid var(--border-subtle)" }}
    >
      {options.map((o) => (
        <button
          key={o.value}
          onClick={() => onChange(o.value)}
          className="rounded-md px-2.5 py-1 text-xs font-medium transition-all duration-150"
          style={{
            background: value === o.value ? "var(--surface)" : "transparent",
            color: value === o.value ? "var(--text-primary)" : "var(--text-muted)",
            boxShadow: value === o.value ? "0 1px 2px rgba(0,0,0,0.07)" : "none",
          }}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}
