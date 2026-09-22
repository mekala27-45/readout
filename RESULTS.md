# Measured results

Computed at 2026-09-22T15:57:28.020486+00:00 from stored relational records. Every simulation is labeled by scenario and seed in its manifest. Public Cookie Cats observations are analyzed separately. Calibration seed: 20260922; null replicates: 1000; validation replicates per setting: 500. Rate bands are Wilson Monte Carlo intervals.

## Peeking calibration

Source: simulated true null, normal unit outcomes. A detection means at least one rejection by that day.

| Daily checks | Naive false positive rate and interval | Sequential false positive rate and interval |
| ---: | --- | --- |
| 1 | 4.00% [2.95%, 5.40%] | 0.00% [0.00%, 0.38%] |
| 2 | 7.10% [5.67%, 8.86%] | 0.00% [0.00%, 0.38%] |
| 3 | 9.50% [7.83%, 11.48%] | 0.00% [0.00%, 0.38%] |
| 4 | 10.60% [8.84%, 12.66%] | 0.10% [0.02%, 0.56%] |
| 5 | 12.60% [10.69%, 14.80%] | 0.10% [0.02%, 0.56%] |
| 6 | 13.50% [11.52%, 15.76%] | 0.20% [0.05%, 0.73%] |
| 7 | 14.50% [12.45%, 16.82%] | 0.20% [0.05%, 0.73%] |
| 8 | 15.60% [13.48%, 17.98%] | 0.20% [0.05%, 0.73%] |
| 9 | 16.80% [14.61%, 19.24%] | 0.20% [0.05%, 0.73%] |
| 10 | 17.40% [15.18%, 19.87%] | 0.20% [0.05%, 0.73%] |
| 11 | 18.30% [16.03%, 20.82%] | 0.20% [0.05%, 0.73%] |
| 12 | 18.80% [16.50%, 21.34%] | 0.30% [0.10%, 0.88%] |
| 13 | 19.60% [17.26%, 22.17%] | 0.40% [0.16%, 1.02%] |
| 14 | 20.20% [17.83%, 22.80%] | 0.40% [0.16%, 1.02%] |
| 15 | 20.40% [18.02%, 23.01%] | 0.50% [0.21%, 1.17%] |
| 16 | 20.70% [18.30%, 23.32%] | 0.50% [0.21%, 1.17%] |
| 17 | 22.00% [19.54%, 24.67%] | 0.60% [0.28%, 1.30%] |
| 18 | 22.20% [19.73%, 24.88%] | 0.60% [0.28%, 1.30%] |
| 19 | 22.50% [20.02%, 25.19%] | 0.60% [0.28%, 1.30%] |
| 20 | 22.70% [20.21%, 25.40%] | 0.70% [0.34%, 1.44%] |
| 21 | 23.00% [20.50%, 25.71%] | 0.70% [0.34%, 1.44%] |
| 22 | 23.20% [20.69%, 25.92%] | 0.70% [0.34%, 1.44%] |
| 23 | 23.60% [21.07%, 26.33%] | 0.70% [0.34%, 1.44%] |
| 24 | 24.30% [21.74%, 27.05%] | 0.70% [0.34%, 1.44%] |
| 25 | 24.80% [22.22%, 27.57%] | 0.70% [0.34%, 1.44%] |
| 26 | 25.00% [22.42%, 27.78%] | 0.70% [0.34%, 1.44%] |
| 27 | 25.30% [22.70%, 28.09%] | 0.70% [0.34%, 1.44%] |
| 28 | 25.60% [22.99%, 28.39%] | 0.70% [0.34%, 1.44%] |
| 29 | 25.80% [23.18%, 28.60%] | 0.70% [0.34%, 1.44%] |
| 30 | 26.30% [23.67%, 29.12%] | 0.80% [0.41%, 1.57%] |

Independent Bernoulli null validation, day 30: naive **28.50% [25.79%, 31.38%]**, sequential **1.10% [0.62%, 1.96%]**. The plug-in mSPRT is an asymptotic approximation; these measurements do not establish a universal finite-sample guarantee.

## Empirical power

Source: simulated effect exactly at the registered MDE. Counts come from engine rejections, not from the calculator's own formula.

| Design multiple | Sample per arm | Empirical power and interval | Theoretical power |
| ---: | ---: | --- | ---: |
| 0.5 | 442 | 49.20% [44.84%, 53.57%] | 50.89% |
| 0.75 | 663 | 68.20% [63.99%, 72.13%] | 68.00% |
| 1 | 883 | 80.00% [76.27%, 83.27%] | 80.00% |
| 1.5 | 1325 | 93.60% [91.10%, 95.43%] | 92.95% |
| 2 | 1766 | 97.80% [96.10%, 98.77%] | 97.74% |

The separate Bernoulli validation uses the same sample-size multiples:

| Design multiple | Sample per arm | Empirical power and interval | Theoretical power |
| ---: | ---: | --- | ---: |
| 0.5 | 1195 | 51.80% [47.42%, 56.15%] | 50.84% |
| 0.75 | 1792 | 70.00% [65.84%, 73.85%] | 67.95% |
| 1 | 2389 | 79.80% [76.06%, 83.09%] | 80.00% |
| 1.5 | 3584 | 94.20% [91.79%, 95.93%] | 92.95% |
| 2 | 4778 | 98.00% [96.36%, 98.91%] | 97.74% |

## SRM sensitivity

Source: simulated assignment dropout. Detection means crossing the platform blocking threshold, not the warning threshold.

| Initial sample per arm | Treatment dropout | Blocking probability and interval |
| ---: | ---: | --- |
| 1000 | 0.00% | 0.40% [0.11%, 1.45%] |
| 1000 | 1.00% | 0.00% [0.00%, 0.76%] |
| 1000 | 2.00% | 0.20% [0.04%, 1.12%] |
| 1000 | 3.00% | 0.20% [0.04%, 1.12%] |
| 1000 | 4.00% | 0.60% [0.20%, 1.75%] |
| 1000 | 5.00% | 1.40% [0.68%, 2.86%] |
| 1000 | 10.00% | 19.80% [16.54%, 23.52%] |
| 10000 | 0.00% | 0.00% [0.00%, 0.76%] |
| 10000 | 1.00% | 0.80% [0.31%, 2.04%] |
| 10000 | 2.00% | 2.00% [1.09%, 3.64%] |
| 10000 | 3.00% | 9.60% [7.32%, 12.50%] |
| 10000 | 4.00% | 31.40% [27.49%, 35.60%] |
| 10000 | 5.00% | 64.00% [59.70%, 68.09%] |
| 10000 | 10.00% | 100.00% [99.24%, 100.00%] |
| 100000 | 0.00% | 0.20% [0.04%, 1.12%] |
| 100000 | 1.00% | 15.00% [12.14%, 18.40%] |
| 100000 | 2.00% | 86.80% [83.55%, 89.49%] |
| 100000 | 3.00% | 100.00% [99.24%, 100.00%] |
| 100000 | 4.00% | 100.00% [99.24%, 100.00%] |
| 100000 | 5.00% | 100.00% [99.24%, 100.00%] |
| 100000 | 10.00% | 100.00% [99.24%, 100.00%] |

## Pricepoint reproduction

| Assumption or result | Stored value |
| --- | --- |
| Assumed elasticity | -1.50 |
| Price change | 10.00% |
| Effect magnitude | 0.14296527 |
| Effect scale | log demand, using elasticity times log1p price change |
| Residual standard deviation | 1.03269289 |
| Alpha | 5.00% |
| Requested power | 80.00% |
| Published sample per arm | 820 |
| Reproduced sample per arm | 820 |

Source: `experiments/pricepoint/source-plan_experiment.py`, source commit `e1a1db84249c562f895de23d5ec6627675ee1147`. No missing variance assumption: sigma is the measured held-out log1p-demand forecast residual standard deviation. Serial dependence and interference still require a clustered pilot. The reproduction checks arithmetic, not identification or independence. Test: `test_reproduces_pricepoint_power`.

## CUPED recovery

Source: simulated correlated pre-period values. The empirical variance reduction below compares the spread of effect estimates across independent experiments. Its paired bootstrap interval does not use the engine's variance formula.

| Quantity | Estimate and uncertainty or registered truth |
| --- | --- |
| True effect | 0.4000 |
| Mean adjusted effect across replicates | 0.3991 [0.3897, 0.4085] |
| Expected variance reduction from squared correlation | 64.00% |
| Empirical variance reduction across replicates | 61.04% [55.08%, 66.40%] |
| Mean engine-reported reduction, descriptive | 63.90% [63.75%, 64.06%] |

Bootstrap draws: 2000. The full replicate-level estimates remain in the committed results bundle for the recovery distribution chart.

## Ratio interval coverage

Source: simulated sessions correlated within randomized users. Delta intervals preserve the user as the sampling unit; the naive comparison treats sessions as independent.

| Method | Coverage and Monte Carlo interval |
| --- | --- |
| Registered nominal target | 95.00% |
| Unit delta method | 94.80% [92.49%, 96.43%] |
| Naive independent sessions | 70.80% [66.67%, 74.61%] |

True effect: 0.0200; randomized units per arm: 2000; within-user correlation: 0.25. Ratio power planning and ratio sequential monitoring are outside this implementation.

## Exposure dilution

Source: simulated exposure independent of assignment and potential outcomes. This specific generator supports the exposure-conditioned comparison; arbitrary real exposure does not.

| Estimand | Expected effect | Observed effect and interval | Control units | Treatment units |
| --- | ---: | --- | ---: | ---: |
| All assigned units | 0.2400 | 0.2221 [0.1848, 0.2593] | 50113 | 49887 |
| Exposed units | 0.4000 | 0.3843 [0.3361, 0.4324] | 29979 | 29808 |

Exposure rate: 60.00%. Seed: 20261722. Exposure generated independently of assignment, pre-period value and potential outcomes.

## Mixing-variance sensitivity

Source: simulated effect at the MDE, sharing the same experiments across mixing settings. Day summaries are conditional on rejection; unrejected experiments remain in the denominator of the rejection rate.

| Mixing variance | Rejection rate and interval | First rejection day: median [interquartile range] | Not rejected |
| ---: | --- | ---: | ---: |
| 0.0160 | 19.20% [15.99%, 22.88%] | 26.0 [23.0, 29.0] | 404 |
| 0.1600 | 53.40% [49.02%, 57.73%] | 19.0 [13.0, 24.0] | 233 |
| 1.6000 | 46.80% [42.47%, 51.18%] | 18.0 [11.0, 23.0] | 266 |

The bundle retains the full first-rejection-day histogram for every setting.

## Decisions across sources

| Experiment | Source | Health | Decision | Primary effect and interval |
| --- | --- | --- | --- | --- |
| at_mde | simulated | warn, pass | ship (provisional) | 0.3907 [0.1094, 0.6719] |
| cookie_cats | public | warn, pass | no_ship | -0.0082 [-0.0133, -0.0031] |
| correlated_pre | simulated | pass | ship | 0.4442 [0.2275, 0.6610] |
| guardrail_hit | simulated | pass | no_ship | 0.7180 [0.5682, 0.8679] |
| heterogeneous | simulated | pass | ship | 0.2844 [0.1512, 0.4177] |
| null | simulated | warn, pass | no_ship (provisional) | -0.0057 [-0.2851, 0.2737] |
| ratio_metric | simulated | warn, pass | ship (provisional) | 0.0275 [0.0093, 0.0458] |
| srm_dropout | simulated | block, pass | blocked | blocked; no metrics |

## Cookie Cats

srm_assigned: conventional **warn**, platform **pass**, p = 0.008608. Observed {"control": 44700, "treatment": 45489}, expected {"control": 45094.5, "treatment": 45094.5}. The platform records the conventional warning while reserving blocking for stronger mismatch evidence.
srm_exposed: conventional **warn**, platform **pass**, p = 0.008608. Observed {"control": 44700, "treatment": 45489}, expected {"control": 45094.5, "treatment": 45094.5}. The platform records the conventional warning while reserving blocking for stronger mismatch evidence.

Primary retention effect: **-0.0082 [-0.0133, -0.0031]**, relative **-4.31% [-6.92%, -1.70%]**. Decision: **no_ship**.

| Metric | Declared policy effect and interval | Without policy effect and interval |
| --- | --- | --- |
| Rounds played | -0.0956 [-1.3735, 1.1822] | -1.1575 [-3.7197, 1.4047] |

| Source diagnostic | Stored value |
| --- | --- |
| Rows | 90189 |
| Largest rounds value | 49854 |
| Declared pooled rounds threshold | 1,073.6240 |
| Retrieved at | 2026-09-22T15:14:28.059482+00:00 |
| Source | https://www.kaggle.com/datasets/mursideyarkin/mobile-games-ab-testing-cookie-cats |
| SHA-256 | `5ab54d761fbddcd50de7b88e4eaf7837cba4569474f50c043a4d17ee342c46bd` |

Actual gate exposure is unavailable. All randomized installations are retained; exposed=True is a computational inclusion flag, not an observed gate exposure. The description credits DataCamp and Tactile Entertainment but states no additional license grant. The data is not covered by this repository's Apache license.

## Assignment evidence

Deterministic IDs checked: 100000. Histogram population: 10000. Independent-salt assignment correlation: 0.002442.
Allocation goodness-of-fit p-value: 0.859440; verdict **pass**. Observed control: 50028; treatment: 49972.

## Limitations

Monte Carlo confidence bands measure sampling uncertainty in the measured scenarios. They do not prove validity on all outcome distributions. Estimated-variance mSPRT is approximate. The normal power approximation can differ from finite-sample Welch inference. The public experiment was not prospectively pre-registered here, has no pre-period or temporal data, and lacks observed gate exposure. Its winsorization policy is a retrospective sensitivity analysis. The listed Kaggle license does not specify a general redistribution grant. The software's Apache license does not apply to that dataset.

The exposed-unit estimand needs treatment-independent exposure and ignorable missingness. Fixed-horizon decisions must respect the registered horizon. Exploratory secondary metrics and segments are separate correction families; their pointwise intervals are not adjusted confidence intervals. Production authentication, upload isolation between users, workload limits beyond the demo cap, interference detection and non-randomized causal identification are outside this build. Optional stretch modules were deferred.
