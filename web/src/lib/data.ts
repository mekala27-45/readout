export type Row = Record<string, unknown>;
export type Manifest = {
  experiment: Row;
  run?: Row;
  health?: Row[];
  decision?: Row;
};
export type Bundle = {
  generated_at?: string;
  experiments: Manifest[];
  registry?: Row[];
  calibration?: Row;
  pricepoint?: Row;
  assignment?: Row;
};
export const BASE = process.env.NEXT_PUBLIC_BASE_PATH ?? "";
export const API = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "").replace(
  /\/$/,
  "",
);
export const rec = (v: unknown): Row =>
  v && typeof v === "object" && !Array.isArray(v) ? (v as Row) : {};
export const rows = (v: unknown): Row[] => (Array.isArray(v) ? v.map(rec) : []);
export const num = (v: unknown, fallback = NaN): number =>
  typeof v === "number" && Number.isFinite(v) ? v : fallback;
export const str = (v: unknown, fallback = "Not recorded"): string =>
  typeof v === "string" ? v : fallback;
export const fmt = (v: unknown, digits = 3): string =>
  Number.isFinite(num(v))
    ? num(v).toLocaleString("en-US", { maximumFractionDigits: digits })
    : "Unavailable";
export const pct = (v: unknown, digits = 1): string =>
  Number.isFinite(num(v))
    ? `${(num(v) * 100).toFixed(digits)}%`
    : "Unavailable";
export const interval = (r: Row, percent = false): string => {
  const f = percent ? pct : fmt;
  return `${f(r.estimate ?? r.rate)} [${f(r.ci_low ?? r.low)}, ${f(r.ci_high ?? r.high)}]`;
};
export const status = (v: unknown): string =>
  str(v, "unknown").toLowerCase().replaceAll("_", " ");
export const result = (m: Manifest): Row => rec(m.run?.results);
export const design = (m: Manifest): Row =>
  rec(m.experiment.registered_design ?? m.experiment.design);
export const healthStatus = (m: Manifest): string =>
  status(
    m.health?.find((h) => str(h.check ?? h.kind, "").includes("srm"))?.status ??
      m.health?.[0]?.status,
  );
export const blocked = (m: Manifest): boolean =>
  !m.health?.length ||
  m.health.some((h) =>
    ["block", "blocked", "fail"].includes(status(h.status)),
  ) ||
  status(m.decision?.decision) === "blocked";
export const sourceLabel = (m: Manifest): string =>
  m.experiment.source === "public"
    ? "Real public data"
    : str(m.experiment.source, "Source unavailable");
export const sourceDetail = (m: Manifest): string => {
  const d = rec(m.experiment.source_detail);
  if (typeof m.experiment.source_detail === "string")
    return m.experiment.source_detail;
  return (
    Object.entries(d)
      .filter(
        ([k, v]) =>
          [
            "scenario",
            "seed",
            "url",
            "dataset",
            "provenance",
            "source_url",
          ].includes(k) && ["string", "number"].includes(typeof v),
      )
      .map(([k, v]) => `${k}: ${String(v)}`)
      .join(" · ") || JSON.stringify(d)
  );
};
export async function getBundle(
  signal?: AbortSignal,
): Promise<{ bundle: Bundle; source: "live" | "committed" }> {
  if (API) {
    try {
      const response = await fetch(`${API}/api/bundle`, {
        signal: AbortSignal.any([
          AbortSignal.timeout(4500),
          ...(signal ? [signal] : []),
        ]),
      });
      if (response.ok) {
        const data = (await response.json()) as Bundle;
        if (Array.isArray(data.experiments))
          return { bundle: data, source: "live" };
      }
    } catch {
      /* The canonical artifact is the public offline source. */
    }
  }
  const response = await fetch(`${BASE}/results/bundle.json`, { signal });
  if (!response.ok)
    throw new Error(
      "The measured results bundle could not be loaded. Please retry.",
    );
  const bundle = (await response.json()) as Bundle;
  if (!Array.isArray(bundle.experiments))
    throw new Error("The result bundle is not valid.");
  return { bundle, source: "committed" };
}
export async function api(path: string, init?: RequestInit): Promise<Row> {
  if (!API)
    throw new Error(
      "The live API is not configured. The published results remain available.",
    );
  const response = await fetch(`${API}${path}`, {
    ...init,
    signal: AbortSignal.timeout(30000),
  });
  const body = (await response.json()) as Row;
  if (!response.ok)
    throw new Error(
      typeof body.detail === "string"
        ? body.detail
        : `Request failed (${response.status}).`,
    );
  return body;
}
export const experimentKeys = [
  "null",
  "at_mde",
  "srm_dropout",
  "guardrail_hit",
  "correlated_pre",
  "ratio_metric",
  "heterogeneous",
  "cookie_cats",
  "view",
];
