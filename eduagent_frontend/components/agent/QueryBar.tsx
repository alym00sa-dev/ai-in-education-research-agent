"use client";
import { useState, useRef, KeyboardEvent } from "react";
import { ResearchConfig } from "@/lib/types";
import { ArrowUp, Info } from "lucide-react";

interface QueryBarProps {
  onSubmit: (query: string, config: ResearchConfig) => void;
  isRunning: boolean;
}

type Speed = "fast" | "slow";

const SPEED_OPTIONS: { value: Speed; label: string; model: string; tooltip: string }[] = [
  { value: "fast", label: "Fast", model: "gpt-5.4-mini", tooltip: "GPT 5.4 Mini — ~20 min" },
  { value: "slow", label: "Slow", model: "gpt-5.4",      tooltip: "GPT 5.4 — ~40 min"      },
];

const DEFAULT_SPEED: Speed = "fast";

const DEFAULT_CONFIG: ResearchConfig = {
  taskType: "research-basic",
  model: SPEED_OPTIONS.find((s) => s.value === DEFAULT_SPEED)!.model,
  depth: "standard",
  maxSources: 30,
  keywords: "",
  agentVersion: "v2",
};

export default function QueryBar({ onSubmit, isRunning }: QueryBarProps) {
  const [query, setQuery] = useState("");
  const [config, setConfig] = useState<ResearchConfig>(DEFAULT_CONFIG);
  const [speed, setSpeed] = useState<Speed>(DEFAULT_SPEED);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSpeedChange = (s: Speed) => {
    setSpeed(s);
    setConfig((c) => ({
      ...c,
      model: SPEED_OPTIONS.find((o) => o.value === s)!.model,
    }));
  };

  const handleSubmit = () => {
    if (!query.trim() || isRunning) return;
    onSubmit(query.trim(), config);
    setQuery("");
    setConfig((c) => ({ ...c, keywords: "" }));
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
    textareaRef.current.style.height = `${Math.min(
      textareaRef.current.scrollHeight,
      200
    )}px`;
  };

  return (
    <div className="w-full">
      <div
        className="w-full rounded-2xl transition-shadow duration-200"
        style={{
          background: "var(--surface)",
          border: "1px solid var(--border)",
          boxShadow: "0 2px 12px rgba(0,0,0,0.06)",
        }}
      >
        {/* Query row */}
        <div className="flex items-start">
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
              className="w-full resize-none bg-transparent px-5 py-4 text-sm leading-relaxed focus:outline-none disabled:opacity-50"
              style={{
                color: "var(--text-primary)",
                minHeight: "56px",
                maxHeight: "200px",
              }}
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

        {/* Keywords + speed row */}
        <div
          className="flex items-center gap-3 border-t px-5 py-2.5"
          style={{ borderColor: "var(--border-subtle)" }}
        >
          {/* Keywords label */}
          <span className="flex-shrink-0 text-xs" style={{ color: "var(--text-muted)" }}>
            Keywords
          </span>

          {/* Keywords input */}
          <input
            type="text"
            value={config.keywords ?? ""}
            onChange={(e) => setConfig({ ...config, keywords: e.target.value })}
            placeholder="Optional — comma-separated terms to guide search (e.g. RCT, K-12, math tutoring)"
            disabled={isRunning}
            className="flex-1 bg-transparent text-xs focus:outline-none disabled:opacity-50"
            style={{ color: "var(--text-secondary)" }}
          />

          {/* Divider */}
          <span className="h-3 w-px flex-shrink-0" style={{ background: "var(--border)" }} />

          {/* Speed toggle with tooltip */}
          <div className="relative flex items-center gap-1.5">
            <div
              className="flex items-center gap-1 rounded-lg p-0.5"
              style={{ background: "var(--surface-alt)", border: "1px solid var(--border-subtle)" }}
            >
              {SPEED_OPTIONS.map((o) => (
                <button
                  key={o.value}
                  onClick={() => handleSpeedChange(o.value)}
                  disabled={isRunning}
                  className="rounded-md px-3 py-1 text-xs font-medium transition-all duration-150 disabled:opacity-50"
                  style={{
                    background: speed === o.value ? "var(--surface)" : "transparent",
                    color: speed === o.value ? "var(--text-primary)" : "var(--text-muted)",
                    boxShadow: speed === o.value ? "0 1px 2px rgba(0,0,0,0.07)" : "none",
                  }}
                >
                  {o.label}
                </button>
              ))}
            </div>

            {/* Info icon with tooltip */}
            <div className="group relative flex items-center">
              <Info size={12} style={{ color: "var(--text-muted)", cursor: "default" }} />
              <div
                className="pointer-events-none absolute bottom-full right-0 mb-2 hidden group-hover:block z-50"
              >
                <div
                  className="rounded-lg px-3 py-2 text-xs whitespace-nowrap shadow-lg"
                  style={{
                    background: "var(--surface)",
                    border: "1px solid var(--border)",
                    color: "var(--text-secondary)",
                  }}
                >
                  <div className="font-medium mb-1" style={{ color: "var(--text-primary)" }}>Model</div>
                  <div>Fast — GPT 5.4 Mini, ~20 min</div>
                  <div>Slow — GPT 5.4, ~40 min</div>
                  <div className="mt-1" style={{ color: "var(--text-muted)" }}>Report always uses GPT 5.4</div>
                </div>
              </div>
            </div>
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
