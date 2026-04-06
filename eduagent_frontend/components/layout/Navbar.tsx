"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navbar() {
  const pathname = usePathname();
  return (
    <header
      className="sticky top-0 z-50 w-full border-b bg-white/80 backdrop-blur-sm"
      style={{ borderColor: "var(--border)" }}
    >
      <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-6">
        {/* Logo */}
        <span
          className="text-sm font-semibold tracking-tight"
          style={{ color: "var(--text-primary)" }}
        >
          EduAgent
        </span>

        {/* Nav links */}
        <div className="flex items-center gap-1">
          <NavLink href="/agent" active={!!pathname?.startsWith("/agent")}>
            Agent
          </NavLink>
        </div>
      </div>
    </header>
  );
}

function NavLink({
  href,
  active,
  children,
}: {
  href: string;
  active: boolean;
  children: React.ReactNode;
}) {
  return (
    <Link
      href={href}
      className="rounded-md px-3 py-1.5 text-sm font-medium transition-all duration-150"
      style={{
        background: active ? "var(--surface-alt)" : "transparent",
        color: active ? "var(--text-primary)" : "var(--text-muted)",
      }}
    >
      {children}
    </Link>
  );
}
