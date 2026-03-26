"use client";
import { useState, useRef, KeyboardEvent } from "react";
import { ResearchConfig, MODEL_OPTIONS, DEPTH_OPTIONS, TASK_TYPE_OPTIONS, ResearchDepth, TaskType } from "@/lib/types";
import { ArrowUp, ChevronDown } from "lucide-react";

interface QueryBarProps {
  onSubmit: (query: string, config: ResearchConfig) => void;
  isRunning: boolean;
}

const DEFAULT_CONFIG: ResearchConfig = {
  taskType: "research-basic",
  model: "gpt-5.2",
  depth: "standard",
  maxSources: 30,
  keywords: "",
  agentVersion: "v2",
};

export default function QueryBar({ onSubmit, isRunning }: QueryBarProps) {
  const [query, setQuery] = useState("");
  const [config, setConfig] = useState<ResearchConfig>(DEFAULT_CONFIG);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    if (!query.trim() || isRunning) return;
    onSubmit(query.trim(), config);
    setQuery("");
    setConfig({ ...config, keywords: "" });
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInput = () => {
    if (!textareaRef.current) return;
    textareaRef.current.style.height = "auto";
    textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
  };

  return (
    <div className="w-full">
      {/* Main input card */}
      <div
        className="w-full rounded-2xl transition-shadow duration-200"
        style={{
          background: "var(--surface)",
          border: "1px solid var(--border)",
          boxShadow: "0 2px 12px rgba(0,0,0,0.06)",
        }}
      >
        {/* Task type + query row */}
        <div className="flex items-start gap-0">
          {/* Task type selector */}
          <div className="relative flex-shrink-0">
            <select
              value={config.taskType}
              onChange={(e) => setConfig({ ...config, taskType: e.target.value as TaskType })}
              className="h-full appearance-none rounded-l-2xl border-r px-4 py-4 pr-8 text-sm font-medium cursor-pointer focus:outline-none"
              style={{
                background: "var(--surface-alt)",
                borderColor: "var(--border)",
                color: config.taskType ? "var(--text-primary)" : "var(--text-muted)",
                minWidth: "160px",
              }}
            >
              <option value="">Task type</option>
              {TASK_TYPE_OPTIONS.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
            <ChevronDown
              size={14}
              className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2"
              style={{ color: "var(--text-muted)" }}
            />
          </div>

          {/* Query textarea */}
          <div className="relative flex-1">
            <textarea
              ref={textareaRef}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              onInput={handleInput}
              placeholder="Ask a research question..."
              rows={1}
              disabled={isRunning}
              className="w-full resize-none bg-transparent px-4 py-4 text-sm leading-relaxed focus:outline-none disabled:opacity-50"
              style={{ color: "var(--text-primary)", minHeight: "54px", maxHeight: "180px" }}
            />
          </div>

          {/* Submit button */}
          <div className="flex-shrink-0 p-3 flex items-end pb-3">
            <button
              onClick={handleSubmit}
              disabled={!query.trim() || isRunning}
              className="flex h-8 w-8 items-center justify-center rounded-lg transition-all duration-150 disabled:opacity-30"
              style={{ background: "var(--accent)", color: "#fff" }}
            >
              {isRunning ? (
                <span className="h-3 w-3 rounded-full border-2 border-white/40 border-t-white animate-spin" />
              ) : (
                <ArrowUp size={15} strokeWidth={2.5} />
              )}
            </button>
          </div>
        </div>

        {/* Keywords row */}
        <div
          className="border-t px-4 py-2.5"
          style={{ borderColor: "var(--border-subtle)" }}
        >
          <div className="flex items-center gap-2">
            <span className="flex-shrink-0 text-xs" style={{ color: "var(--text-muted)" }}>
              Keywords
            </span>
            <input
              type="text"
              value={config.keywords ?? ""}
              onChange={(e) => setConfig({ ...config, keywords: e.target.value })}
              placeholder="Optional — comma-separated terms to guide search (e.g. RCT, K-12, math tutoring)"
              disabled={isRunning}
              className="flex-1 bg-transparent text-xs focus:outline-none disabled:opacity-50"
              style={{ color: "var(--text-secondary)" }}
            />
          </div>
        </div>

        {/* Filters row */}
        <div
          className="flex flex-wrap items-center gap-2 border-t px-4 py-2.5"
          style={{ borderColor: "var(--border-subtle)" }}
        >
          {/* Model */}
          <FilterSelect
            value={config.model}
            onChange={(v) => setConfig({ ...config, model: v })}
            options={MODEL_OPTIONS}
            label="Model"
          />

          <Divider />

          {/* Search Rigor */}
          <FilterSelect
            value={config.depth}
            onChange={(v) => setConfig({ ...config, depth: v as ResearchDepth })}
            options={DEPTH_OPTIONS.map((d) => ({ value: d.value, label: d.label }))}
            label="Search Rigor"
          />

          <Divider />

          {/* Top-K */}
          <div className="flex items-center gap-1.5">
            <span className="text-xs" style={{ color: "var(--text-muted)" }}>Top-K</span>
            <select
              value={config.maxSources}
              onChange={(e) => setConfig({ ...config, maxSources: Number(e.target.value) })}
              className="appearance-none rounded-md px-2 py-1 text-xs focus:outline-none"
              style={{ background: "transparent", color: "var(--text-secondary)" }}
            >
              {[10, 20, 30, 50].map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {isRunning && (
        <p className="mt-2 text-center text-xs" style={{ color: "var(--text-muted)" }}>
          Research in progress — you can browse past sessions below while this runs
        </p>
      )}
    </div>
  );
}

function FilterSelect({
  value, onChange, options, label,
}: {
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
  label: string;
}) {
  return (
    <div className="flex items-center gap-1.5">
      <span className="text-xs" style={{ color: "var(--text-muted)" }}>{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="appearance-none rounded-md px-2 py-1 text-xs font-medium focus:outline-none cursor-pointer"
        style={{ background: "transparent", color: "var(--text-secondary)" }}
      >
        {options.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>
    </div>
  );
}

function Divider() {
  return <span className="h-3 w-px" style={{ background: "var(--border)" }} />;
}
