import test from "node:test";
import assert from "node:assert/strict";
import { plan } from "../src/lib/power.ts";

test("browser planner matches independent SciPy backend reference values", () => {
  for (const [baseline, power, allocation, control, treatment] of [
    [0.2, 0.8, 0.5, 6510, 6510],
    [0.2, 0.8, 0.3, 10788, 4624],
    [0.5, 0.9, 0.5, 13127, 13127],
  ]) {
    const actual = plan(baseline, 0.02, 0.05, power, allocation);
    assert.equal(actual.n, control);
    assert.equal(actual.treatment, treatment);
    assert.ok(Math.abs(actual.achieved(actual.n) - power) < 0.001);
  }
});
test("larger effects need less sample and greater power needs more", () => {
  const base = plan(0.2, 0.02, 0.05, 0.8, 0.5);
  assert.ok(plan(0.2, 0.04, 0.05, 0.8, 0.5).n < base.n);
  assert.ok(plan(0.2, 0.02, 0.05, 0.9, 0.5).n > base.n);
  assert.ok(base.achieved(base.n * 2) > base.achieved(base.n));
});
test("planner refuses invalid probabilities and effects", () => {
  for (const args of [
    [0.2, 0, 0.05, 0.8, 0.5],
    [0.99, 0.02, 0.05, 0.8, 0.5],
    [0.2, 0.02, 0, 0.8, 0.5],
    [0.2, 0.02, 0.05, 0.8, 0],
    [NaN, 0.02, 0.05, 0.8, 0.5],
  ])
    assert.throws(
      () => plan(args[0], args[1], args[2], args[3], args[4]),
      /Invalid/,
    );
});
