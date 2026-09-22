"use client";
import { useState } from "react";
import { api, fmt, rec, Row, rows, str } from "@/lib/data";
import { Icon, PageHead, useBundle } from "./shell";
import { ChartCard, DataTable, SeriesChart } from "./charts";
export function Assignment() {
  const { bundle } = useBundle();
  const [unit, setUnit] = useState("reviewer-001");
  const [experiment, setExperiment] = useState("null");
  const [assignment, setAssignment] = useState<Row | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const data = rec(bundle?.assignment);
  const hist = rows(data.histogram ?? data.buckets).map((r) => ({
    ...r,
    bucket: r.bucket ?? `${fmt(r.bucket_start, 0)}-${fmt(r.bucket_end, 0)}`,
  }));
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      setAssignment(
        await api("/api/assign", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ experiment_key: experiment, unit_id: unit }),
        }),
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Assignment request failed.");
    } finally {
      setLoading(false);
    }
  }
  return (
    <>
      <PageHead
        eyebrow="DETERMINISTIC ASSIGNMENT"
        title="One unit. One stable assignment."
        description="A salted SHA-256 hash maps each unit into a fixed bucket, then into a variant."
      />
      <div className="assignment-layout">
        <section className="input-card">
          <div className="panel-title">
            <h2>Try an assignment</h2>
            <span className="tag">LIVE API</span>
          </div>
          <form onSubmit={submit}>
            <label className="text-field">
              Experiment
              <select
                value={experiment}
                onChange={(e) => setExperiment(e.target.value)}
              >
                {bundle?.experiments.map((m) => (
                  <option
                    key={str(m.experiment.key)}
                    value={str(m.experiment.key)}
                  >
                    {str(m.experiment.name)}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-field">
              Unit ID
              <input
                value={unit}
                required
                maxLength={500}
                onChange={(e) => setUnit(e.target.value)}
                autoComplete="off"
              />
            </label>
            <button className="button primary full" disabled={loading || !unit}>
              {loading ? "Computing assignment..." : "Resolve assignment"}
              <Icon name="arrow" size={16} />
            </button>
          </form>
          <p className="input-foot">
            Repeat the same input to verify stability. This public lookup does
            not enroll a unit or write an assignment record.
          </p>
          {error && (
            <div className="inline-error" role="alert">
              {error}
            </div>
          )}
        </section>
        <section className="assignment-output">
          <div className="assignment-flow">
            <div>
              <span>01 / HASH</span>
              <code>
                {assignment
                  ? str(assignment.hash)
                  : "Submit a unit to inspect its SHA-256 hash"}
              </code>
            </div>
            <i>↓</i>
            <div>
              <span>02 / BUCKET</span>
              <strong>
                {assignment ? fmt(assignment.bucket, 0) : "Pending"}
              </strong>
              <small>First eight hexadecimal characters, modulo 10,000</small>
            </div>
            <i>↓</i>
            <div>
              <span>03 / VARIANT</span>
              <strong
                className={
                  assignment?.variant === "treatment" ? "treatment-text" : ""
                }
              >
                {assignment ? str(assignment.variant) : "Pending"}
              </strong>
              <small>Mapped using the experiment allocation</small>
            </div>
          </div>
        </section>
      </div>
      <ChartCard
        title="Uniformity across the bucket space"
        subtitle="The canonical sample is generated and checked by the assignment test."
        source={str(
          data.source,
          "Measured assignment audit · committed results",
        )}
        table={
          <DataTable
            columns={[
              { key: "bucket", label: "Bucket range" },
              { key: "count", label: "Observed" },
              { key: "expected", label: "Expected" },
            ]}
            data={hist}
          />
        }
      >
        <SeriesChart
          data={hist}
          x="bucket"
          xLabel="BUCKET RANGE"
          series={[
            { key: "count", label: "Observed units", bar: true },
            { key: "expected", label: "Expected", dashed: true },
          ]}
        />
      </ChartCard>
    </>
  );
}
