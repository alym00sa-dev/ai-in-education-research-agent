"use client";
import { useState, useEffect, useRef } from "react";
import { Job } from "@/lib/types";
import { X } from "lucide-react";

interface ReportDrawerProps {
  job: Job | null;
  onClose: () => void;
  onCancel: () => void;
}

function useElapsed(startMs: number | undefined): string {
  const [elapsed, setElapsed] = useState(0);
  useEffect(() => {
    if (!startMs) return;
    const tick = () => setElapsed(Math.floor((Date.now() - startMs) / 1000));
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [startMs]);
  const m = Math.floor(elapsed / 60);
  const s = elapsed % 60;
  return m > 0 ? `${m}m ${s}s` : `${s}s`;
}


export default function ReportDrawer({ job, onClose, onCancel }: ReportDrawerProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const elapsed = useElapsed(job?.createdAt);
  const logLines = (job?.statusLog ?? []).map((s) => s.text);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logLines.length]);

  const isOpen = !!job;

  return (
    <>
      {isOpen && (
        <div className="fixed inset-0 z-40 bg-black/20" onClick={onClose} />
      )}

      <div
        className="fixed right-0 top-0 z-50 h-full flex flex-col transition-transform duration-300 ease-out"
        style={{
          width: "min(520px, 100vw)",
          background: "#0d1117",
          borderLeft: "1px solid #21262d",
          boxShadow: "-8px 0 40px rgba(0,0,0,0.3)",
          transform: isOpen ? "translateX(0)" : "translateX(100%)",
        }}
      >
        {job && (
          <>
            {/* Header */}
            <div className="flex-shrink-0 border-b px-5 py-4" style={{ borderColor: "#21262d" }}>
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium leading-snug line-clamp-2" style={{ color: "#e6edf3" }}>
                    {job.query}
                  </p>
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-xs tabular-nums font-mono" style={{ color: "#7d8590" }}>
                      {elapsed}
                    </span>
                    <span style={{ color: "#30363d" }}>·</span>
                    <span className="text-xs font-mono" style={{ color: "#7d8590" }}>running</span>
                  </div>
                </div>

                <div className="flex flex-shrink-0 items-center gap-1.5 pt-0.5">
                  <button
                    onClick={onCancel}
                    className="flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs font-medium font-mono transition-all"
                    style={{ background: "#161b22", color: "#8b949e", border: "1px solid #30363d" }}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLElement).style.borderColor = "#f87171";
                      (e.currentTarget as HTMLElement).style.color = "#f87171";
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLElement).style.borderColor = "#30363d";
                      (e.currentTarget as HTMLElement).style.color = "#8b949e";
                    }}
                  >
                    stop
                  </button>
                  <button
                    onClick={onClose}
                    className="rounded-md p-1.5 transition-colors"
                    style={{ color: "#484f58" }}
                    onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = "#8b949e"; }}
                    onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = "#484f58"; }}
                  >
                    <X size={14} />
                  </button>
                </div>
              </div>
            </div>

            {/* Terminal log — raw run.log lines */}
            <div className="flex-1 overflow-y-auto px-5 py-4" style={{ background: "#0d1117" }}>
              <div className="font-mono text-xs leading-relaxed space-y-0.5">
                {logLines.length === 0 ? (
                  <div style={{ color: "#484f58" }}>waiting for pipeline...</div>
                ) : (
                  logLines.map((line, i) => (
                    <div key={i} style={{ color: line.includes("Error") || line.includes("Warning") ? "#f87171" : "#e6edf3", whiteSpace: "pre-wrap", wordBreak: "break-all" }}>
                      {line}
                    </div>
                  ))
                )}
                <div style={{ color: "#484f58" }}>▌</div>
              </div>
              <div ref={bottomRef} />
            </div>
          </>
        )}
      </div>
    </>
  );
}

