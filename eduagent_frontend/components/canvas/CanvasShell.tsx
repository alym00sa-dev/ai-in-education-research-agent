"use client";

export default function CanvasShell() {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      <div
        className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl"
        style={{ background: "var(--surface-alt)", border: "1px solid var(--border)" }}
      >
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          style={{ color: "var(--text-muted)" }}
        >
          <rect x="3" y="3" width="18" height="18" rx="2" />
          <path d="M3 9h18M9 21V9" />
        </svg>
      </div>
      <h2
        className="text-base font-medium"
        style={{ color: "var(--text-primary)" }}
      >
        Strategic Canvas
      </h2>
      <p
        className="mt-2 max-w-sm text-sm leading-relaxed"
        style={{ color: "var(--text-muted)" }}
      >
        Turn a broad education challenge into a structured research strategy.
        Full experience coming soon.
      </p>
    </div>
  );
}
