# Primary gain, guardrail harm

Source: **simulated**. The primary improves but the safety metric degrades beyond its margin.
Scenario: `guardrail_hit`. Seed: 20260922.

Analysis recorded: 2026-09-22T15:57:14.134402+00:00. Input fingerprint: `c499c5acaae30e48fa5308f9b9010da4b67822b3e5734b03773cad4764acab67`.

## Health

A p-value below the conventional SRM threshold triggers a warning; a p-value below the stricter platform threshold blocks analysis. Both outcomes remain visible. A warning permits analysis with a qualification.

| Check | Status | Statistic | p-value | Details |
| --- | --- | ---: | ---: | --- |
| srm_assigned | pass | 1.4107 | 0.234946 | treatment is short by 46.0 units versus configured allocation; block below 0.001, warn below 0.05. |
| srm_exposed | pass | 1.4107 | 0.234946 | treatment is short by 46.0 units versus configured allocation; block below 0.001, warn below 0.05. |
| exposure | pass | unavailable | unavailable | Analysis conditions on exposure. Random assignment alone does not identify this effect if treatment changes exposure. |
| missingness: value | pass | unavailable | unavailable | Missing metric values or ratio denominators by exposed arm; primary and guardrail metrics require two valid units per arm. Complete-case analysis assumes ignorable missingness. |
| missingness: quality | pass | unavailable | unavailable | Missing metric values or ratio denominators by exposed arm; primary and guardrail metrics require two valid units per arm. Complete-case analysis assumes ignorable missingness. |
| missingness: retained | pass | unavailable | unavailable | Missing metric values or ratio denominators by exposed arm; primary and guardrail metrics require two valid units per arm. Complete-case analysis assumes ignorable missingness. |

**assigned allocation:** conventional verdict **pass** at 0.050000; platform verdict **pass** at 0.001000.

| Variant | Observed units | Expected units |
| --- | ---: | ---: |
| control | 3046 | 3,000.0 |
| treatment | 2954 | 3,000.0 |

**exposed allocation:** conventional verdict **pass** at 0.050000; platform verdict **pass** at 0.001000.

| Variant | Observed units | Expected units |
| --- | ---: | ---: |
| control | 3046 | 3,000.0 |
| treatment | 2954 | 3,000.0 |

Exposure coverage: 100.00%. Control 100.00%; treatment 100.00%.
Missing value: control 0.00%; treatment 0.00%.
Missing quality: control 0.00%; treatment 0.00%.
Missing retained: control 0.00%; treatment 0.00%.

## Design

The primary improves but the safety metric degrades beyond its margin.

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
| Value per exposed unit | 0.7180 [0.5682, 0.8679] | 7.17% [5.62%, 8.72%] | 8.04e-21 | 3046 | 2954 |

Standard error: 0.0764. Method: Welch t.
Projected power at the registered effect and achieved sample: 99.93%. This is a design projection, not observed-effect evidence.
Unit bootstrap cross check: 0.7180 [0.5680, 0.8791]. Resamples: 400; seed: 20260922.

## Guardrails

| Metric | Absolute effect and interval | Relative effect and interval | Margin | Verdict | One-sided p-value |
| --- | --- | --- | ---: | --- | ---: |
| Quality score | -9.9188 [-10.4308, -9.4068] | -9.92% [-10.41%, -9.44%] | 5.00% | fail | 1.000000 |

Pass means the one-sided interval excludes degradation beyond the registered margin. Fail includes insufficient evidence of safety as well as demonstrated harm. Displayed two-sided effect intervals provide context; the verdict uses the one-sided test.

## Variance

| Estimator | Effect and interval | Standard error |
| --- | --- | ---: |
| Unadjusted | 0.7180 [0.5682, 0.8679] | 0.0764 |
| CUPED adjusted | 0.7177 [0.5678, 0.8675] | 0.0764 |

Descriptive variance reduction: 0.02%. Equivalent sample multiplier: 1.00. Equivalent units saved: 1. These are variance-model planning equivalents, not additional observed users. The decision uses the registered unadjusted primary. Same-sample theta has small finite-sample bias; pre-period covariates must be unaffected by treatment.

## Sequential

Normal-mixture mSPRT with estimated variance. This is an asymptotic approximation; calibration supports only the simulated regimes that were measured. Mixing variance: 0.1600.

First sequential rejection day: 1. First naive rejection day: 1.

| Final day | Method | Effect | Current interval | p-value |
| ---: | --- | ---: | --- | ---: |
| 30 | Sequential monitor, running-min p | 0.7180 | [0.4802, 0.9558] | 1.74e-18 |
| 30 | Naive daily comparison | 0.7180 | [0.5682, 0.8678] | 5.78e-21 |

The sequential p-value retains the strongest evidence from any earlier look. The displayed band is the current, un-intersected interval, so it can include zero after an earlier sequential rejection. The naive p-value uses only the current look.

## Secondary and segments

These are exploratory comparisons. Adjusted p-values are Benjamini-Hochberg corrections within separate secondary-metric and segment families. Pointwise intervals are not simultaneous confidence intervals.

| Comparison | Effect and interval | Raw p-value | Adjusted p-value | Raw verdict | Corrected verdict |
| --- | --- | ---: | ---: | --- | --- |
| Retention | 0.0144 [-0.0104, 0.0392] | 0.256017 | 0.256017 | not significant | not significant |
| Segment desktop: Value per exposed unit | 0.6375 [0.3381, 0.9369] | 3.13e-05 | 3.13e-05 | significant | significant |
| Segment mobile: Value per exposed unit | 0.7900 [0.4846, 1.0954] | 4.38e-07 | 1.75e-06 | significant | significant |
| Segment new: Value per exposed unit | 0.7223 [0.4304, 1.0142] | 1.34e-06 | 2.68e-06 | significant | significant |
| Segment returning: Value per exposed unit | 0.7265 [0.4244, 1.0287] | 2.62e-06 | 3.49e-06 | significant | significant |

## Decision

**NO_SHIP**


At least one guardrail did not demonstrate non-inferiority at its pre-registered margin.

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
uv run readout render guardrail_hit
```

Restore the committed relational evidence first with `uv run python -m scripts.restore_evidence`, or regenerate every source scenario with `uv run python -m scripts.reset_and_rederive`.
