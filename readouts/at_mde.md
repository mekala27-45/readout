# Effect at the MDE

Source: **simulated**. Effect equals the design threshold exactly.
Scenario: `at_mde`. Seed: 20260922.

Analysis recorded: 2026-09-22T15:57:10.418025+00:00. Input fingerprint: `b0a5b3d55fadd5a0c2ba82315299f28c7bf347a97d18b25bdbb3a5e520a32b33`.

## Health

A p-value below the conventional SRM threshold triggers a warning; a p-value below the stricter platform threshold blocks analysis. Both outcomes remain visible. A warning permits analysis with a qualification.

| Check | Status | Statistic | p-value | Details |
| --- | --- | ---: | ---: | --- |
| srm_assigned | warn | 5.4383 | 0.019700 | treatment is short by 49.0 units versus configured allocation; block below 0.001, warn below 0.05. |
| srm_exposed | warn | 5.4383 | 0.019700 | treatment is short by 49.0 units versus configured allocation; block below 0.001, warn below 0.05. |
| exposure | pass | unavailable | unavailable | Analysis conditions on exposure. Random assignment alone does not identify this effect if treatment changes exposure. |
| missingness: value | pass | unavailable | unavailable | Missing metric values or ratio denominators by exposed arm; primary and guardrail metrics require two valid units per arm. Complete-case analysis assumes ignorable missingness. |
| missingness: quality | pass | unavailable | unavailable | Missing metric values or ratio denominators by exposed arm; primary and guardrail metrics require two valid units per arm. Complete-case analysis assumes ignorable missingness. |
| missingness: retained | pass | unavailable | unavailable | Missing metric values or ratio denominators by exposed arm; primary and guardrail metrics require two valid units per arm. Complete-case analysis assumes ignorable missingness. |

**assigned allocation:** conventional verdict **warn** at 0.050000; platform verdict **pass** at 0.001000.

| Variant | Observed units | Expected units |
| --- | ---: | ---: |
| control | 932 | 883.0 |
| treatment | 834 | 883.0 |

**exposed allocation:** conventional verdict **warn** at 0.050000; platform verdict **pass** at 0.001000.

| Variant | Observed units | Expected units |
| --- | ---: | ---: |
| control | 932 | 883.0 |
| treatment | 834 | 883.0 |

Exposure coverage: 100.00%. Control 100.00%; treatment 100.00%.
Missing value: control 0.00%; treatment 0.00%.
Missing quality: control 0.00%; treatment 0.00%.
Missing retained: control 0.00%; treatment 0.00%.

## Design

Effect equals the design threshold exactly.

Frozen design hash: `43527b1efe0739f4d7e7ae62701a31cfa7bb936225c4d449c70edc4336db659c`.

No changes to the registered design were recorded.

| Registered parameter | Value |
| --- | --- |
| Primary metric | value |
| Baseline | 10.0000 |
| Relative MDE | 4.00% |
| Alpha | 5.00% |
| Requested power | 80.00% |
| Planned units per arm | 883 |
| Planned days | 30 |
| Mixing variance | 0.1600 |
| control allocation | 50.00% |
| treatment allocation | 50.00% |

| Metric | Type | Favorable direction | Winsorization policy |
| --- | --- | --- | --- |
| Value per exposed unit | mean | higher_is_better | none |
| Quality score | mean | higher_is_better | none |
| Retention | proportion | higher_is_better | none |

## Primary metric

Intervals use the registered confidence level of 95.00%. Absolute effects are in metric units; relative effects are percent lift.

| Metric | Absolute effect and interval | Relative effect and interval | p-value | Control units | Treatment units |
| --- | --- | --- | ---: | ---: | ---: |
| Value per exposed unit | 0.3907 [0.1094, 0.6719] | 3.97% [1.06%, 6.88%] | 0.006505 | 932 | 834 |

Standard error: 0.1434. Method: Welch t.
Projected power at the registered effect and achieved sample: 79.88%. This is a design projection, not observed-effect evidence.
Unit bootstrap cross check: 0.3907 [0.0718, 0.6549]. Resamples: 400; seed: 20260922.

## Guardrails

| Metric | Absolute effect and interval | Relative effect and interval | Margin | Verdict | One-sided p-value |
| --- | --- | --- | ---: | --- | ---: |
| Quality score | -0.1437 [-1.0685, 0.7811] | -0.14% [-1.06%, 0.78%] | 5.00% | pass | 1.91e-25 |

Pass means the one-sided interval excludes degradation beyond the registered margin. Fail includes insufficient evidence of safety as well as demonstrated harm. Displayed two-sided effect intervals provide context; the verdict uses the one-sided test.

## Variance

| Estimator | Effect and interval | Standard error |
| --- | --- | ---: |
| Unadjusted | 0.3907 [0.1094, 0.6719] | 0.1434 |
| CUPED adjusted | 0.3955 [0.1146, 0.6764] | 0.1432 |

Descriptive variance reduction: 0.22%. Equivalent sample multiplier: 1.00. Equivalent units saved: 4. These are variance-model planning equivalents, not additional observed users. The decision uses the registered unadjusted primary. Same-sample theta has small finite-sample bias; pre-period covariates must be unaffected by treatment.

## Sequential

Normal-mixture mSPRT with estimated variance. This is an asymptotic approximation; calibration supports only the simulated regimes that were measured. Mixing variance: 0.1600.

First sequential rejection day: 23. First naive rejection day: 13.

| Final day | Method | Effect | Current interval | p-value |
| ---: | --- | ---: | --- | ---: |
| 30 | Sequential monitor, running-min p | 0.3907 | [-0.0446, 0.8259] | 0.012979 |
| 30 | Naive daily comparison | 0.3907 | [0.1096, 0.6717] | 0.006439 |

The sequential p-value retains the strongest evidence from any earlier look. The displayed band is the current, un-intersected interval, so it can include zero after an earlier sequential rejection. The naive p-value uses only the current look.

## Secondary and segments

These are exploratory comparisons. Adjusted p-values are Benjamini-Hochberg corrections within separate secondary-metric and segment families. Pointwise intervals are not simultaneous confidence intervals.

| Comparison | Effect and interval | Raw p-value | Adjusted p-value | Raw verdict | Corrected verdict |
| --- | --- | ---: | ---: | --- | --- |
| Retention | 0.0219 [-0.0239, 0.0677] | 0.348236 | 0.348236 | not significant | not significant |
| Segment desktop: Value per exposed unit | 0.5561 [0.0013, 1.1110] | 0.049455 | 0.072582 | significant | not significant |
| Segment mobile: Value per exposed unit | 0.6088 [0.0787, 1.1389] | 0.024486 | 0.072582 | significant | not significant |
| Segment new: Value per exposed unit | -0.1831 [-0.7600, 0.3938] | 0.532944 | 0.532944 | not significant | not significant |
| Segment returning: Value per exposed unit | 0.5826 [-0.0111, 1.1763] | 0.054436 | 0.072582 | not significant | not significant |

## Decision

**SHIP**

**PROVISIONAL: the registered sample horizon has not been reached.** This current fixed-horizon recommendation cannot authorize a launch. Achieved units: 932 control / 834 treatment. Registered targets: 883 control / 883 treatment.

The primary interval excludes zero in the favorable direction and all guardrails pass.

Registered rule:

> Blocked health blocks analysis. A failing guardrail gives no_ship. Otherwise ship when the primary interval excludes zero in the good direction. Otherwise no_ship when the interval excludes the MDE in the good direction. Otherwise extend using the design calculator. Guardrail, ship, futility, extend is the precedence.


## Limitations

Simulations validate implementation under their stated data-generating assumptions. Exposure-conditioned comparisons require exposure independent of treatment and potential outcomes; conditioning on treatment-dependent exposure can bias causal effects. The platform does not identify interference or unmeasured post-randomization selection.
- Exposure-conditioned analysis needs treatment-independent exposure and ignorable missingness.
- Plug-in mSPRT monitoring is an asymptotic approximation, evaluated on the committed simulated distributions.
- Segment and secondary metric families are adjusted separately using Benjamini-Hochberg; dependence assumptions still apply.
- The primary decision uses the registered fixed horizon; daily fixed-horizon decisions must not become a stopping policy.

## Reproduce

```sh
uv run readout render at_mde
```

Restore the committed relational evidence first with `uv run python -m scripts.restore_evidence`, or regenerate every source scenario with `uv run python -m scripts.reset_and_rederive`.
