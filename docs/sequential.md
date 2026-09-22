# Sequential monitoring

The monitor implements the normal-mixture mSPRT approximation. Let `d` denote the current difference in means, `v` its estimated sampling variance, and `tau2` the pre-registered normal mixing variance. The mixture evidence against zero is

```text
log LR = -0.5 log(1 + tau2 / v) + d^2 tau2 / (2 v (v + tau2))
p_t = min(1, exp(-max_{s <= t} log LR_s))
radius_t = sqrt(v (v + tau2) / tau2 * [2 log(1 / alpha) + log(1 + tau2 / v)])
```

The displayed interval is `d +/- radius_t`. Each day's inversion is shown without intersecting earlier intervals, so the current estimate stays inside its displayed band. The p-value uses maximum evidence to date and cannot increase. The naive band is an ordinary normal fixed-horizon interval at each daily look, included to make the peeking cost visible.

With an appropriate known-variance Gaussian model the likelihood-ratio martingale construction yields anytime validity. This implementation replaces variance with cumulative sample estimates for means and proportions. It is therefore an asymptotic plug-in approximation, not a universal finite-sample guarantee. Bounded outcomes, heavy tails, early tiny samples, unequal time trends, and treatment-dependent arrival may change its operating characteristics. The calibration validates the committed distributions and checking schedule, including separate mean and Bernoulli null studies. It cannot certify every future dataset. [Johari, Pekelis and Walsh](https://arxiv.org/abs/1512.04922) provides the underlying framework.

Mixing variance is the variance of the alternative mixing distribution, on the squared absolute-effect scale. It is set in the design before results arrive. The sensitivity study reuses the same simulated experiments for each candidate mixing variance and records first-rejection-day distributions, unrejected experiments, and rejection rates. A median rejection day is explicitly conditional on rejection; it is never presented as the duration every experiment needs.

The primary fixed-horizon decision and the sequential monitor are distinct registered policies. A dashboard may display the monitor during collection; the fixed-horizon decision must not be repeatedly treated as a stopping rule. No chronological monitor is fabricated for a dataset without timestamps. Ratio metrics are outside this sequential implementation.
