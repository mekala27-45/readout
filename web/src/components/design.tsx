"use client";
import { useMemo, useState } from "react";
import { plan } from "@/lib/power";
import { fmt, num, pct, rec, Row, str } from "@/lib/data";
import { PageHead, useBundle } from "./shell";
import { ChartCard, DataTable, SeriesChart } from "./charts";
export function DesignCalculator() {
  const { bundle } = useBundle();
  const [baseline, setBaseline] = useState(20);
  const [mde, setMde] = useState(2);
  const [alpha, setAlpha] = useState(5);
  const [power, setPower] = useState(80);
  const [allocation, setAllocation] = useState(50);
  const [daily, setDaily] = useState(1000);
  const valid =
    baseline > 0 &&
    baseline < 100 &&
    mde > 0 &&
    baseline + mde < 100 &&
    alpha > 0 &&
    alpha < 50 &&
    power > 50 &&
    power < 100 &&
    allocation > 0 &&
    allocation < 100 &&
    daily > 0;
  const calculated = useMemo(
    () =>
      valid
        ? plan(
            baseline / 100,
            mde / 100,
            alpha / 100,
            power / 100,
            allocation / 100,
          )
        : null,
    [baseline, mde, alpha, power, allocation, daily, valid],
  );
  const curves = calculated
    ? Array.from({ length: 21 }, (_, i) => {
        const n =
          i === 8
            ? calculated.n
            : Math.max(1, Math.round(calculated.n * (0.1 + i * 0.115)));
        const r: Row = { n };
        [0.5, 1, 1.5].forEach((f, j) => {
          if (baseline + mde * f < 100)
            r[`mde${j}`] = plan(
              baseline / 100,
              (mde * f) / 100,
              alpha / 100,
              power / 100,
              allocation / 100,
            ).achieved(n);
        });
        return r;
      })
    : [];
  const pp = rec(bundle?.pricepoint ?? rec(bundle?.calibration).pricepoint);
  return (
    <>
      <PageHead
        eyebrow="PRE-REGISTRATION / DESIGN"
        title="Know what the experiment needs."
        description="Set a meaningful effect, choose the error budget, and plan the sample before you start."
      />
      <div className="calculator-layout">
        <section className="input-card">
          <div className="panel-title">
            <h2>Design parameters</h2>
            <span className="tag">BINARY OUTCOME</span>
          </div>
          <p className="caption">
            Two-sided, independent proportions. MDE is an absolute
            percentage-point change.
          </p>
          <NumberField
            label="Baseline conversion"
            value={baseline}
            set={setBaseline}
            suffix="%"
            min={0.01}
            max={99}
          />
          <NumberField
            label="Minimum detectable effect"
            value={mde}
            set={setMde}
            suffix="pp"
            min={0.01}
            max={99}
          />
          <div className="input-pair">
            <NumberField
              label="Significance α"
              value={alpha}
              set={setAlpha}
              suffix="%"
              min={0.01}
              max={49}
            />
            <NumberField
              label="Target power"
              value={power}
              set={setPower}
              suffix="%"
              min={51}
              max={99.9}
            />
          </div>
          <NumberField
            label="Treatment allocation"
            value={allocation}
            set={setAllocation}
            suffix="%"
            min={1}
            max={99}
          />
          <NumberField
            label="Eligible units per day"
            value={daily}
            set={setDaily}
            suffix="units"
            min={1}
            max={10000000}
          />
          <div className="input-foot">
            Normal approximation. Independent units, fixed horizon, no
            continuity correction. CUPED savings are not assumed.
          </div>
        </section>
        <div>
          <div className="design-output">
            <span className="mini-label">REQUIRED SAMPLE</span>
            <div className="planned-n">
              {calculated ? fmt(calculated.n, 0) : "Invalid design"}
              <span>control units</span>
            </div>
            <div className="design-output-bottom">
              <span>
                Treatment{" "}
                <strong>
                  {calculated ? fmt(calculated.treatment, 0) : "Unavailable"}
                </strong>
              </span>
              <span>
                Estimated duration{" "}
                <strong>
                  {calculated
                    ? `${Math.ceil(Math.max(calculated.n / (1 - allocation / 100), calculated.treatment / (allocation / 100)) / daily)} days`
                    : "Unavailable"}
                </strong>
              </span>
            </div>
            <p>
              {calculated
                ? `Planning assumptions: ${pct(alpha / 100)} alpha, ${pct(power / 100)} power, ${fmt(mde, 2)} percentage-point MDE.`
                : "Enter a valid baseline, effect, allocation, and error budget."}
            </p>
          </div>
          <ChartCard
            title="Power grows with the sample"
            subtitle="The target is fixed before the outcome is observed."
            source="Calculated planning curves · normal approximation"
            table={
              <DataTable
                columns={[
                  { key: "n", label: "Control sample" },
                  ...["0", "1", "2"].map((s, i) => ({
                    key: `mde${s}`,
                    label: `MDE ${mde * [0.5, 1, 1.5][i]} pp`,
                    percent: true,
                  })),
                ]}
                data={curves}
              />
            }
          >
            <SeriesChart
              data={curves}
              x="n"
              xLabel="CONTROL SAMPLE SIZE"
              markers={
                calculated ? [{ x: calculated.n, label: "Current design" }] : []
              }
              series={[
                {
                  key: "mde0",
                  label: `${fmt(mde * 0.5)} pp MDE`,
                  color: "var(--control)",
                  dashed: true,
                },
                {
                  key: "mde1",
                  label: `${fmt(mde)} pp MDE`,
                  color: "var(--treatment)",
                },
                {
                  key: "mde2",
                  label: `${fmt(mde * 1.5)} pp MDE`,
                  dashed: true,
                  color: "var(--series-three)",
                },
              ]}
              percent
              reference={power / 100}
              referenceLabel={`Target ${power}%`}
            />
          </ChartCard>
          <div className="notice">
            <span className="mini-label">CROSS-PROJECT CHECK / PRICEPOINT</span>
            <h3>
              {Number.isFinite(
                num(pp.n_per_arm ?? pp.reproduced_n ?? pp.computed_n_per_arm),
              )
                ? `${fmt(pp.n_per_arm ?? pp.reproduced_n ?? pp.computed_n_per_arm, 0)} product-weeks per arm`
                : "Reproduction evidence"}
            </h3>
            <p>
              {str(
                pp.detail ?? pp.note ?? pp.documentation_gap,
                "The repository tests the earlier pricepoint calculation against its documented assumptions. See the published calibration record for the reproduction and any missing variance assumptions.",
              )}
            </p>
            <code>{str(pp.test_name, "test_reproduces_pricepoint_power")}</code>
          </div>
        </div>
      </div>
    </>
  );
}
function NumberField({
  label,
  value,
  set,
  suffix,
  min,
  max,
}: {
  label: string;
  value: number;
  set: (n: number) => void;
  suffix: string;
  min: number;
  max: number;
}) {
  return (
    <label className="number-field">
      <span>{label}</span>
      <div>
        <input
          type="number"
          min={min}
          max={max}
          step="any"
          value={value}
          onChange={(e) => set(Number(e.target.value))}
        />
        <span>{suffix}</span>
      </div>
    </label>
  );
}
