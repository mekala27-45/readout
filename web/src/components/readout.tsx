"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import {
  BASE,
  blocked,
  design,
  fmt,
  interval,
  Manifest,
  num,
  pct,
  rec,
  result,
  Row,
  rows,
  sourceDetail,
  sourceLabel,
  str,
} from "@/lib/data";
import { Badge, Empty, Icon, Loading, Source, useBundle } from "./shell";
import {
  ChartCard,
  DataTable,
  Forest,
  metricColumns,
  pValue,
  SeriesChart,
} from "./charts";
const sections = [
  "Health",
  "Design",
  "Primary metric",
  "Guardrails",
  "Variance",
  "Sequential",
  "Secondary and segments",
  "Decision",
  "Limitations",
  "Reproduce",
];
const anchor = (s: string) => s.toLowerCase().replaceAll(" ", "-");
export function Readout({ experimentKey }: { experimentKey: string }) {
  const { bundle } = useBundle();
  const [resolvedKey, setResolvedKey] = useState(experimentKey);
  useEffect(() => {
    if (experimentKey === "view")
      setResolvedKey(
        new URLSearchParams(window.location.search).get("key") ?? "",
      );
  }, [experimentKey]);
  if (!bundle) return <Loading />;
  const m =
    bundle.experiments.find((m) => m.experiment.key === resolvedKey) ??
    (bundle.registry?.find((r) => r.key === resolvedKey)
      ? { experiment: bundle.registry.find((r) => r.key === resolvedKey)! }
      : undefined);
  if (!m)
    return (
      <Empty>
        This experiment has no published analysis. The source data or analysis
        may be unavailable.
      </Empty>
    );
  return <ReadoutBody manifest={m} />;
}
export function ReadoutBody({
  manifest: m,
  session = false,
}: {
  manifest: Manifest;
  session?: boolean;
}) {
  const d = design(m);
  const r = result(m);
  const p = rec(r.primary);
  const cuped = rec(r.cuped);
  const seq = rec(r.sequential);
  const guardrails = rows(r.guardrails);
  const secondaries = [...rows(r.secondary), ...rows(r.segments)];
  const isBlocked = blocked(m);
  const source = `${sourceLabel(m)} · ${sourceDetail(m)}`;
  const key = str(m.experiment.key);
  const decision = {
    ...rec(r.decision),
    ...rec(m.decision?.rule_applied),
    ...m.decision,
  };
  const plannedByArm = rec(decision.planned_n_by_arm);
  const treatmentAllocation = num(
    rows(d.variants).find((variant) => variant.name === "treatment")
      ?.allocation,
    0.5,
  );
  const plannedControl = num(plannedByArm.control, num(d.planned_n_per_arm));
  const plannedTreatment = num(
    plannedByArm.treatment,
    Math.ceil(
      (plannedControl * treatmentAllocation) / (1 - treatmentAllocation),
    ),
  );
  const provisional =
    decision.provisional === true ||
    (!isBlocked &&
      (num(p.n_control) < plannedControl ||
        num(p.n_treatment) < plannedTreatment));
  const seqPoints = rows(seq.points ?? seq.history);
  const limitations = Array.isArray(r.limitations)
    ? r.limitations
    : Array.isArray(m.experiment.limitations)
      ? m.experiment.limitations
      : [];
  return (
    <>
      <div className="readout-topline">
        <Link href="/experiments">← All experiments</Link>
        <div className="readout-actions">
          <button className="button small" onClick={() => window.print()}>
            Print readout
          </button>
          {!session && (
            <a
              className="button small"
              href={`${BASE}/readouts/${key}.md`}
              download
            >
              <Icon name="download" size={14} />
              Markdown
            </a>
          )}
          {!session && (
            <a
              className="button small"
              href={`${BASE}/readouts/${key}.html`}
              download
            >
              HTML
            </a>
          )}
        </div>
      </div>
      <div className="readout-title">
        <div className="eyebrow">
          <span />
          EXPERIMENT READOUT / {key.toUpperCase().replaceAll("_", " ")}
        </div>
        <div className="readout-title-line">
          <h1>{str(m.experiment.name, key)}</h1>
          <div>
            <Badge value={decision.decision ?? m.experiment.status} />
            {provisional && <span className="tag">PROVISIONAL</span>}
          </div>
        </div>
        <p>
          {str(
            m.experiment.hypothesis ?? d.hypothesis,
            "A pre-registered experiment with recorded health checks and explicit decision rules.",
          )}
        </p>
        <div className="readout-meta">
          <Source label={sourceLabel(m)} detail={sourceDetail(m)} />
          <span>
            Run <code>{str(m.run?.id, "unavailable").slice(0, 12)}</code>
          </span>
          <span>
            {m.run?.ran_at
              ? new Date(str(m.run.ran_at)).toLocaleDateString("en-US", {
                  month: "long",
                  day: "numeric",
                  year: "numeric",
                })
              : "Run date unavailable"}
          </span>
          <span className="protocol-lock">◇ Design recorded</span>
        </div>
      </div>
      <div className="readout-layout">
        <aside className="section-index">
          <div className="mini-label">IN THIS READOUT</div>
          {sections.map((s, i) => (
            <a key={s} href={`#${anchor(s)}`}>
              <span>{String(i + 1).padStart(2, "0")}</span>
              {s}
            </a>
          ))}
          <div className="index-foot">
            Evidence in order.
            <br />
            Every result traceable.
          </div>
        </aside>
        <div className="readout-content">
          <Section
            n={1}
            title="Health"
            subtitle="Verify the experiment before interpreting its metrics."
          >
            <div className={`health-verdict ${isBlocked ? "unhealthy" : ""}`}>
              <div className="verdict-icon">{isBlocked ? "⊘" : "✓"}</div>
              <div>
                <h3>
                  {isBlocked
                    ? "Analysis is blocked"
                    : "Randomization health recorded"}
                </h3>
                <p>
                  {isBlocked
                    ? "The health gate prevents this run from producing a launch recommendation."
                    : "The observed traffic allocation is checked before any result is made available."}
                </p>
              </div>
              <Badge
                value={
                  isBlocked
                    ? "block"
                    : m.health?.some((h) => h.status === "warn")
                      ? "warn"
                      : "pass"
                }
              />
            </div>
            {m.health?.map((h, i) =>
              str(h.check ?? h.kind, "").includes("srm") ? (
                <HealthChart key={i} check={h} source={source} />
              ) : (
                <div className="health-line" key={i}>
                  <div>
                    <strong>
                      {str(h.check ?? h.kind).replaceAll("_", " ")}
                      {typeof h.metric_key === "string"
                        ? `: ${h.metric_key}`
                        : ""}
                    </strong>
                    <p>
                      {str(h.check ?? h.kind) === "exposure" &&
                      m.experiment.source === "public"
                        ? "All assigned players are included. Actual gate exposure is unobserved; the result is an assignment effect."
                        : str(h.detail)}
                    </p>
                    {Object.keys(rec(h.by_arm)).length > 0 && (
                      <p>
                        {str(h.check ?? h.kind) === "exposure" &&
                        m.experiment.source === "public"
                          ? "Analysis inclusion"
                          : str(h.check ?? h.kind) === "exposure"
                            ? "Exposure coverage"
                            : "Missingness"}
                        :{" "}
                        {Object.entries(rec(h.by_arm))
                          .map(([arm, fraction]) => `${arm} ${pct(fraction)}`)
                          .join(" / ")}
                      </p>
                    )}
                  </div>
                  <Badge value={h.status} />
                </div>
              ),
            )}
          </Section>
          <Section
            n={2}
            title="Design"
            subtitle="The question, the thresholds, and the rule, declared up front."
          >
            <div className="design-summary">
              <Field
                label="PRIMARY METRIC"
                value={str(
                  rows(d.metrics).find((x) => x.key === d.primary_metric_key)
                    ?.name ?? d.primary_metric_key,
                  "Not recorded",
                )}
              />
              <Field
                label="MINIMUM DETECTABLE EFFECT"
                value={`${pct(d.mde_relative)} relative / ${fmt(num(d.mde_relative) * num(d.baseline))} absolute`}
              />
              <Field
                label="ALPHA / TARGET POWER"
                value={`${fmt(d.alpha)} / ${pct(d.power)}`}
              />
              <Field
                label="PLANNED SAMPLE / ARM"
                value={fmt(d.planned_n_per_arm ?? d.n_per_arm, 0)}
              />
              <Field
                label="PLANNED DURATION"
                value={`${fmt(d.planned_days ?? d.days, 0)} days`}
              />
              <Field
                label="ALLOCATION"
                value={
                  typeof d.allocation === "number"
                    ? pct(d.allocation)
                    : rows(d.variants)
                        .map((v) => `${str(v.name)} ${pct(v.allocation)}`)
                        .join(" / ")
                }
              />
            </div>
            <div className="hash-block">
              <span>PRE-REGISTRATION HASH</span>
              <code>{str(m.experiment.design_hash, "Hash not recorded")}</code>
            </div>
            {["public", "uploaded"].includes(str(m.experiment.source)) && (
              <div className="notice">
                <strong>Retrospective design reconstruction</strong>
                <p>
                  This design was recorded before this platform analyzed the
                  supplied outcomes. The hash does not establish historical
                  pre-registration by the original experiment team.
                </p>
              </div>
            )}
            {Array.isArray(m.experiment.design_deviations) &&
              m.experiment.design_deviations.length > 0 && (
                <div className="notice warning">
                  <strong>Protocol deviation recorded</strong>
                  <p>{JSON.stringify(m.experiment.design_deviations)}</p>
                </div>
              )}
          </Section>
          {isBlocked ? (
            <div className="blocked-metrics">
              <span>⊘</span>
              <h2>Metric analysis withheld</h2>
              <p>
                Resolve the failed health check and run a new analysis. This
                readout intentionally contains no metric results.
              </p>
            </div>
          ) : (
            <>
              <Section
                n={3}
                title="Primary metric"
                subtitle="Magnitude and uncertainty, measured against the decision threshold."
              >
                <div className="metric-summary">
                  <div>
                    <span className="mini-label">
                      ABSOLUTE EFFECT · CONFIDENCE INTERVAL
                    </span>
                    <strong>{interval(p)}</strong>
                  </div>
                  <div>
                    <span className="mini-label">
                      RELATIVE EFFECT · CONFIDENCE INTERVAL
                    </span>
                    <strong>
                      {interval(
                        {
                          estimate: p.relative,
                          ci_low: p.relative_ci_low,
                          ci_high: p.relative_ci_high,
                        },
                        true,
                      )}
                    </strong>
                  </div>
                </div>
                <ChartCard
                  title={str(p.name ?? p.key, "Primary outcome")}
                  subtitle="Intervals crossing zero remain compatible with no effect. The lower axis rescales the absolute interval with control fixed; the relative interval above also retains denominator uncertainty."
                  source={source}
                  table={<DataTable columns={metricColumns} data={[p]} />}
                >
                  <Forest
                    data={[p]}
                    mde={
                      (p.direction === "lower_is_better" ? -1 : 1) *
                      num(d.mde_relative, 0) *
                      Math.abs(num(d.baseline, 0))
                    }
                    baseline={num(p.control_mean)}
                  />
                </ChartCard>
                <div className="stat-inline">
                  <span>
                    Control mean <b>{fmt(p.control_mean)}</b>
                  </span>
                  <span>
                    Treatment mean <b>{fmt(p.treatment_mean)}</b>
                  </span>
                  <span>
                    p-value <b>{pValue(p.p_value)}</b>
                  </span>
                  <span>
                    Projected power at registered effect{" "}
                    <b>
                      {pct(r.achieved_power ?? p.design_effect_projected_power)}
                    </b>
                  </span>
                </div>
              </Section>
              <Section
                n={4}
                title="Guardrails"
                subtitle="A primary improvement does not excuse unacceptable regressions."
              >
                {guardrails.length ? (
                  guardrails.map((g, i) => {
                    const sign = g.direction === "lower_is_better" ? -1 : 1;
                    const favorableEffect = sign * num(g.relative);
                    const plotted = {
                      ...g,
                      name: str(g.name ?? g.key),
                      estimate: favorableEffect,
                      ci_low: g.one_sided_good_direction_low,
                      ci_high:
                        2 * favorableEffect -
                        num(g.one_sided_good_direction_low),
                      p_value: g.noninferiority_p_value,
                      verdict: g.passed ? "pass" : "fail",
                    };
                    const raw = rows(r.raw_metrics).find(
                      (metric) => metric.key === g.key,
                    );
                    return (
                      <ChartCard
                        key={i}
                        title={str(g.name ?? g.key, "Guardrail")}
                        subtitle={`Relative margin: ${pct(g.margin)} · ${g.passed ? "pass" : "fail"} · ${pct(1 - 2 * num(d.alpha, 0.05))} central interval, equivalent to the ${pct(1 - num(d.alpha, 0.05))} one-sided lower bound; favorable direction is positive`}
                        source={source}
                        table={
                          <DataTable
                            columns={[
                              { key: "name", label: "Metric" },
                              {
                                key: "estimate",
                                label: "Favorable relative effect",
                                percent: true,
                              },
                              {
                                key: "ci_low",
                                label: "One-sided lower bound",
                                percent: true,
                              },
                              {
                                key: "ci_high",
                                label: "Central interval upper",
                                percent: true,
                              },
                              {
                                key: "p_value",
                                label: "Non-inferiority p-value",
                              },
                              {
                                key: "margin",
                                label: "Relative margin",
                                percent: true,
                              },
                              { key: "verdict", label: "Verdict" },
                            ]}
                            data={[plotted]}
                          />
                        }
                      >
                        <Forest
                          data={[plotted]}
                          margin={num(g.margin, 0)}
                          percent
                          axisLabel="FAVORABLE RELATIVE EFFECT"
                        />
                        {raw && (
                          <p className="caption">
                            Sensitivity without the declared outlier policy, in
                            original metric units: {interval(raw)}.
                            Declared-policy estimate: {interval(g)}. The
                            guardrail verdict uses the declared policy.
                          </p>
                        )}
                      </ChartCard>
                    );
                  })
                ) : (
                  <Empty>
                    No guardrail metric was registered for this experiment.
                  </Empty>
                )}
              </Section>
              <Section
                n={5}
                title="Variance"
                subtitle="Use pre-period information only when it is available and eligible."
              >
                {cuped.applicable === true ? (
                  <>
                    <div className="notice">
                      <strong>
                        {pct(cuped.variance_reduction)} estimated variance
                        reduction
                      </strong>
                      <p>
                        Equivalent sample saved:{" "}
                        <span className="mono">{fmt(cuped.n_saved, 0)}</span>.
                        This is a variance-model planning equivalence, not
                        observed users saved. The registered decision uses the
                        unadjusted primary.
                      </p>
                    </div>
                    <ChartCard
                      title="CUPED adjustment"
                      source={source}
                      table={
                        <DataTable
                          columns={metricColumns}
                          data={[
                            { ...rec(cuped.unadjusted), name: "Unadjusted" },
                            { ...rec(cuped.adjusted), name: "CUPED adjusted" },
                          ]}
                        />
                      }
                    >
                      <Forest
                        data={[
                          { ...rec(cuped.unadjusted), name: "Unadjusted" },
                          { ...rec(cuped.adjusted), name: "CUPED adjusted" },
                        ]}
                      />
                    </ChartCard>
                  </>
                ) : (
                  <Empty>
                    {str(
                      cuped.reason,
                      "No eligible pre-period covariate is available. CUPED is not applied.",
                    )}
                  </Empty>
                )}
              </Section>
              <Section
                n={6}
                title="Sequential"
                subtitle="Repeated looks require an inference method designed for repeated looks."
              >
                <ChartCard
                  title="The effect, as evidence accumulates"
                  subtitle="Confidence sequence and naive fixed-horizon interval"
                  source={source}
                  table={
                    <DataTable
                      columns={[
                        { key: "day", label: "Day" },
                        { key: "estimate", label: "Effect" },
                        { key: "ci_low", label: "CS lower" },
                        { key: "ci_high", label: "CS upper" },
                        { key: "naive_low", label: "Naive lower" },
                        { key: "naive_high", label: "Naive upper" },
                        { key: "p_value", label: "Running-min p (approx.)" },
                        {
                          key: "naive_p_value",
                          label: "Naive fixed-horizon p",
                        },
                      ]}
                      data={seqPoints}
                    />
                  }
                >
                  <SeriesChart
                    data={seqPoints.map((x) => ({
                      ...x,
                      naive_estimate: x.estimate,
                    }))}
                    x="day"
                    xLabel="DAY OF EXPERIMENT"
                    series={[
                      {
                        key: "estimate",
                        label: "Sequential",
                        low: "ci_low",
                        high: "ci_high",
                      },
                      {
                        key: "naive_estimate",
                        label: "Naive fixed horizon",
                        low: "naive_low",
                        high: "naive_high",
                        dashed: true,
                      },
                    ]}
                    reference={0}
                    referenceLabel="No effect"
                    markers={[
                      ...(typeof seq.first_rejection_day === "number"
                        ? [
                            {
                              x: seq.first_rejection_day,
                              label: "Sequential rejects",
                            },
                          ]
                        : []),
                      ...(typeof seq.naive_first_rejection_day === "number"
                        ? [
                            {
                              x: seq.naive_first_rejection_day,
                              label: "Naive rejects",
                              dashed: true,
                            },
                          ]
                        : []),
                    ]}
                  />
                </ChartCard>
                <div className="stat-inline">
                  <span>
                    Sequential first rejection{" "}
                    <b>
                      {seq.first_rejection_day == null
                        ? "Not observed"
                        : `Day ${fmt(seq.first_rejection_day, 0)}`}
                    </b>
                  </span>
                  <span>
                    Naive first rejection{" "}
                    <b>
                      {seq.naive_first_rejection_day == null
                        ? "Not observed"
                        : `Day ${fmt(seq.naive_first_rejection_day, 0)}`}
                    </b>
                  </span>
                  <span>
                    Mixing variance <b>{fmt(seq.mixing_variance, 5)}</b>
                  </span>
                </div>
                {typeof seq.reason === "string" && (
                  <p className="caption">{seq.reason}</p>
                )}
                {typeof seq.limitation === "string" && (
                  <p className="caption">{str(seq.limitation)}</p>
                )}
                <p className="caption">
                  The sequential p-value retains the strongest earlier evidence.
                  The displayed band is the current, un-intersected interval, so
                  it can include zero after an earlier rejection. The naive
                  p-value uses only the current look.
                </p>
              </Section>
              <Section
                n={7}
                title="Secondary and segments"
                subtitle="Benjamini-Hochberg is applied separately to the secondary-metric family and the segment family."
              >
                {secondaries.length ? (
                  <ChartCard
                    title="Exploratory effects"
                    subtitle="Circle: raw p. Square: BH-adjusted p. Filled markers are significant. Multiplicity changes the verdict, not the effect interval."
                    source={source}
                    table={
                      <DataTable
                        columns={[
                          ...metricColumns,
                          { key: "p_adjusted", label: "BH adjusted p" },
                          { key: "significant", label: "Raw significant" },
                          {
                            key: "significant_adjusted",
                            label: "BH significant",
                          },
                        ]}
                        data={secondaries.map((s) => ({
                          ...s,
                          significant: String(s.significant),
                          significant_adjusted: String(s.significant_adjusted),
                        }))}
                      />
                    }
                  >
                    <Forest
                      corrections
                      data={secondaries.map((s) => ({
                        ...s,
                        name: str(s.segment ?? s.name ?? s.key),
                      }))}
                    />
                    <div className="segment-verdicts">
                      {secondaries.map((s, i) => (
                        <div key={i}>
                          <span>{str(s.segment ?? s.name ?? s.key)}</span>
                          <span>
                            Raw <b>{s.significant ? "●" : "○"}</b>
                          </span>
                          <span>
                            BH <b>{s.significant_adjusted ? "●" : "○"}</b>
                          </span>
                          <span>Adjusted p = {pValue(s.p_adjusted)}</span>
                        </div>
                      ))}
                    </div>
                  </ChartCard>
                ) : (
                  <Empty>
                    No secondary or segment estimates were recorded.
                  </Empty>
                )}
              </Section>
            </>
          )}
          <Section
            n={8}
            title="Decision"
            subtitle="A recommendation from the declared rule, with its reason attached."
          >
            <div
              className={`decision-panel ${isBlocked ? "decision-blocked" : ""}`}
            >
              {provisional && (
                <div className="notice warning">
                  <strong>PROVISIONAL: planned sample not reached</strong>
                  <p>
                    Achieved: {fmt(p.n_control, 0)} control /{" "}
                    {fmt(p.n_treatment, 0)} treatment. Registered targets:{" "}
                    {fmt(plannedControl, 0)} control /{" "}
                    {fmt(plannedTreatment, 0)} treatment. This is not a
                    finalized launch decision.
                  </p>
                </div>
              )}
              <span className="mini-label">RECOMMENDATION</span>
              <h2>{str(decision.decision, "Pending").replaceAll("_", " ")}</h2>
              <p>{str(decision.reason, "No decision has been recorded.")}</p>
              <div className="decision-rule">
                <span>THE REGISTERED RULE</span>
                <blockquote>
                  {str(
                    decision.rule ?? rec(d.decision_rule).text,
                    "Decision rule not recorded.",
                  )}
                </blockquote>
              </div>
            </div>
          </Section>
          <Section
            n={9}
            title="Limitations"
            subtitle="What this readout can and cannot establish."
          >
            {limitations.length ? (
              <ul className="limitations">
                {limitations.map((l, i) => (
                  <li key={i}>
                    {typeof l === "string" ? l : JSON.stringify(l)}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="body-copy">
                Interpret this result within its declared analysis unit,
                observation window, and metric definitions. Source-specific
                limitations are included in the downloadable readout.
              </p>
            )}
            <p className="caption">
              Outlier policy:{" "}
              {JSON.stringify(
                p.outlier_policy ??
                  "See the registered design and canonical readout.",
              )}
            </p>
          </Section>
          <Section
            n={10}
            title="Reproduce"
            subtitle="Regenerate the document from the stored analysis manifest."
          >
            <div className="code-command">
              <code>uv run readout render {key}</code>
              <button
                onClick={() =>
                  navigator.clipboard.writeText(`uv run readout render ${key}`)
                }
              >
                Copy
              </button>
            </div>
            <p className="caption">
              This page reads the same manifest as the published Markdown and
              HTML readouts.
            </p>
          </Section>
        </div>
      </div>
    </>
  );
}
function Section({
  n,
  title,
  subtitle,
  children,
}: {
  n: number;
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  return (
    <section id={anchor(title)} className="readout-section">
      <header className="section-heading">
        <span>{String(n).padStart(2, "0")}</span>
        <div>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
      </header>
      {children}
    </section>
  );
}
function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <span className="mini-label">{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
function HealthChart({ check: h, source }: { check: Row; source: string }) {
  const obs = rec(h.observed);
  const exp = rec(h.expected);
  const data = ["control", "treatment"].map((key) => ({
    variant: key,
    observed: num(obs[key]),
    expected: num(exp[key]),
  }));
  const max = Math.max(...data.flatMap((r) => [r.observed, r.expected]), 1);
  const pv = num(h.p_value);
  return (
    <ChartCard
      title={str(h.check ?? h.kind, "Sample ratio mismatch").replaceAll(
        "_",
        " ",
      )}
      subtitle={str(h.detail)}
      source={source}
      table={
        <DataTable
          columns={[
            { key: "variant", label: "Variant" },
            { key: "observed", label: "Observed" },
            { key: "expected", label: "Expected" },
          ]}
          data={data}
        />
      }
    >
      <div className="health-chart">
        <div className="count-bars">
          <div className="chart-legend">
            <span>
              <i />
              Observed
            </span>
            <span>
              <i className="dashed" />
              Expected allocation
            </span>
          </div>
          {data.map((r, i) => (
            <div className="count-row" key={r.variant}>
              <span>{r.variant}</span>
              <div className="count-track">
                <div
                  tabIndex={0}
                  title={`${r.variant}: ${fmt(r.observed, 0)} observed; ${fmt(r.expected, 1)} expected`}
                  style={{
                    width: `${(r.observed / max) * 95}%`,
                    background: i === 0 ? "var(--control)" : "var(--treatment)",
                  }}
                />
                <i style={{ left: `${(r.expected / max) * 95}%` }} />
              </div>
              <strong>{fmt(r.observed, 0)}</strong>
            </div>
          ))}
        </div>
        <div className="srm-stats">
          <div>
            <span>χ² statistic</span>
            <strong>{fmt(h.statistic)}</strong>
          </div>
          <div>
            <span>p-value</span>
            <strong>{pValue(h.p_value)}</strong>
          </div>
          <div>
            <span>α = 0.05</span>
            <Badge
              value={
                Number.isFinite(pv) ? (pv < 0.05 ? "warn" : "pass") : "unknown"
              }
            />
          </div>
          <div>
            <span>α = 0.001</span>
            <Badge
              value={
                Number.isFinite(pv)
                  ? pv < 0.001
                    ? "block"
                    : "pass"
                  : "unknown"
              }
            />
          </div>
        </div>
      </div>
    </ChartCard>
  );
}
