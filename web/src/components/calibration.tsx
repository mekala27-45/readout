"use client";
import { fmt, interval, num, pct, rec, Row, rows, str } from "@/lib/data";
import { Loading, PageHead, useBundle } from "./shell";
import { ChartCard, DataTable, SeriesChart } from "./charts";
export function Calibration() {
  const { bundle } = useBundle();
  if (!bundle) return <Loading />;
  const c = rec(bundle.calibration);
  const peeking = rows(c.peeking).map((r) => ({
    day: r.day,
    naive: rec(r.naive).rate,
    naive_low: rec(r.naive).low,
    naive_high: rec(r.naive).high,
    sequential: rec(r.sequential).rate,
    sequential_low: rec(r.sequential).low,
    sequential_high: rec(r.sequential).high,
  }));
  const power = rows(c.power);
  const srm = rows(c.srm);
  const cuped = rec(c.cuped);
  const delta = rec(c.delta);
  const sampleSizes = [...new Set(srm.map((r) => num(r.n_per_arm)))]
    .filter(Number.isFinite)
    .sort((a, b) => a - b);
  const drops = [...new Set(srm.map((r) => num(r.dropout)))].sort(
    (a, b) => a - b,
  );
  const srmData = drops.map((drop) => {
    const r: Row = { dropout: drop };
    sampleSizes.forEach((n) => {
      const point = srm.find((p) => p.n_per_arm === n && p.dropout === drop);
      r[`n${n}`] = point?.rate;
      r[`n${n}low`] = point?.low;
      r[`n${n}high`] = point?.high;
    });
    return r;
  });
  const cupedPoints = rows(cuped.records);
  const deltaData = [
    {
      method: "Nominal",
      rate: delta.nominal,
      low: delta.nominal,
      high: delta.nominal,
    },
    { method: "Delta", ...rec(delta.delta) },
    { method: "Naive", ...rec(delta.naive) },
  ];
  const final = peeking[peeking.length - 1] ?? {};
  const source = `Simulated calibration · seed ${fmt(c.seed, 0)} · peeking: ${fmt(c.peeking_replicates, 0)} trials · other checks: ${fmt(c.validation_replicates, 0)} trials`;
  return (
    <>
      <PageHead
        eyebrow="THE PLATFORM VALIDATES ITSELF"
        title="Measure the method. Then trust the result."
        description="Independent simulations count outcomes against known truth. The engine never grades its own answers."
      />
      <div className="calibration-banner">
        <div>
          <span className="mini-label">THE COST OF REPEATED LOOKS</span>
          <h2>Same null. Same data. Different error control.</h2>
          <p>
            Each trial has no true treatment effect. These are the fractions
            that declared a difference at least once.
          </p>
        </div>
        <div className="calibration-headline">
          <div>
            <span>
              <i className="legend-control" />
              Naive daily checks
            </span>
            <strong>
              {interval(
                {
                  rate: final.naive,
                  low: final.naive_low,
                  high: final.naive_high,
                },
                true,
              )}
            </strong>
          </div>
          <div>
            <span>
              <i />
              Sequential monitoring
            </span>
            <strong>
              {interval(
                {
                  rate: final.sequential,
                  low: final.sequential_low,
                  high: final.sequential_high,
                },
                true,
              )}
            </strong>
          </div>
        </div>
      </div>
      <ChartCard
        title="False positives accumulate when you keep looking"
        subtitle="Cumulative rejection probability under the true null, with binomial intervals"
        source={source}
        wide
        table={
          <DataTable
            columns={[
              { key: "day", label: "Daily looks" },
              { key: "naive", label: "Naive rate", percent: true },
              { key: "naive_low", label: "Naive lower", percent: true },
              { key: "naive_high", label: "Naive upper", percent: true },
              { key: "sequential", label: "Sequential rate", percent: true },
              {
                key: "sequential_low",
                label: "Sequential lower",
                percent: true,
              },
              {
                key: "sequential_high",
                label: "Sequential upper",
                percent: true,
              },
            ]}
            data={peeking}
          />
        }
      >
        <SeriesChart
          data={peeking}
          x="day"
          xLabel="NUMBER OF DAILY CHECKS"
          percent
          series={[
            {
              key: "sequential",
              label: "Sequential",
              low: "sequential_low",
              high: "sequential_high",
            },
            {
              key: "naive",
              label: "Naive daily checks",
              low: "naive_low",
              high: "naive_high",
              dashed: true,
            },
          ]}
          reference={num(c.alpha, 0.05)}
          referenceLabel={`α = ${pct(c.alpha ?? 0.05)}`}
          height={340}
        />
        <div className="chart-callout">
          Intervals quantify Monte Carlo uncertainty; a finite simulation is
          evidence about calibration, not a guarantee for every data-generating
          process.
        </div>
      </ChartCard>
      <div className="chart-grid">
        <ChartCard
          title="Does the planned power hold up?"
          subtitle="Measured detection against the planning curve"
          source={source}
          table={
            <DataTable
              columns={[
                { key: "multiple", label: "Sample multiple" },
                { key: "n_per_arm", label: "Sample / arm" },
                { key: "theoretical", label: "Theoretical", percent: true },
                { key: "rate", label: "Measured", percent: true },
                { key: "low", label: "Lower", percent: true },
                { key: "high", label: "Upper", percent: true },
              ]}
              data={power}
            />
          }
        >
          <SeriesChart
            data={power}
            x="multiple"
            xLabel="MULTIPLE OF PLANNED SAMPLE"
            percent
            series={[
              {
                key: "rate",
                label: "Empirical power",
                low: "low",
                high: "high",
              },
              { key: "theoretical", label: "Theoretical power", dashed: true },
            ]}
            reference={num(power[0]?.requested_power, 0.8)}
            referenceLabel="Target power"
          />
        </ChartCard>
        <ChartCard
          title="Will the health gate catch a defect?"
          subtitle="SRM detection as treatment dropout increases"
          source={source}
          table={
            <DataTable
              columns={[
                { key: "dropout", label: "Dropout", percent: true },
                { key: "n_per_arm", label: "Sample / arm" },
                { key: "rate", label: "Detected", percent: true },
                { key: "low", label: "Lower", percent: true },
                { key: "high", label: "Upper", percent: true },
              ]}
              data={srm}
            />
          }
        >
          <SeriesChart
            data={srmData}
            x="dropout"
            xLabel="INJECTED TREATMENT DROPOUT"
            xPercent
            percent
            series={sampleSizes.map((n, i) => ({
              key: `n${n}`,
              label: `n = ${fmt(n, 0)}`,
              low: `n${n}low`,
              high: `n${n}high`,
              dashed: i > 0,
              color: i === 2 ? "var(--series-three)" : undefined,
            }))}
          />
        </ChartCard>
        <ChartCard
          title="CUPED: precision without changing the target"
          subtitle={`Variance reduction ${interval({ estimate: cuped.empirical_variance_reduction, ci_low: cuped.empirical_low, ci_high: cuped.empirical_high }, true)}`}
          source={source}
          table={
            <DataTable
              columns={[
                { key: "replicate", label: "Seed replicate" },
                { key: "unadjusted", label: "Raw effect" },
                { key: "adjusted", label: "Adjusted effect" },
                { key: "reduction", label: "Reduction", percent: true },
              ]}
              data={cupedPoints}
            />
          }
        >
          <SeriesChart
            data={cupedPoints}
            x="replicate"
            xLabel="SIMULATION REPLICATE"
            series={[
              { key: "adjusted", label: "CUPED adjusted", scatter: true },
              {
                key: "unadjusted",
                label: "Unadjusted",
                dashed: true,
                scatter: true,
              },
            ]}
            reference={num(cuped.true_effect, 0)}
            referenceLabel="True effect"
          />
        </ChartCard>
        <ChartCard
          title="Ratio metrics need the covariance"
          subtitle="Interval coverage against a known ratio effect"
          source={source}
          table={
            <DataTable
              columns={[
                { key: "method", label: "Method" },
                { key: "rate", label: "Coverage", percent: true },
                { key: "low", label: "Lower", percent: true },
                { key: "high", label: "Upper", percent: true },
              ]}
              data={deltaData}
            />
          }
        >
          <SeriesChart
            data={deltaData}
            x="method"
            percent
            series={[
              {
                key: "rate",
                label: "Coverage",
                bar: true,
                low: "low",
                high: "high",
              },
            ]}
            reference={num(delta.nominal, 0.95)}
            referenceLabel="Nominal coverage"
          />
        </ChartCard>
      </div>
      <section className="method-footer">
        <div className="mini-label">WHAT THESE CHECKS ESTABLISH</div>
        <h2>Calibrated on stated assumptions.</h2>
        <p>
          These simulations validate the tested scenario family, sample sizes,
          observation schedule, and mixing variance. Heavy tails, dependent
          units, changes to exposure, and misspecified metrics can change the
          behavior. The canonical results include sensitivity and
          exposure-dilution records.
        </p>
        <div className="method-tags">
          <span>Known truth</span>
          <span>Seeded generation</span>
          <span>Independent counting</span>
          <span>Binomial uncertainty</span>
        </div>
      </section>
    </>
  );
}
