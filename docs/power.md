# Planning power and MDE

The planning calculator accepts baseline, relative MDE, alpha, requested power, treatment allocation, daily total units and a standard deviation for means. The absolute effect is the magnitude of baseline times relative MDE. For means, control sample size is

```text
n_control = ceil((z_(1-alpha/2) + z_power)^2
                 * (variance_control + variance_treatment / allocation_ratio)
                 / absolute_effect^2)
allocation_ratio = treatment_fraction / control_fraction
```

Treatment sample size follows that ratio with integer rounding. Days are rounded up using the slower arm's expected arrival rate. Proportion planning accounts for the null pooled standard error and the alternative standard error separately. The calculator assumes independent units, stable variance and a two-sided normal approximation. Clustered units, interference, heavy tails, rare proportions and nonstationarity require a better design or pilot.

The MDE inversion solves for the relative effect giving requested normal-approximation power at a fixed sample. Projected power in a readout uses the registered design effect, never the observed effect as retrospective evidence that a finding is trustworthy. Statistical significance does not establish practical importance; the MDE remains visible alongside the estimate.

The pricepoint fixture preserves the original source assumptions and source script. Its effect is elasticity multiplied by `log1p(price_change)` on the log-demand scale, not elasticity multiplied by the raw percentage. The standard deviation is the measured held-out log1p-demand forecast residual scale. The reproduction test uses those assumptions and independently cross-checks statsmodels. The original design warned that serial dependence and interference need a clustered pilot. No missing variance assumption is invented.

The independent power study draws outcomes at the registered threshold, uses the production fixed-horizon test, and counts detections at the planned sample and surrounding sample multiples. Wilson binomial intervals express Monte Carlo uncertainty. Mean and Bernoulli studies both run, and all empirical values are rendered from stored calibration records.
