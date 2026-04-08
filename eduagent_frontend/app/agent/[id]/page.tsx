"use client";
import React, { useState, useEffect, useMemo, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { Job, StatusLine } from "@/lib/types";
import { ArrowLeft, Download, FileText, ClipboardCheck, Database, ScrollText, ChevronDown } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { formatDate } from "@/lib/utils";

// Parse ## and ### headers from markdown for TOC
function parseToc(markdown: string): { level: 2 | 3; text: string; slug: string }[] {
  const lines = markdown.split("\n");
  const items: { level: 2 | 3; text: string; slug: string }[] = [];
  for (const line of lines) {
    const h2 = line.match(/^## (.+)/);
    const h3 = line.match(/^### (.+)/);
    if (h2) {
      const text = h2[1].trim();
      items.push({ level: 2, text, slug: slugify(text) });
    } else if (h3) {
      const text = h3[1].trim();
      items.push({ level: 3, text, slug: slugify(text) });
    }
  }
  return items;
}

function slugify(text: string): string {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}

// Turn [N] citation markers into markdown links → [[N]](#ref-N)
// Skip if already part of an existing link: [text](url)
function linkifyCitations(md: string): string {
  return md.replace(/\[(\d+)\]/g, (match, n, offset, str) => {
    const after = str[offset + match.length];
    if (after === "(") return match; // already a link
    return `[[${n}]](#ref-${n})`;
  });
}

function runLogToStatusLog(runLog: string): StatusLine[] {
  return runLog.split("\n").filter(Boolean).map((line, i) => ({
    timestamp: i * 1000,
    text: line.replace(/^\[.*?\]\s*/, ""),
    level: "node" as const,
  }));
}

export default function SessionPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);

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

    // 2. Try sessions API
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
          setLoading(false);
          return;
        }
        // 3. Fall back to runs API (Redis on Vercel, disk locally)
        return fetch("/api/runs")
          .then((r) => r.json())
          .then((lr) => {
            const run = (lr.runs ?? []).find((r: { id: string }) => r.id === id);
            if (run) {
              // Convert runLog string → statusLog array
              const statusLog = run.runLog ? runLogToStatusLog(run.runLog) : [];
              setJob({ ...run, statusLog } as Job);
            }
          });
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return <LoadingScreen />;
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
        <div className="mx-auto max-w-6xl">
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
              <p className="mt-1 text-xs" style={{ color: "var(--text-muted)" }}>
                {formatDate(job.createdAt)}
                {job.config.model && <> · {job.config.model}</>}
                {job.paperCount != null && <> · {job.paperCount} papers read</>}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="relative mx-auto max-w-6xl px-6 py-8 pb-24">
        {/* TOC — fixed left */}
        {job.report && <TocPanel report={job.report} />}

        {/* Report — centred with room for the TOC panel */}
        <div className="mx-auto lg:ml-52">
          <ReportContent job={job} />
        </div>

        {/* Downloads panel — hidden for now
        <div className="hidden lg:block fixed top-24 right-5 z-20">
          <DownloadsPanel job={job} />
        </div>
        */}
      </div>
    </div>
  );
}


const LOADING_PHRASES = [
  "Pulling from the research stack…",
  "Cross-referencing the evidence base…",
  "Checking citations one more time…",
  "Synthesising findings across studies…",
  "Reading between the data points…",
  "Assembling your research brief…",
  "Good things take a moment to learn…",
  "Surfacing what the literature says…",
];

function LoadingScreen() {
  const [idx, setIdx] = useState(0);
  const [fade, setFade] = useState(true);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    timerRef.current = setInterval(() => {
      setFade(false);
      setTimeout(() => {
        setIdx((i) => (i + 1) % LOADING_PHRASES.length);
        setFade(true);
      }, 300);
    }, 2800);
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, []);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-6" style={{ background: "var(--bg)" }}>
      <div className="h-8 w-8 rounded-full border-2 border-zinc-200 border-t-zinc-400 animate-spin" />
      <div className="text-center" style={{ minHeight: "2rem" }}>
        <p
          className="text-sm font-medium transition-opacity duration-300"
          style={{
            color: "var(--text-secondary)",
            opacity: fade ? 1 : 0,
          }}
        >
          {LOADING_PHRASES[idx]}
        </p>
      </div>
    </div>
  );
}

function TocPanel({ report }: { report: string }) {
  const toc = useMemo(() => parseToc(report), [report]);
  if (toc.length === 0) return null;

  return (
    <div className="hidden lg:block fixed top-24 left-5 z-20 w-44">
      <div
        className="rounded-xl p-3"
        style={{ border: "1px solid var(--border)", background: "var(--surface)", boxShadow: "0 2px 16px rgba(0,0,0,0.07)" }}
      >
        <p className="text-[10px] font-semibold uppercase tracking-wider mb-2.5" style={{ color: "var(--text-muted)" }}>
          Contents
        </p>
        <nav className="space-y-0.5 max-h-[70vh] overflow-y-auto">
          {toc.map((item) => (
            <a
              key={item.slug}
              href={`#${item.slug}`}
              className="block rounded px-1.5 py-1 text-[11px] leading-snug transition-colors"
              style={{
                color: "var(--text-muted)",
                paddingLeft: item.level === 3 ? "14px" : "6px",
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.background = "var(--surface-alt)";
                (e.currentTarget as HTMLElement).style.color = "var(--text-primary)";
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.background = "transparent";
                (e.currentTarget as HTMLElement).style.color = "var(--text-muted)";
              }}
            >
              {item.text}
            </a>
          ))}
        </nav>
      </div>
    </div>
  );
}


function ReportContent({ job }: { job: Job }) {
  if (job.status === "running" && !job.report) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <div className="mb-3 h-6 w-6 rounded-full border-2 border-zinc-200 border-t-zinc-400 animate-spin" />
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>Research in progress…</p>
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
          h1: ({ children }) => <h1 className="mt-8 mb-3 text-2xl font-semibold" style={{ color: "var(--text-primary)" }}>{children}</h1>,
          h2: ({ children }) => {
            const text = String(children);
            const slug = slugify(text);
            return <h2 id={slug} className="mt-6 mb-2 text-xl font-semibold" style={{ color: "var(--text-primary)" }}>{children}</h2>;
          },
          h3: ({ children }) => {
            const text = String(children);
            const slug = slugify(text);
            return <h3 id={slug} className="mt-5 mb-2 text-base font-semibold" style={{ color: "var(--text-primary)" }}>{children}</h3>;
          },
          p: ({ children }) => <p className="mb-4 text-base leading-relaxed" style={{ color: "var(--text-secondary)" }}>{children}</p>,
          ul: ({ children }) => <ul className="mb-4 space-y-1.5 pl-5">{children}</ul>,
          ol: ({ children }) => <ol className="mb-4 space-y-1.5 pl-5 list-decimal">{children}</ol>,
          li: ({ children }) => <li className="text-base leading-relaxed list-disc" style={{ color: "var(--text-secondary)" }}>{children}</li>,
          a: ({ href, children }) => {
            const isAnchor = href?.startsWith("#");
            return (
              <a
                href={href}
                target={isAnchor ? undefined : "_blank"}
                rel={isAnchor ? undefined : "noopener noreferrer"}
                className="underline underline-offset-2"
                style={{ color: "var(--indigo)" }}
              >
                {children}
              </a>
            );
          },
          strong: ({ children }) => <strong style={{ color: "var(--text-primary)", fontWeight: 600 }}>{children}</strong>,
          blockquote: ({ children }) => (
            <blockquote className="border-l-2 pl-4 italic my-4" style={{ borderColor: "var(--border)", color: "var(--text-muted)" }}>{children}</blockquote>
          ),
          hr: () => <hr style={{ borderColor: "var(--border)", margin: "24px 0" }} />,
          table: ({ children }) => (
            <div className="overflow-x-auto my-6">
              <table className="w-full text-sm border-collapse">{children}</table>
            </div>
          ),
          th: ({ children }) => <th className="px-3 py-2 text-left font-semibold" style={{ borderBottom: "1px solid var(--border)", color: "var(--text-primary)" }}>{children}</th>,
          td: ({ children }) => {
            // Tag the first column of bibliography rows so [N] links can jump here
            const text = String(children).trim();
            const isRefNum = /^\d+$/.test(text);
            return (
              <td
                id={isRefNum ? `ref-${text}` : undefined}
                className="px-3 py-2"
                style={{ borderBottom: "1px solid var(--border-subtle)", color: "var(--text-secondary)" }}
              >
                {children}
              </td>
            );
          },
        }}
      >
        {linkifyCitations(job.report)}
      </ReactMarkdown>
    </div>
  );
}


function DownloadsPanel({ job }: { job: Job }) {
  const [open, setOpen] = useState(true);
  const slug = job.query.slice(0, 40).replace(/[^a-z0-9]+/gi, "_").toLowerCase();

  // For local pipeline runs (UUID-format id), download actual files from disk
  const isLocalRun = /^[0-9a-f-]{36}$/.test(job.id);

  const downloadFromDisk = (fileType: string, filename: string) => {
    const a = document.createElement("a");
    a.href = `/api/download/${job.id}?file=${fileType}`;
    a.download = `${slug}_${filename}`;
    a.click();
  };

  const downloadText = (content: string, filename: string, mime = "text/plain") => {
    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  type ExportEntry = {
    label: string;
    ext: string;
    icon: React.ComponentType<{ size?: number; style?: React.CSSProperties }>;
    disabled: boolean;
    onClick: () => void;
  };

  const exports: ExportEntry[] = [
    {
      label: "Final Report",
      ext: ".md",
      icon: FileText,
      disabled: !job.report,
      onClick: () => {
        if (isLocalRun) { downloadFromDisk("report", "report.md"); return; }
        if (!job.report) return;
        downloadText(job.report, `${slug}_report.md`, "text/markdown");
      },
    },
    {
      label: "QA Report",
      ext: ".md",
      icon: ClipboardCheck,
      disabled: !job.qaReport,
      onClick: () => {
        if (isLocalRun) { downloadFromDisk("qa", "qa.md"); return; }
        if (!job.qaReport) return;
        downloadText(job.qaReport, `${slug}_qa.md`, "text/markdown");
      },
    },
    {
      label: "Run Log",
      ext: ".log",
      icon: ScrollText,
      disabled: !(job.statusLog && job.statusLog.length > 0),
      onClick: () => {
        if (isLocalRun) { downloadFromDisk("log", "run.log"); return; }
        if (!job.statusLog?.length) return;
        const lines = job.statusLog.map((s) => {
          const t = `+${(s.timestamp / 1000).toFixed(1)}s`;
          return `[${t.padStart(8)}] ${s.text}`;
        });
        lines.unshift(`Query: ${job.query}`, `Date: ${new Date(job.createdAt).toISOString()}`, "");
        downloadText(lines.join("\n"), `${slug}_run.log`);
      },
    },
    {
      label: "State Snapshot",
      ext: ".json",
      icon: Database,
      disabled: !job.report && !job.sources?.length,
      onClick: () => {
        if (isLocalRun) { downloadFromDisk("snapshot", "snapshot.json"); return; }
        const snapshot = {
          id: job.id,
          query: job.query,
          config: job.config,
          status: job.status,
          createdAt: job.createdAt,
          completedAt: job.completedAt,
          paperCount: job.paperCount,
          toolCalls: job.toolCalls,
          sourcesCount: job.sources?.length ?? 0,
          sources: job.sources ?? [],
        };
        downloadText(JSON.stringify(snapshot, null, 2), `${slug}_snapshot.json`, "application/json");
      },
    },
  ];

  return (
    <div
      className="rounded-xl w-44"
      style={{ border: "1px solid var(--border)", background: "var(--surface)", boxShadow: "0 2px 16px rgba(0,0,0,0.07)" }}
    >
      {/* Header — toggle */}
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl"
        style={{ color: "var(--text-muted)" }}
        onMouseEnter={(e) => (e.currentTarget.style.background = "var(--surface-alt)")}
        onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
      >
        <div className="flex items-center gap-1.5">
          <Download size={11} />
          <span className="text-[10px] font-semibold uppercase tracking-wider">Downloads</span>
        </div>
        <ChevronDown
          size={11}
          style={{ transform: open ? "rotate(180deg)" : "rotate(0deg)", transition: "transform 150ms" }}
        />
      </button>

      {open && (
        <div className="px-2 pb-2 space-y-1">
          {exports.map(({ label, ext, icon: Icon, disabled, onClick }) => (
            <button
              key={label}
              onClick={onClick}
              disabled={disabled}
              className="w-full flex items-center gap-2 rounded-lg px-2 py-2 text-left transition-colors disabled:opacity-30"
              style={{ background: "transparent" }}
              onMouseEnter={(e) => { if (!disabled) (e.currentTarget as HTMLElement).style.background = "var(--surface-alt)"; }}
              onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = "transparent"; }}
            >
              <Icon size={12} style={{ color: "var(--text-muted)", flexShrink: 0 }} />
              <div className="flex-1 min-w-0">
                <p className="text-[11px] font-medium leading-tight" style={{ color: "var(--text-primary)" }}>{label}</p>
                <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>{ext}</p>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
