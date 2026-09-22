function normalCDF(x: number) {
  const t = 1 / (1 + 0.2316419 * Math.abs(x));
  const d = 0.3989422804014327 * Math.exp((-x * x) / 2);
  const p =
    1 -
    d *
      t *
      (0.31938153 +
        t *
          (-0.356563782 +
            t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))));
  return x >= 0 ? p : 1 - p;
}
function normalInverse(p: number) {
  let lo = -9,
    hi = 9;
  for (let i = 0; i < 80; i++) {
    const mid = (lo + hi) / 2;
    if (normalCDF(mid) < p) lo = mid;
    else hi = mid;
  }
  return (lo + hi) / 2;
}
export function plan(
  baseline: number,
  mde: number,
  alpha: number,
  power: number,
  allocation: number,
) {
  if (
    ![baseline, mde, alpha, power, allocation].every(Number.isFinite) ||
    baseline <= 0 ||
    baseline >= 1 ||
    mde <= 0 ||
    baseline + mde >= 1 ||
    alpha <= 0 ||
    alpha >= 1 ||
    power <= alpha ||
    power >= 1 ||
    allocation <= 0 ||
    allocation >= 1
  )
    throw new Error("Invalid proportion design");
  const p1 = baseline + mde;
  const ratio = allocation / (1 - allocation);
  const pooled = (baseline + ratio * p1) / (1 + ratio);
  const vn = pooled * (1 - pooled) * (1 + 1 / ratio);
  const va = baseline * (1 - baseline) + (p1 * (1 - p1)) / ratio;
  const z = normalInverse(1 - alpha / 2);
  const n = Math.ceil(
    (z * Math.sqrt(vn) + normalInverse(power) * Math.sqrt(va)) ** 2 / mde ** 2,
  );
  return {
    n,
    treatment: Math.ceil(n * ratio),
    achieved: (nc: number) =>
      normalCDF((Math.sqrt(nc) * mde - z * Math.sqrt(vn)) / Math.sqrt(va)) +
      normalCDF((-Math.sqrt(nc) * mde - z * Math.sqrt(vn)) / Math.sqrt(va)),
  };
}
