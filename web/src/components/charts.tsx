"use client";
import { Fragment, useState } from "react";
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Bar,
  ErrorBar,
  Scatter,
} from "recharts";
import { fmt, num, pct, Row, str } from "@/lib/data";
import { Empty } from "./shell";
export const pValue = (value: unknown): string => {
  const p = num(value);
  return Number.isFinite(p) && p > 0 && p < 0.0001
    ? p.toExponential(2)
    : fmt(value, 6);
};
export type Series = {
  key: string;
  label: string;
  color?: string;
  dashed?: boolean;
  low?: string;
  high?: string;
  bar?: boolean;
  scatter?: boolean;
};
export function ChartCard({
  title,
  subtitle,
  source,
  children,
  table,
  wide = false,
}: {
  title: string;
  subtitle?: string;
  source?: string;
  children: React.ReactNode;
  table: React.ReactNode;
  wide?: boolean;
}) {
  const [asTable, setTable] = useState(false);
  return (
    <section className={`chart-card ${wide ? "wide" : ""}`}>
      <div className="chart-heading">
        <div>
          <h3>{title}</h3>
          {subtitle && <p>{subtitle}</p>}
        </div>
        <div className="segmented" aria-label={`${title} view`}>
          <button aria-pressed={!asTable} onClick={() => setTable(false)}>
            Chart
          </button>
          <button aria-pressed={asTable} onClick={() => setTable(true)}>
            Table
          </button>
        </div>
      </div>
      {asTable ? <div className="chart-table">{table}</div> : children}
      {source && <div className="chart-source">◈ {source}</div>}
    </section>
  );
}
export function DataTable({
  columns,
  data,
}: {
  columns: { key: string; label: string; percent?: boolean }[];
  data: Row[];
}) {
  return (
    <div className="table-scroll">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((c) => (
              <th key={c.key}>{c.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((r, i) => (
            <tr key={i}>
              {columns.map((c) => (
                <td key={c.key}>
                  {typeof r[c.key] === "number"
                    ? [
                        "p_value",
                        "p_adjusted",
                        "naive_p_value",
                        "noninferiority_p_value",
                      ].includes(c.key)
                      ? pValue(r[c.key])
                      : c.percent
                        ? pct(r[c.key])
                        : fmt(r[c.key])
                    : str(r[c.key], "Unavailable")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
export function SeriesChart({
  data,
  x,
  series,
  percent = false,
  xPercent = false,
  reference,
  referenceLabel,
  height = 290,
  xLabel,
  markers = [],
}: {
  data: Row[];
  x: string;
  series: Series[];
  percent?: boolean;
  xPercent?: boolean;
  reference?: number;
  referenceLabel?: string;
  height?: number;
  xLabel?: string;
  markers?: { x: number; label: string; dashed?: boolean }[];
}) {
  if (!data.length)
    return (
      <Empty>No measured observations are available for this chart.</Empty>
    );
  const numericX = data.every((row) => Number.isFinite(num(row[x])));
  const normalized = data.map((r) => {
    const out = { ...r };
    series.forEach((s) => {
      if (
        s.low &&
        s.high &&
        Number.isFinite(num(r[s.low])) &&
        Number.isFinite(num(r[s.high]))
      ) {
        out[`${s.key}_band`] = [r[s.low], r[s.high]];
        out[`${s.key}_error`] = [
          num(r[s.key]) - num(r[s.low]),
          num(r[s.high]) - num(r[s.key]),
        ];
      }
    });
    return out;
  });
  return (
    <>
      <div className="chart-legend">
        {series.map((s, i) => (
          <span key={s.key}>
            <i
              style={{
                background:
                  s.color ?? (i === 0 ? "var(--treatment)" : "var(--control)"),
                borderTopColor:
                  s.color ?? (i === 0 ? "var(--treatment)" : "var(--control)"),
                borderTopStyle: s.dashed ? "dashed" : "solid",
              }}
            />
            {s.label}
          </span>
        ))}
      </div>
      <div
        className="chart-region"
        style={{ height }}
        role="img"
        aria-label={`${series.map((s) => s.label).join(" and ")} by ${xLabel ?? x}. Use the table view for exact values.`}
      >
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={normalized}
            margin={{ top: 20, right: 26, bottom: 20, left: 6 }}
            accessibilityLayer
          >
            <CartesianGrid stroke="var(--grid)" vertical={false} />
            <XAxis
              dataKey={x}
              type={numericX ? "number" : "category"}
              domain={numericX ? ["dataMin", "dataMax"] : undefined}
              tickFormatter={
                numericX
                  ? (value) => (xPercent ? pct(value) : fmt(value, 2))
                  : undefined
              }
              tick={{
                fill: "var(--muted)",
                fontSize: 11,
                fontFamily: "monospace",
              }}
              axisLine={false}
              tickLine={false}
              minTickGap={30}
              label={
                xLabel
                  ? {
                      value: xLabel,
                      position: "insideBottom",
                      offset: -15,
                      fill: "var(--muted)",
                      fontSize: 11,
                    }
                  : undefined
              }
            />
            <YAxis
              tickFormatter={(v) =>
                percent ? `${(Number(v) * 100).toFixed(0)}%` : fmt(v, 2)
              }
              tick={{
                fill: "var(--muted)",
                fontSize: 11,
                fontFamily: "monospace",
              }}
              width={58}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                background: "var(--panel)",
                border: "1px solid var(--border)",
                borderRadius: 8,
                fontSize: 12,
                color: "var(--text)",
              }}
              formatter={(v: unknown, n: unknown) => [
                Array.isArray(v)
                  ? `[${v.map((a) => (percent ? pct(a) : fmt(a))).join(", ")}]`
                  : percent
                    ? pct(v)
                    : fmt(v),
                String(n).replaceAll("_band", " interval"),
              ]}
            />
            {reference !== undefined && (
              <ReferenceLine
                y={reference}
                stroke="var(--muted)"
                strokeDasharray="4 5"
                label={{
                  value: referenceLabel ?? String(reference),
                  fill: "var(--muted)",
                  fontSize: 11,
                  position: "insideTopRight",
                }}
              />
            )}
            {markers.map((m, i) => (
              <ReferenceLine
                key={i}
                x={m.x}
                stroke={m.dashed ? "var(--control)" : "var(--treatment)"}
                strokeDasharray={m.dashed ? "3 5" : "3 3"}
                label={{
                  value: m.label,
                  position: "insideTopRight",
                  fill: "var(--muted)",
                  fontSize: 9,
                }}
              />
            ))}
            {series.map((s, i) => {
              const color =
                s.color ?? (i === 0 ? "var(--treatment)" : "var(--control)");
              return (
                <Fragment key={s.key}>
                  {s.low && s.high && !s.bar && (
                    <Area
                      type="linear"
                      dataKey={`${s.key}_band`}
                      stroke="none"
                      fill={color}
                      fillOpacity={s.dashed ? 0.075 : 0.14}
                      isAnimationActive={false}
                      name={`${s.label} interval`}
                    />
                  )}{" "}
                  {s.bar ? (
                    <Bar
                      dataKey={s.key}
                      name={s.label}
                      fill={color}
                      radius={[4, 4, 0, 0]}
                      isAnimationActive={false}
                    >
                      {s.low && s.high && (
                        <ErrorBar
                          dataKey={`${s.key}_error`}
                          width={6}
                          strokeWidth={2}
                          stroke="var(--text)"
                        />
                      )}
                    </Bar>
                  ) : s.scatter ? (
                    <Scatter
                      dataKey={s.key}
                      name={s.label}
                      fill={color}
                      shape={s.dashed ? "diamond" : "circle"}
                      isAnimationActive={false}
                    />
                  ) : (
                    <Line
                      type="linear"
                      dataKey={s.key}
                      name={s.label}
                      stroke={color}
                      strokeWidth={2}
                      strokeDasharray={s.dashed ? "5 5" : undefined}
                      dot={{ r: 4, strokeWidth: 2, fill: "var(--panel)" }}
                      activeDot={{ r: 5 }}
                      isAnimationActive={false}
                    />
                  )}
                </Fragment>
              );
            })}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </>
  );
}
export function Forest({
  data,
  mde = 0,
  margin,
  baseline,
  corrections = false,
  percent = false,
  axisLabel = "ABSOLUTE EFFECT",
}: {
  data: Row[];
  mde?: number;
  margin?: number;
  baseline?: number;
  corrections?: boolean;
  percent?: boolean;
  axisLabel?: string;
}) {
  const format = percent ? pct : fmt;
  const valid = data.filter(
    (r) =>
      Number.isFinite(num(r.estimate)) &&
      Number.isFinite(num(r.ci_low)) &&
      Number.isFinite(num(r.ci_high)),
  );
  if (!valid.length)
    return <Empty>No estimable interval is recorded for this section.</Empty>;
  const extreme =
    Math.max(
      ...valid.flatMap((r) => [
        Math.abs(num(r.ci_low)),
        Math.abs(num(r.ci_high)),
      ]),
      Math.abs(mde),
      Math.abs(margin ?? 0),
      0.001,
    ) * 1.28;
  const scale = (v: number) => 220 + ((v + extreme) / (extreme * 2)) * 560;
  const h = valid.length * 68 + 92;
  return (
    <div className="forest-scroll">
      <svg
        className="forest"
        viewBox={`0 0 850 ${h}`}
        role="img"
        aria-label="Effect estimates with confidence intervals. Zero is the vertical reference; numerical values are available in the table."
      >
        <defs>
          <pattern
            id="margin-hatch"
            width="7"
            height="7"
            patternUnits="userSpaceOnUse"
            patternTransform="rotate(45)"
          >
            <line
              x1="0"
              y1="0"
              x2="0"
              y2="7"
              stroke="var(--warn)"
              strokeWidth="1"
              opacity=".2"
            />
          </pattern>
        </defs>
        {mde !== 0 && (
          <>
            <rect
              x={scale(Math.min(0, mde))}
              y="15"
              width={Math.abs(scale(mde) - scale(0))}
              height={h - 68}
              fill="var(--treatment)"
              opacity=".07"
            />
            <line
              x1={scale(mde)}
              x2={scale(mde)}
              y1="15"
              y2={h - 53}
              stroke="var(--treatment)"
              opacity=".5"
              strokeDasharray="3 4"
            />
            <text x={scale(mde) + 6} y="17" fill="var(--muted)" fontSize="10">
              MDE
            </text>
          </>
        )}
        {margin !== undefined && (
          <rect
            x={scale(-extreme)}
            y="15"
            width={scale(-Math.abs(margin)) - scale(-extreme)}
            height={h - 68}
            fill="url(#margin-hatch)"
          />
        )}
        <line
          x1={scale(0)}
          x2={scale(0)}
          y1="20"
          y2={h - 53}
          stroke="var(--muted)"
          strokeDasharray="3 4"
        />
        {valid.map((r, i) => {
          const y = 46 + i * 68;
          const color = i === 1 ? "var(--control)" : "var(--treatment)";
          return (
            <g key={i} tabIndex={0}>
              <title>{`${str(r.name ?? r.key, "Estimate")}: ${format(r.estimate)} [${format(r.ci_low)}, ${format(r.ci_high)}]`}</title>
              <text x="0" y={y - 4} fill="var(--text)" fontSize="12">
                {str(r.name ?? r.key, "Estimate")}
              </text>
              <text
                x="0"
                y={y + 16}
                fill="var(--muted)"
                fontSize="11"
                fontFamily="monospace"
              >
                {format(r.estimate)} [{format(r.ci_low)}, {format(r.ci_high)}]
              </text>
              <line x1="220" x2="780" y1={y} y2={y} stroke="var(--grid)" />
              <line
                x1={scale(num(r.ci_low))}
                x2={scale(num(r.ci_high))}
                y1={y}
                y2={y}
                stroke={color}
                strokeWidth="2"
                strokeDasharray={i === 1 ? "5 3" : undefined}
              />
              <line
                x1={scale(num(r.ci_low))}
                x2={scale(num(r.ci_low))}
                y1={y - 6}
                y2={y + 6}
                stroke={color}
                strokeWidth="2"
              />
              <line
                x1={scale(num(r.ci_high))}
                x2={scale(num(r.ci_high))}
                y1={y - 6}
                y2={y + 6}
                stroke={color}
                strokeWidth="2"
              />
              {corrections ? (
                <>
                  <circle
                    cx={scale(num(r.estimate))}
                    cy={y - 8}
                    r="4"
                    fill={r.significant ? color : "var(--panel)"}
                    stroke={color}
                    strokeWidth="2"
                  />
                  <rect
                    x={scale(num(r.estimate)) - 4}
                    y={y + 4}
                    width="8"
                    height="8"
                    fill={r.significant_adjusted ? color : "var(--panel)"}
                    stroke={color}
                    strokeWidth="2"
                  />
                </>
              ) : (
                <circle
                  cx={scale(num(r.estimate))}
                  cy={y}
                  r="5"
                  fill={color}
                  stroke="var(--panel)"
                  strokeWidth="2"
                />
              )}
            </g>
          );
        })}
        {[-extreme, -extreme / 2, 0, extreme / 2, extreme].map((v, i) => (
          <g key={i}>
            <text
              x={scale(v)}
              y={h - 28}
              textAnchor="middle"
              fill="var(--muted)"
              fontSize="10"
              fontFamily="monospace"
            >
              {format(v)}
            </text>
            {baseline !== undefined && baseline !== 0 && (
              <text
                x={scale(v)}
                y={h - 9}
                textAnchor="middle"
                fill="var(--muted)"
                fontSize="10"
                fontFamily="monospace"
              >
                {pct(v / baseline)}
              </text>
            )}
          </g>
        ))}
        <text x="0" y={h - 28} fill="var(--muted)" fontSize="10">
          {axisLabel}
        </text>
        {baseline !== undefined && baseline !== 0 && (
          <text x="0" y={h - 9} fill="var(--muted)" fontSize="10">
            RELATIVE SCALE (FIXED CONTROL)
          </text>
        )}
      </svg>
    </div>
  );
}
export const metricColumns = [
  { key: "name", label: "Metric" },
  { key: "estimate", label: "Effect" },
  { key: "ci_low", label: "CI lower" },
  { key: "ci_high", label: "CI upper" },
  { key: "p_value", label: "p-value" },
];
