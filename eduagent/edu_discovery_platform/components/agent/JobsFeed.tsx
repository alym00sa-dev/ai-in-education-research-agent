"use client";
import { Job } from "@/lib/types";
import JobRow from "./JobRow";
import { Inbox } from "lucide-react";

interface JobsFeedProps {
  jobs: Job[];
  activeJobId: string | null;
  selectedJobId: string | null;
  onSelect: (job: Job) => void;
}

export default function JobsFeed({ jobs, activeJobId, selectedJobId, onSelect }: JobsFeedProps) {
  if (jobs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div
          className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl"
          style={{ background: "var(--surface-alt)", border: "1px solid var(--border)" }}
        >
          <Inbox size={20} style={{ color: "var(--text-muted)" }} />
        </div>
        <p className="text-sm font-medium" style={{ color: "var(--text-secondary)" }}>No sessions yet</p>
        <p className="mt-1 text-xs" style={{ color: "var(--text-muted)" }}>
          Submit a query above to start your first research session
        </p>
      </div>
    );
  }

  const running = jobs.filter((j) => j.status === "running");
  const past = jobs.filter((j) => j.status !== "running");

  return (
    <div className="space-y-6">
      {running.length > 0 && (
        <section>
          <SectionHeader label="Active" count={running.length} />
          <div className="space-y-2">
            {running.map((job) => (
              <JobRow
                key={job.id}
                job={job}
                isActive={job.id === selectedJobId || job.id === activeJobId}
                onClick={() => onSelect(job)}
              />
            ))}
          </div>
        </section>
      )}

      {past.length > 0 && (
        <section>
          <SectionHeader label="Past Sessions" count={past.length} />
          <div className="space-y-2">
            {past.map((job) => (
              <JobRow
                key={job.id}
                job={job}
                isActive={job.id === selectedJobId}
                onClick={() => onSelect(job)}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function SectionHeader({ label, count }: { label: string; count: number }) {
  return (
    <div className="mb-3 flex items-center gap-2">
      <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>
        {label}
      </span>
      <span
        className="rounded-full px-1.5 py-0.5 text-[11px] font-medium"
        style={{ background: "var(--surface-alt)", color: "var(--text-muted)" }}
      >
        {count}
      </span>
    </div>
  );
}
