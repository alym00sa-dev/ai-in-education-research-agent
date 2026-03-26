"use client";
import { AppMode } from "@/lib/types";

interface NavbarProps {
  mode: AppMode;
  onModeChange: (mode: AppMode) => void;
}

export default function Navbar({ mode, onModeChange }: NavbarProps) {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/80 backdrop-blur-sm" style={{ borderColor: "var(--border)" }}>
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-6">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold tracking-tight" style={{ color: "var(--text-primary)" }}>
            EduAgent
          </span>
          <span className="rounded-full px-2 py-0.5 text-[10px] font-medium" style={{ background: "var(--surface-alt)", color: "var(--text-muted)" }}>
            beta
          </span>
        </div>

        {/* Mode switcher */}
        <div className="flex items-center rounded-lg p-1" style={{ background: "var(--surface-alt)", border: "1px solid var(--border)" }}>
          {(["research", "canvas"] as AppMode[]).map((m) => (
            <button
              key={m}
              onClick={() => onModeChange(m)}
              className="rounded-md px-4 py-1.5 text-sm font-medium transition-all duration-150"
              style={{
                background: mode === m ? "var(--surface)" : "transparent",
                color: mode === m ? "var(--text-primary)" : "var(--text-muted)",
                boxShadow: mode === m ? "0 1px 3px rgba(0,0,0,0.08)" : "none",
              }}
            >
              {m === "research" ? "Research" : "Strategic Canvas"}
            </button>
          ))}
        </div>

        {/* Right — reserved for future actions */}
        <div className="w-7" />
      </div>
    </header>
  );
}
