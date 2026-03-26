"use client";
import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { Job, TOOL_CATEGORIES } from "@/lib/types";
import { ArrowLeft, ExternalLink, Brain, FileText, Link2, ChevronDown, Download } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { formatDate } from "@/lib/utils";

type Tab = "report" | "evidence" | "thoughts" | "downloads";

export default function SessionPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<Tab>("report");
  const [metaOpen, setMetaOpen] = useState(false);

  useEffect(() => {
    // 1. Try localStorage first
    try {
      const raw = localStorage.getItem("eduagent_jobs");
      if (raw) {
        const jobs: Job[] = JSON.parse(raw);
        const found = jobs.find((j) => j.id === id);
        if (found) {
          setJob(found);
          setLoading(false);
          return;
        }
      }
    } catch {}

    // 2. Fall back to sessions API
    fetch("/api/sessions")
      .then((r) => r.json())
      .then((data) => {
        const sessions = data.sessions ?? [];
        const match = sessions.find(
          (s: { session_id: string }) => s.session_id === id
        );
        if (match) {
          setJob({
            id: match.session_id,
            query: match.query,
            config: {
              taskType: "",
              model: match.model_provider?.replace(/^(openai:|anthropic:)/, "") ?? "gpt-4.1",
              depth: match.search_depth ?? "standard",
              maxSources: 30,
            },
            status: match.status === "active" ? "complete" : (match.status ?? "complete"),
            createdAt: isNaN(Number(match.created_at))
              ? new Date(match.created_at).getTime()
              : Number(match.created_at),
            report: match.research_report ?? undefined,
            paperCount: match.paper_count ?? undefined,
          });
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: "var(--bg)" }}>
        <div className="h-6 w-6 rounded-full border-2 border-zinc-200 border-t-zinc-400 animate-spin" />
      </div>
    );
  }

  if (!job) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4" style={{ background: "var(--bg)" }}>
        <p className="text-sm" style={{ color: "var(--text-muted)" }}>Session not found.</p>
        <button onClick={() => router.push("/agent")} className="text-sm underline" style={{ color: "var(--text-secondary)" }}>
          Back to research
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{ background: "var(--bg)" }}>
      {/* Header */}
      <div
        className="sticky top-0 z-10 border-b px-6 py-4"
        style={{ background: "var(--surface)", borderColor: "var(--border)" }}
      >
        <div className="mx-auto max-w-4xl">
          <div className="flex items-start gap-4">
            <button
              onClick={() => router.push("/agent")}
              className="mt-0.5 flex-shrink-0 flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs transition-colors"
              style={{ color: "var(--text-muted)" }}
              onMouseEnter={(e) => (e.currentTarget.style.background = "var(--surface-alt)")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
            >
              <ArrowLeft size={13} />
              Back
            </button>

            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium leading-snug" style={{ color: "var(--text-primary)" }}>
                {job.query}
              </p>
              {/* Collapsible metadata */}
              <button
                onClick={() => setMetaOpen((o) => !o)}
                className="mt-1.5 flex items-center gap-1 text-xs transition-colors"
                style={{ color: "var(--text-muted)" }}
              >
                <span>Session details</span>
                <ChevronDown
                  size={12}
                  style={{ transform: metaOpen ? "rotate(180deg)" : "rotate(0deg)", transition: "transform 150ms" }}
                />
              </button>
              {metaOpen && (
                <div
                  className="mt-2 rounded-lg px-3 py-2.5 grid grid-cols-2 gap-x-6 gap-y-1.5"
                  style={{ background: "var(--surface-alt)", border: "1px solid var(--border-subtle)" }}
                >
                  {[
                    ["Model", job.config.model],
                    ["Search Rigor", job.config.depth],
                    ["Top-K", String(job.config.maxSources)],
                    ["Task Type", job.config.taskType || "streamlit-research"],
                    ["Agent Version", job.config.agentVersion || "v1"],
                    ["Date", formatDate(job.createdAt)],
                    ...(job.config.keywords ? [["Keywords", job.config.keywords]] : []),
                  ].map(([label, value]) => (
                    <div key={label} className="flex items-baseline gap-1.5">
                      <span className="text-[11px] font-medium" style={{ color: "var(--text-muted)" }}>{label}</span>
                      <span className="text-[11px]" style={{ color: "var(--text-secondary)" }}>{value}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Tabs */}
          <div className="mt-4 flex gap-1">
            {([
              { key: "report" as Tab, label: "Report", icon: FileText },
              { key: "evidence" as Tab, label: `Evidence Log${job.sources?.length ? ` (${job.sources.length})` : ""}`, icon: Link2 },
              { key: "thoughts" as Tab, label: `Agent Thoughts${job.thoughts?.length ? ` (${job.thoughts.length})` : ""}`, icon: Brain },
              { key: "downloads" as Tab, label: "Downloads", icon: Download },
            ]).map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                onClick={() => setTab(key)}
                className="flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-all"
                style={{
                  background: tab === key ? "var(--surface-alt)" : "transparent",
                  color: tab === key ? "var(--text-primary)" : "var(--text-muted)",
                }}
              >
                <Icon size={12} />
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="mx-auto max-w-4xl px-6 py-8 pb-24">
        {tab === "report" && <ReportTab job={job} />}
        {tab === "evidence" && <SourcesTab job={job} />}
        {tab === "thoughts" && <ThoughtsTab job={job} />}
        {tab === "downloads" && <DownloadsTab job={job} />}
      </div>
    </div>
  );
}

function ReportTab({ job }: { job: Job }) {
  if (job.status === "running" && !job.report) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <div className="mb-3 h-6 w-6 rounded-full border-2 border-zinc-200 border-t-zinc-400 animate-spin" />
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>Research in progress…</p>
        <p className="mt-1 text-xs" style={{ color: "var(--text-muted)" }}>Check the Thoughts tab for live updates</p>
      </div>
    );
  }

  if (job.status === "failed") {
    return (
      <div className="rounded-xl p-4 max-w-xl" style={{ background: "#fff1f2", border: "1px solid #fecdd3" }}>
        <p className="text-sm font-medium" style={{ color: "#dc2626" }}>Research failed</p>
        <p className="mt-1 text-xs" style={{ color: "#ef4444" }}>{job.error || "Unknown error"}</p>
      </div>
    );
  }

  if (!job.report) {
    return <p className="text-sm" style={{ color: "var(--text-muted)" }}>No report available.</p>;
  }

  return (
    <div className="prose prose-sm max-w-none" style={{ color: "var(--text-primary)" }}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => <h1 className="mt-8 mb-3 text-xl font-semibold" style={{ color: "var(--text-primary)" }}>{children}</h1>,
          h2: ({ children }) => <h2 className="mt-6 mb-2 text-base font-semibold" style={{ color: "var(--text-primary)" }}>{children}</h2>,
          h3: ({ children }) => <h3 className="mt-5 mb-2 text-sm font-semibold" style={{ color: "var(--text-primary)" }}>{children}</h3>,
          p: ({ children }) => <p className="mb-4 text-sm leading-relaxed" style={{ color: "var(--text-secondary)" }}>{children}</p>,
          ul: ({ children }) => <ul className="mb-4 space-y-1.5 pl-5">{children}</ul>,
          ol: ({ children }) => <ol className="mb-4 space-y-1.5 pl-5 list-decimal">{children}</ol>,
          li: ({ children }) => <li className="text-sm leading-relaxed list-disc" style={{ color: "var(--text-secondary)" }}>{children}</li>,
          a: ({ href, children }) => (
            <a href={href} target="_blank" rel="noopener noreferrer" className="underline underline-offset-2" style={{ color: "var(--indigo)" }}>
              {children}
            </a>
          ),
          strong: ({ children }) => <strong style={{ color: "var(--text-primary)", fontWeight: 600 }}>{children}</strong>,
          blockquote: ({ children }) => (
            <blockquote className="border-l-2 pl-4 italic my-4" style={{ borderColor: "var(--border)", color: "var(--text-muted)" }}>{children}</blockquote>
          ),
          hr: () => <hr style={{ borderColor: "var(--border)", margin: "24px 0" }} />,
          table: ({ children }) => (
            <div className="overflow-x-auto my-6">
              <table className="w-full text-xs border-collapse">{children}</table>
            </div>
          ),
          th: ({ children }) => <th className="px-3 py-2 text-left font-semibold" style={{ borderBottom: "1px solid var(--border)", color: "var(--text-primary)" }}>{children}</th>,
          td: ({ children }) => <td className="px-3 py-2" style={{ borderBottom: "1px solid var(--border-subtle)", color: "var(--text-secondary)" }}>{children}</td>,
        }}
      >
        {job.report}
      </ReactMarkdown>
    </div>
  );
}

function SourcesTab({ job }: { job: Job }) {
  return (
    <div className="space-y-6">
      {/* Search Activity */}
      {job.toolCalls && Object.keys(job.toolCalls).length > 0 && (
        <div>
          <p className="mb-3 text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>
            Search Activity
          </p>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            {Object.entries(TOOL_CATEGORIES).map(([catKey, cat]) => {
              const total = cat.tools.reduce((sum, t) => sum + (job.toolCalls?.[t] ?? 0), 0);
              const breakdown = cat.tools
                .filter((t) => (job.toolCalls?.[t] ?? 0) > 0)
                .map((t) => `${t.replace(/_search$/, "").replace(/_/g, " ")}: ${job.toolCalls![t]}`)
                .join(", ");
              return (
                <div
                  key={catKey}
                  className="rounded-lg px-3 py-2.5"
                  style={{ background: "var(--surface-alt)", border: "1px solid var(--border-subtle)" }}
                >
                  <p className="text-[11px] font-medium" style={{ color: "var(--text-muted)" }}>{cat.label}</p>
                  <p className="mt-0.5 text-lg font-semibold tabular-nums" style={{ color: "var(--text-primary)" }}>
                    {total}
                  </p>
                  {breakdown && (
                    <p className="mt-1 text-[10px] leading-tight" style={{ color: "var(--text-muted)" }}>{breakdown}</p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Sources list */}
      {!job.sources || job.sources.length === 0 ? (
        <p className="text-sm" style={{ color: "var(--text-muted)" }}>No sources extracted yet.</p>
      ) : (
        <div>
          <p className="mb-3 text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>
            Sources ({job.sources.length})
          </p>
          <div className="space-y-2">
            {job.sources.map((source, i) => (
              <a
                key={i}
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-start gap-3 rounded-lg p-3 transition-colors group"
                style={{ border: "1px solid var(--border-subtle)" }}
                onMouseEnter={(e) => (e.currentTarget.style.background = "var(--surface-alt)")}
                onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
              >
                <div
                  className="mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded text-[10px] font-medium"
                  style={{ background: "var(--surface-alt)", color: "var(--text-muted)", border: "1px solid var(--border)" }}
                >
                  {i + 1}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-medium leading-snug" style={{ color: "var(--text-primary)" }}>
                    {source.title || source.url}
                  </p>
                  <p className="mt-0.5 truncate text-[11px]" style={{ color: "var(--text-muted)" }}>{source.url}</p>
                </div>
                <ExternalLink size={12} className="flex-shrink-0 mt-0.5 opacity-0 group-hover:opacity-100 transition-opacity" style={{ color: "var(--text-muted)" }} />
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function DownloadsTab({ job }: { job: Job }) {
  const slug = job.query.slice(0, 40).replace(/[^a-z0-9]+/gi, "_").toLowerCase();

  const downloadText = (content: string, filename: string, mime = "text/plain") => {
    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleReport = () => {
    if (!job.report) return;
    downloadText(job.report, `${slug}_report.md`, "text/markdown");
  };

  const handleEvidenceCSV = () => {
    const lines: string[] = [];

    // Tool usage section
    if (job.toolCalls && Object.keys(job.toolCalls).length > 0) {
      lines.push("Search Activity");
      lines.push("Tool,Calls");
      for (const [tool, count] of Object.entries(job.toolCalls).sort((a, b) => b[1] - a[1])) {
        lines.push(`"${tool}",${count}`);
      }
      lines.push("");
    }

    // Sources section
    if (job.sources?.length) {
      lines.push("Sources");
      lines.push("No.,Title,URL");
      for (const [i, s] of job.sources.entries()) {
        lines.push(`${i + 1},"${(s.title || s.url).replace(/"/g, '""')}","${s.url}"`);
      }
    }

    if (lines.length === 0) return;
    downloadText(lines.join("\n"), `${slug}_evidence_log.csv`, "text/csv");
  };

  const handleThoughtsJSON = () => {
    if (!job.thoughts?.length) return;
    downloadText(JSON.stringify(job.thoughts, null, 2), `${slug}_thoughts.json`, "application/json");
  };

  const exports = [
    {
      label: "Research Report",
      description: "Full report in Markdown format",
      ext: ".md",
      disabled: !job.report,
      onClick: handleReport,
    },
    {
      label: "Evidence Log",
      description: `${job.sources?.length ?? 0} sources · tool usage in CSV format`,
      ext: ".csv",
      disabled: !job.sources?.length && !job.toolCalls,
      onClick: handleEvidenceCSV,
    },
    {
      label: "Agent Thoughts",
      description: "LLM reasoning trail in JSON format",
      ext: ".json",
      disabled: !job.thoughts?.length,
      onClick: handleThoughtsJSON,
    },
  ];

  return (
    <div className="space-y-3 max-w-lg">
      {exports.map(({ label, description, ext, disabled, onClick }) => (
        <button
          key={label}
          onClick={onClick}
          disabled={disabled}
          className="w-full flex items-center justify-between rounded-xl px-4 py-3.5 text-left transition-colors disabled:opacity-40"
          style={{ border: "1px solid var(--border)", background: "var(--surface)" }}
          onMouseEnter={(e) => { if (!disabled) (e.currentTarget as HTMLElement).style.background = "var(--surface-alt)"; }}
          onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = "var(--surface)"; }}
        >
          <div>
            <p className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>{label}</p>
            <p className="mt-0.5 text-xs" style={{ color: "var(--text-muted)" }}>{description}</p>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <span
              className="rounded px-1.5 py-0.5 text-[11px] font-mono font-medium"
              style={{ background: "var(--surface-alt)", color: "var(--text-muted)", border: "1px solid var(--border-subtle)" }}
            >
              {ext}
            </span>
            <Download size={14} style={{ color: "var(--text-muted)" }} />
          </div>
        </button>
      ))}
    </div>
  );
}

function ThoughtsTab({ job }: { job: Job }) {
  if (!job.thoughts || job.thoughts.length === 0) {
    return <p className="text-sm" style={{ color: "var(--text-muted)" }}>No thoughts recorded for this session.</p>;
  }

  return (
    <div className="space-y-3">
      {job.thoughts.map((t, i) => (
        <div
          key={i}
          className="rounded-lg p-3"
          style={{
            background: t.type === "critique" ? "#fef9ee" : "var(--surface-alt)",
            border: `1px solid ${t.type === "critique" ? "#fed7aa" : "var(--border-subtle)"}`,
          }}
        >
          {t.type === "sub_researcher_start" ? (
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-semibold uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>
                Sub-researcher
              </span>
              <span className="text-xs font-medium" style={{ color: "var(--text-primary)" }}>{t.content}</span>
            </div>
          ) : (
            <>
              <div className="mb-1.5 flex items-center gap-2">
                <span
                  className="text-[10px] font-semibold uppercase tracking-wider"
                  style={{ color: t.type === "critique" ? "#d97706" : "var(--text-muted)" }}
                >
                  {t.type === "critique" ? "Critique" : "Thought"}
                </span>
                {t.metadata?.research_topic != null && (
                  <span className="text-[10px] rounded px-1.5 py-0.5" style={{ background: "var(--border)", color: "var(--text-muted)" }}>
                    {String(t.metadata.research_topic).slice(0, 60)}
                  </span>
                )}
              </div>
              <p className="text-xs leading-relaxed" style={{ color: "var(--text-secondary)" }}>{t.content}</p>
            </>
          )}
        </div>
      ))}
    </div>
  );
}
