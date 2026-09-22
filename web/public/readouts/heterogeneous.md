# One responsive segment

Source: **simulated**. Only the returning segment has a treatment effect.
Scenario: `heterogeneous`. Seed: 20260922.

Analysis recorded: 2026-09-22T15:57:16.741434+00:00. Input fingerprint: `312eaa25b36c177b687ea4133c03f83c66000a1693ab2e8b953f6f2411efdfe0`.

## Health

A p-value below the conventional SRM threshold triggers a warning; a p-value below the stricter platform threshold blocks analysis. Both outcomes remain visible. A warning permits analysis with a qualification.

| Check | Status | Statistic | p-value | Details |
| --- | --- | ---: | ---: | --- |
| srm_assigned | pass | 1.1045 | 0.293281 | treatment is short by 47.0 units versus configured allocation; block below 0.001, warn below 0.05. |
| srm_exposed | pass | 1.1045 | 0.293281 | treatment is short by 47.0 units versus configured allocation; block below 0.001, warn below 0.05. |
| exposure | pass | unavailable | unavailable | Analysis conditions on exposure. Random assignment alone does not identify this effect if treatment changes exposure. |
| missingness: value | pass | unavailable | unavailable | Missing metric values or ratio denominators by exposed arm; primary and guardrail metrics require two valid units per arm. Complete-case analysis assumes ignorable missingness. |
| missingness: quality | pass | unavailable | unavailable | Missing metric values or ratio denominators by exposed arm; primary and guardrail metrics require two valid units per arm. Complete-case analysis assumes ignorable missingness. |
| missingness: retained | pass | unavailable | unavailable | Missing metric values or ratio denominators by exposed arm; primary and guardrail metrics require two valid units per arm. Complete-case analysis assumes ignorable missingness. |

**assigned allocation:** conventional verdict **pass** at 0.050000; platform verdict **pass** at 0.001000.

| Variant | Observed units | Expected units |
| --- | ---: | ---: |
| control | 4047 | 4,000.0 |
| treatment | 3953 | 4,000.0 |

**exposed allocation:** conventional verdict **pass** at 0.050000; platform verdict **pass** at 0.001000.

| Variant | Observed units | Expected units |
| --- | ---: | ---: |
| control | 4047 | 4,000.0 |
| treatment | 3953 | 4,000.0 |

Exposure coverage: 100.00%. Control 100.00%; treatment 100.00%.
Missing value: control 0.00%; treatment 0.00%.
Missing quality: control 0.00%; treatment 0.00%.
Missing retained: control 0.00%; treatment 0.00%.

## Design

Only the returning segment has a treatment effect.

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
| Value per exposed unit | 0.2844 [0.1512, 0.4177] | 2.85% [1.50%, 4.21%] | 2.9e-05 | 4047 | 3953 |

Standard error: 0.0680. Method: Welch t.
Projected power at the registered effect and achieved sample: 100.00%. This is a design projection, not observed-effect evidence.
Unit bootstrap cross check: 0.2844 [0.1540, 0.4234]. Resamples: 400; seed: 20260922.

## Guardrails

| Metric | Absolute effect and interval | Relative effect and interval | Margin | Verdict | One-sided p-value |
| --- | --- | --- | ---: | --- | ---: |
| Quality score | -0.4167 [-0.8585, 0.0251] | -0.42% [-0.86%, 0.02%] | 5.00% | pass | 3.49e-93 |

Pass means the one-sided interval excludes degradation beyond the registered margin. Fail includes insufficient evidence of safety as well as demonstrated harm. Displayed two-sided effect intervals provide context; the verdict uses the one-sided test.

## Variance

| Estimator | Effect and interval | Standard error |
| --- | --- | ---: |
| Unadjusted | 0.2844 [0.1512, 0.4177] | 0.0680 |
| CUPED adjusted | 0.3136 [0.1863, 0.4409] | 0.0649 |

Descriptive variance reduction: 8.76%. Equivalent sample multiplier: 1.10. Equivalent units saved: 701. These are variance-model planning equivalents, not additional observed users. The decision uses the registered unadjusted primary. Same-sample theta has small finite-sample bias; pre-period covariates must be unaffected by treatment.

## Sequential

Normal-mixture mSPRT with estimated variance. This is an asymptotic approximation; calibration supports only the simulated regimes that were measured. Mixing variance: 0.1600.

First sequential rejection day: 14. First naive rejection day: 2.

| Final day | Method | Effect | Current interval | p-value |
| ---: | --- | ---: | --- | ---: |
| 30 | Sequential monitor, running-min p | 0.2844 | [0.0712, 0.4977] | 0.001207 |
| 30 | Naive daily comparison | 0.2844 | [0.1512, 0.4177] | 2.87e-05 |

The sequential p-value retains the strongest evidence from any earlier look. The displayed band is the current, un-intersected interval, so it can include zero after an earlier sequential rejection. The naive p-value uses only the current look.

## Secondary and segments

These are exploratory comparisons. Adjusted p-values are Benjamini-Hochberg corrections within separate secondary-metric and segment families. Pointwise intervals are not simultaneous confidence intervals.

| Comparison | Effect and interval | Raw p-value | Adjusted p-value | Raw verdict | Corrected verdict |
| --- | --- | ---: | ---: | --- | --- |
| Retention | 0.0155 [-0.0061, 0.0370] | 0.160290 | 0.160290 | not significant | not significant |
| Segment desktop: Value per exposed unit | -0.0711 [-0.3409, 0.1986] | 0.605085 | 0.605085 | not significant | not significant |
| Segment mobile: Value per exposed unit | 0.2243 [-0.0403, 0.4889] | 0.096510 | 0.193020 | not significant | not significant |
| Segment new: Value per exposed unit | -0.1827 [-0.4474, 0.0819] | 0.175902 | 0.234535 | not significant | not significant |
| Segment returning: Value per exposed unit | 1.1530 [0.8919, 1.4141] | 9.57e-18 | 3.83e-17 | significant | significant |

## Decision

**SHIP**


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
uv run readout render heterogeneous
```

Restore the committed relational evidence first with `uv run python -m scripts.restore_evidence`, or regenerate every source scenario with `uv run python -m scripts.reset_and_rederive`.
