"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { createContext, useContext, useEffect, useState } from "react";
import { Bundle, getBundle } from "@/lib/data";
type Context = {
  bundle: Bundle | null;
  source: string;
  error: string;
  retry: () => void;
};
const DataContext = createContext<Context>({
  bundle: null,
  source: "loading",
  error: "",
  retry: () => {},
});
export const useBundle = () => useContext(DataContext);
export function Icon({ name, size = 18 }: { name: string; size?: number }) {
  const paths: Record<string, React.ReactNode> = {
    grid: (
      <>
        <rect x="3" y="3" width="7" height="7" rx="1" />
        <rect x="14" y="3" width="7" height="7" rx="1" />
        <rect x="3" y="14" width="7" height="7" rx="1" />
        <rect x="14" y="14" width="7" height="7" rx="1" />
      </>
    ),
    pulse: <path d="M2 12h5l3-8 4 16 3-8h5" />,
    sliders: (
      <>
        <path d="M4 6h16M4 12h16M4 18h16" />
        <circle cx="9" cy="6" r="2" />
        <circle cx="15" cy="12" r="2" />
        <circle cx="7" cy="18" r="2" />
      </>
    ),
    branch: (
      <>
        <circle cx="6" cy="5" r="2" />
        <circle cx="18" cy="5" r="2" />
        <circle cx="6" cy="19" r="2" />
        <path d="M6 7v10M18 7v1a7 7 0 0 1-7 7H6" />
      </>
    ),
    arrow: <path d="M5 12h14m-5-5 5 5-5 5" />,
    upload: (
      <>
        <path d="M12 16V3m-5 5 5-5 5 5M4 16v5h16v-5" />
      </>
    ),
    sun: (
      <>
        <circle cx="12" cy="12" r="4" />
        <path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1 1m12 12 1 1M5 19l1-1M18 6l1-1" />
      </>
    ),
    check: <path d="m5 12 4 4L19 6" />,
    download: (
      <>
        <path d="M12 3v13m-5-5 5 5 5-5M4 17v4h16v-4" />
      </>
    ),
    search: (
      <>
        <circle cx="10" cy="10" r="6" />
        <path d="m15 15 6 6" />
      </>
    ),
  };
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name] ?? paths.grid}
    </svg>
  );
}
export function Shell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [bundle, setBundle] = useState<Bundle | null>(null);
  const [source, setSource] = useState("loading");
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);
  const [dark, setDark] = useState(true);
  useEffect(() => {
    const saved = localStorage.getItem("readout-theme");
    setDark(saved !== "light");
    document.documentElement.dataset.theme = saved ?? "dark";
  }, []);
  useEffect(() => {
    const controller = new AbortController();
    setError("");
    getBundle(controller.signal)
      .then(({ bundle, source }) => {
        setBundle(bundle);
        setSource(source);
      })
      .catch((e: unknown) => {
        if (!controller.signal.aborted)
          setError(
            e instanceof Error ? e.message : "Results could not be loaded.",
          );
      });
    return () => controller.abort();
  }, [attempt]);
  const nav = [
    { href: "/experiments", name: "Experiments", icon: "grid" },
    { href: "/calibration", name: "Calibration", icon: "pulse" },
    { href: "/design", name: "Design", icon: "sliders" },
    { href: "/assign", name: "Assignment", icon: "branch" },
  ];
  return (
    <DataContext.Provider
      value={{ bundle, source, error, retry: () => setAttempt(attempt + 1) }}
    >
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <aside className="sidebar">
        <Link className="brand" href="/experiments" aria-label="readout home">
          <span className="brand-glyph">
            <i />
            <i />
            <i />
          </span>
          readout<span className="brand-dot">.</span>
        </Link>
        <div className="workspace">
          <span className="workspace-avatar">R</span>
          <div>
            <strong>Research workspace</strong>
            <small>Experimentation platform</small>
          </div>
          <span className="workspace-caret">⌄</span>
        </div>
        <div className="nav-label">WORKSPACE</div>
        <nav>
          {nav.map((n) => (
            <Link
              key={n.href}
              href={n.href}
              className={`nav-link ${pathname.startsWith(n.href) || (pathname === "/" && n.href === "/experiments") ? "active" : ""}`}
            >
              <Icon name={n.icon} />
              {n.name}
              {n.name === "Experiments" && bundle && (
                <span className="nav-count">{bundle.experiments.length}</span>
              )}
            </Link>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="method-note">
            <span className="mini-label">THE READOUT PRINCIPLE</span>
            <p>
              Health before metrics.
              <br />
              Evidence before decisions.
            </p>
            <Link href="/calibration">
              See how we validate <Icon name="arrow" size={14} />
            </Link>
          </div>
          <div className="sidebar-footer">
            <span className="version">readout / v0.1.0</span>
            <button
              className="icon-button"
              aria-label={
                dark ? "Switch to light theme" : "Switch to dark theme"
              }
              onClick={() => {
                const next = !dark;
                setDark(next);
                document.documentElement.dataset.theme = next
                  ? "dark"
                  : "light";
                localStorage.setItem("readout-theme", next ? "dark" : "light");
              }}
            >
              <Icon name="sun" />
            </button>
          </div>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div className="breadcrumbs">
            Workspace <span>/</span>{" "}
            <strong>
              {pathname.includes("calibration")
                ? "Calibration"
                : pathname.includes("design")
                  ? "Design calculator"
                  : pathname.includes("assign")
                    ? "Assignment"
                    : pathname.includes("upload")
                      ? "Upload experiment"
                      : "Experiments"}
            </strong>
          </div>
          <div className="topbar-right">
            <span className={`connection ${source === "live" ? "live" : ""}`}>
              <i />
              {source === "live"
                ? "Live API"
                : source === "committed"
                  ? "Published results"
                  : "Loading results"}
            </span>
            <span className="reviewer" title="Public research workspace">
              RO
            </span>
          </div>
        </header>
        <main id="main">{children}</main>
        <footer className="page-footer">
          <span>Built for decisions that stand up to review.</span>
          <span>Deterministic analysis · Reproducible evidence</span>
        </footer>
      </div>
    </DataContext.Provider>
  );
}
export function Badge({ value }: { value: unknown }) {
  const text =
    typeof value === "string" ? value.replaceAll("_", " ") : "unknown";
  const lower = text.toLowerCase();
  const type = /block|fail|no ship|do not ship/.test(lower)
    ? "block"
    : /warn|extend|inconclusive|provisional/.test(lower)
      ? "warn"
      : /pass|ship|complete|healthy/.test(lower)
        ? "pass"
        : "neutral";
  return (
    <span className={`badge ${type}`}>
      <span aria-hidden="true">
        {type === "pass"
          ? "✓"
          : type === "block"
            ? "⊘"
            : type === "warn"
              ? "△"
              : "◌"}
      </span>
      {text}
    </span>
  );
}
export function Source({ label, detail }: { label: string; detail?: string }) {
  return (
    <span className="source" title={detail}>
      <span className="source-mark">
        {label.toLowerCase().includes("sim") ? "◈" : "◇"}
      </span>
      {label.replaceAll("_", " ")}
    </span>
  );
}
export function Empty({ children }: { children: React.ReactNode }) {
  return (
    <div className="empty">
      <span className="empty-symbol">∅</span>
      <p>{children}</p>
    </div>
  );
}
export function Loading() {
  const { error, retry } = useBundle();
  if (error)
    return (
      <div className="error-panel">
        <h2>Results unavailable</h2>
        <p>{error}</p>
        <button className="button" onClick={retry}>
          Try again
        </button>
      </div>
    );
  return (
    <div
      className="loading"
      aria-label="Loading experiment results"
      aria-busy="true"
    >
      <div className="skeleton sk-title" />
      <div className="skeleton sk-subtitle" />
      <div className="stats-grid">
        {[0, 1, 2, 3].map((x) => (
          <div className="skeleton sk-card" key={x} />
        ))}
      </div>
      <div className="skeleton sk-chart" />
    </div>
  );
}
export function PageHead({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow: string;
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="page-head">
      <div>
        <div className="eyebrow">
          <span />
          {eyebrow}
        </div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      {action && <div className="page-action">{action}</div>}
    </div>
  );
}
