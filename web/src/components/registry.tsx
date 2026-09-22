"use client";
import Link from "next/link";
import { useMemo, useState } from "react";
import {
  blocked,
  design,
  fmt,
  healthStatus,
  interval,
  Manifest,
  num,
  rec,
  rows,
  result,
  sourceLabel,
  sourceDetail,
  experimentKeys,
  status,
  str,
} from "@/lib/data";
import { Badge, Icon, Loading, PageHead, Source, useBundle } from "./shell";
export function Registry() {
  const { bundle, source } = useBundle();
  const [filter, setFilter] = useState("all");
  const [query, setQuery] = useState("");
  const experiments = useMemo(
    () =>
      [
        ...(bundle?.experiments ?? []),
        ...(bundle?.registry ?? [])
          .filter(
            (r) => !bundle?.experiments.some((m) => m.experiment.key === r.key),
          )
          .map((experiment) => ({ experiment }) as Manifest),
      ].sort(
        (a, b) =>
          Number(Boolean(b.run) && blocked(b)) -
            Number(Boolean(a.run) && blocked(a)) ||
          ({ block: 0, warn: 1, pass: 2, unknown: 3 }[healthStatus(a)] ?? 3) -
            ({ block: 0, warn: 1, pass: 2, unknown: 3 }[healthStatus(b)] ??
              3) ||
          str(a.experiment.status).localeCompare(str(b.experiment.status)),
      ),
    [bundle],
  );
  if (!bundle) return <Loading />;
  const visible = experiments.filter(
    (m) =>
      (filter === "all" ||
        (filter === "blocked" && Boolean(m.run) && blocked(m)) ||
        (filter === "real" && sourceLabel(m).toLowerCase().includes("real")) ||
        (filter === "simulated" &&
          sourceLabel(m).toLowerCase().includes("sim"))) &&
      `${str(m.experiment.name)} ${str(m.experiment.key)}`
        .toLowerCase()
        .includes(query.toLowerCase()),
  );
  const blockedCount = experiments.filter((m) => m.run && blocked(m)).length;
  const featured =
    experiments.find((m) => m.experiment.key === "cookie_cats") ??
    experiments.find((m) => !blocked(m));
  const fp =
    featured && !blocked(featured) ? rec(result(featured).primary) : {};
  const miniExtent =
    Math.max(Math.abs(num(fp.ci_low, 0)), Math.abs(num(fp.ci_high, 0)), 0.001) *
    1.2;
  const miniScale = (v: unknown) => 50 + (num(v, 0) / miniExtent) * 50;
  return (
    <>
      <PageHead
        eyebrow="EXPERIMENTATION WORKBENCH"
        title="Every decision starts with evidence."
        description="Pre-register the question. Check the experiment. Read the result."
        action={
          <Link className="button primary" href="/upload">
            <Icon name="upload" size={16} />
            Upload experiment
          </Link>
        }
      />
      <div className="stats-grid">
        <Stat
          label="REGISTERED EXPERIMENTS"
          value={String(experiments.length)}
          foot="Designs and analysis records"
        />
        <Stat
          label="HEALTH GATE"
          value={String(blockedCount)}
          suffix="blocked"
          foot="Held before metric analysis"
          tone={blockedCount ? "warn" : ""}
        />
        <Stat
          label="MEASURED SCENARIOS"
          value={String(
            experiments.filter((m) =>
              sourceLabel(m).toLowerCase().includes("sim"),
            ).length,
          )}
          foot="Seeded data with known truth"
        />
        <Stat
          label="EVIDENCE SOURCE"
          value={source === "live" ? "Live" : "Published"}
          foot={
            bundle.generated_at
              ? `Derived ${new Date(bundle.generated_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}`
              : "Canonical results bundle"
          }
          small
        />
      </div>
      <div className="registry-intro">
        <div className="featured-panel">
          <div className="featured-copy">
            <div className="mini-label">
              THE FLAGSHIP READOUT{" "}
              <span className="subtle">
                /{" "}
                {featured
                  ? sourceLabel(featured).toUpperCase()
                  : "FULL PROTOCOL"}
              </span>
            </div>
            <h2>
              {featured
                ? str(featured.experiment.name)
                : "A complete experiment review"}
            </h2>
            <p>
              {featured?.experiment.key === "cookie_cats"
                ? "A familiar mobile game experiment, reviewed from randomization health to a rule-based decision."
                : "Trace a decision back to the health checks, pre-registered design, and measured uncertainty."}
            </p>
            {featured && (
              <Link
                className="text-link"
                href={`/experiments/${str(featured.experiment.key)}`}
              >
                Open the readout <Icon name="arrow" size={17} />
              </Link>
            )}
          </div>
          <div
            className="mini-forest"
            aria-label="Primary estimate with confidence interval"
          >
            <span className="mini-label">PRIMARY EFFECT</span>
            <strong>
              {Object.keys(fp).length ? interval(fp) : "Health first"}
            </strong>
            {Object.keys(fp).length > 0 && (
              <div
                className="mini-axis"
                title={`Primary effect ${interval(fp)}`}
                tabIndex={0}
              >
                <i className="axis-zero" style={{ left: "50%" }} />
                <i
                  className="axis-ci"
                  style={{
                    left: `${miniScale(fp.ci_low)}%`,
                    width: `${miniScale(fp.ci_high) - miniScale(fp.ci_low)}%`,
                  }}
                />
                <i
                  className="axis-dot"
                  style={{ left: `${miniScale(fp.estimate)}%` }}
                />
              </div>
            )}
            <span className="mini-forest-caption">
              {Object.keys(fp).length
                ? str(fp.name ?? fp.key, "Primary metric")
                : "Metrics appear only after recorded checks"}
            </span>
            {featured && (
              <Source
                label={sourceLabel(featured)}
                detail={str(featured.experiment.source_detail, "")}
              />
            )}
          </div>
        </div>
        <Link href="/calibration" className="calibration-teaser">
          <div className="teaser-icon">
            <Icon name="pulse" size={22} />
          </div>
          <h3>Who checks the test?</h3>
          <p>The platform measures its own error rates against known truth.</p>
          <span className="text-link">
            Explore calibration <Icon name="arrow" size={16} />
          </span>
        </Link>
      </div>
      <section className="registry-card">
        <div className="registry-toolbar">
          <div className="tabs" role="group" aria-label="Filter experiments">
            {[
              { k: "all", v: "All experiments" },
              { k: "blocked", v: "Needs attention" },
              { k: "simulated", v: "Simulated" },
              { k: "real", v: "Real data" },
            ].map((t) => (
              <button
                key={t.k}
                className={filter === t.k ? "selected" : ""}
                onClick={() => setFilter(t.k)}
              >
                {t.v}
                {t.k === "all" && <span>{experiments.length}</span>}
              </button>
            ))}
          </div>
          <label className="search-field">
            <Icon name="search" size={15} />
            <input
              aria-label="Search experiments"
              placeholder="Find an experiment..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <span>⌕</span>
          </label>
        </div>
        <div className="table-scroll">
          <table className="registry-table">
            <thead>
              <tr>
                <th>EXPERIMENT</th>
                <th>STATUS</th>
                <th>HEALTH</th>
                <th>SAMPLE / ARM</th>
                <th>DURATION</th>
                <th>DECISION</th>
                <th>
                  <span className="sr-only">Open</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {visible.map((m) => (
                <ExperimentRow key={str(m.experiment.key)} manifest={m} />
              ))}
            </tbody>
          </table>
        </div>
        {!visible.length && (
          <div className="empty">
            <p>No experiments match this filter.</p>
          </div>
        )}
        <div className="registry-bottom">
          <span>
            <i /> Health checks always precede metric analysis
          </span>
          <span>
            {visible.length} of {experiments.length} experiments
          </span>
        </div>
      </section>
      <div className="principles">
        <span>
          <b>01</b> Pre-registered design
        </span>
        <span>
          <b>02</b> Health gate
        </span>
        <span>
          <b>03</b> Calibrated inference
        </span>
        <span>
          <b>04</b> An explicit decision
        </span>
      </div>
    </>
  );
}
function Stat({
  label,
  value,
  suffix,
  foot,
  tone = "",
  small = false,
}: {
  label: string;
  value: string;
  suffix?: string;
  foot: string;
  tone?: string;
  small?: boolean;
}) {
  return (
    <div className={`stat-card ${tone}`}>
      <span className="mini-label">{label}</span>
      <div className={`stat-value ${small ? "word" : ""}`}>
        {value}
        {suffix && <span>{suffix}</span>}
      </div>
      <span className="stat-foot">{foot}</span>
    </div>
  );
}
function ExperimentRow({ manifest: m }: { manifest: Manifest }) {
  const d = design(m);
  const planned = num(d.planned_n_per_arm ?? d.n_per_arm);
  const primary = rec(result(m).primary);
  const achieved = Math.min(
    num(rec(m.run?.n_per_arm).control, num(primary.n_control)),
    num(rec(m.run?.n_per_arm).treatment, num(primary.n_treatment)),
  );
  const days = num(d.planned_days ?? d.days);
  const timeline = rows(rec(result(m).sequential).points);
  const observedDays = num(
    m.run?.days,
    timeline.length ? Math.max(...timeline.map((p) => num(p.day, 0))) : NaN,
  );
  const href = experimentKeys.includes(str(m.experiment.key))
    ? `/experiments/${str(m.experiment.key)}`
    : `/experiments/view?key=${encodeURIComponent(str(m.experiment.key))}`;
  const decisionLabel = str(
    m.decision?.decision ?? rec(result(m).decision).decision,
    "pending",
  );
  const provisional =
    !blocked(m) && Number.isFinite(achieved) && achieved < planned;
  return (
    <tr>
      <td>
        <Link className="experiment-name" href={href}>
          <span className={`experiment-icon ${blocked(m) ? "blocked" : ""}`}>
            <Icon name={blocked(m) ? "branch" : "pulse"} size={17} />
          </span>
          <span>
            <strong>
              {str(m.experiment.name, m.experiment.key as string)}
            </strong>
            <Source label={sourceLabel(m)} detail={sourceDetail(m)} />
          </span>
        </Link>
      </td>
      <td>
        <span className="state-dot" />
        {status(m.experiment.status)}
      </td>
      <td>
        <Badge value={healthStatus(m)} />
      </td>
      <td>
        <div className="sample-label">
          <strong>{fmt(achieved, 0)}</strong>
          <span>/ {fmt(planned, 0)}</span>
        </div>
        <div className="progress-track">
          <div
            style={{
              width: `${Number.isFinite(achieved / planned) ? Math.min(100, (100 * achieved) / planned) : 0}%`,
            }}
          />
        </div>
      </td>
      <td className="mono">
        {Number.isFinite(observedDays)
          ? `${fmt(observedDays, 0)} / ${fmt(days, 0)}d`
          : "Unavailable"}
      </td>
      <td>
        <Badge
          value={provisional ? `provisional ${decisionLabel}` : decisionLabel}
        />
      </td>
      <td>
        <Link
          className="row-arrow"
          href={href}
          aria-label={`Open ${str(m.experiment.name)}`}
        >
          <Icon name="arrow" size={17} />
        </Link>
      </td>
    </tr>
  );
}
