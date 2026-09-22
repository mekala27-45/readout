# True null

Source: **simulated**. No treatment effect; daily monitoring tests false positive control.
Scenario: `null`. Seed: 20260922.

Analysis recorded: 2026-09-22T15:57:10.095298+00:00. Input fingerprint: `2f1c8299b3fead8b386cdaf0d735f9ed00b7f6d03887cf9be2fee49a28c400f0`.

## Health

A p-value below the conventional SRM threshold triggers a warning; a p-value below the stricter platform threshold blocks analysis. Both outcomes remain visible. A warning permits analysis with a qualification.

| Check | Status | Statistic | p-value | Details |
| --- | --- | ---: | ---: | --- |
| srm_assigned | warn | 5.5556 | 0.018422 | treatment is short by 50.0 units versus configured allocation; block below 0.001, warn below 0.05. |
| srm_exposed | warn | 5.5556 | 0.018422 | treatment is short by 50.0 units versus configured allocation; block below 0.001, warn below 0.05. |
| exposure | pass | unavailable | unavailable | Analysis conditions on exposure. Random assignment alone does not identify this effect if treatment changes exposure. |
| missingness: value | pass | unavailable | unavailable | Missing metric values or ratio denominators by exposed arm; primary and guardrail metrics require two valid units per arm. Complete-case analysis assumes ignorable missingness. |
| missingness: quality | pass | unavailable | unavailable | Missing metric values or ratio denominators by exposed arm; primary and guardrail metrics require two valid units per arm. Complete-case analysis assumes ignorable missingness. |
| missingness: retained | pass | unavailable | unavailable | Missing metric values or ratio denominators by exposed arm; primary and guardrail metrics require two valid units per arm. Complete-case analysis assumes ignorable missingness. |

**assigned allocation:** conventional verdict **warn** at 0.050000; platform verdict **pass** at 0.001000.

| Variant | Observed units | Expected units |
| --- | ---: | ---: |
| control | 950 | 900.0 |
| treatment | 850 | 900.0 |

**exposed allocation:** conventional verdict **warn** at 0.050000; platform verdict **pass** at 0.001000.

| Variant | Observed units | Expected units |
| --- | ---: | ---: |
| control | 950 | 900.0 |
| treatment | 850 | 900.0 |

Exposure coverage: 100.00%. Control 100.00%; treatment 100.00%.
Missing value: control 0.00%; treatment 0.00%.
Missing quality: control 0.00%; treatment 0.00%.
Missing retained: control 0.00%; treatment 0.00%.

## Design

No treatment effect; daily monitoring tests false positive control.

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
| Value per exposed unit | -0.0057 [-0.2851, 0.2737] | -0.06% [-2.89%, 2.78%] | 0.968248 | 950 | 850 |

Standard error: 0.1425. Method: Welch t.
Projected power at the registered effect and achieved sample: 80.62%. This is a design projection, not observed-effect evidence.
Unit bootstrap cross check: -0.0057 [-0.2866, 0.3181]. Resamples: 400; seed: 20260922.

## Guardrails

| Metric | Absolute effect and interval | Relative effect and interval | Margin | Verdict | One-sided p-value |
| --- | --- | --- | ---: | --- | ---: |
| Quality score | 0.3064 [-0.6142, 1.2270] | 0.31% [-0.61%, 1.22%] | 5.00% | pass | 5.54e-30 |

Pass means the one-sided interval excludes degradation beyond the registered margin. Fail includes insufficient evidence of safety as well as demonstrated harm. Displayed two-sided effect intervals provide context; the verdict uses the one-sided test.

## Variance

| Estimator | Effect and interval | Standard error |
| --- | --- | ---: |
| Unadjusted | -0.0057 [-0.2851, 0.2737] | 0.1425 |
| CUPED adjusted | -0.0047 [-0.2841, 0.2747] | 0.1425 |

Descriptive variance reduction: 0.01%. Equivalent sample multiplier: 1.00. Equivalent units saved: 0. These are variance-model planning equivalents, not additional observed users. The decision uses the registered unadjusted primary. Same-sample theta has small finite-sample bias; pre-period covariates must be unaffected by treatment.

## Sequential

Normal-mixture mSPRT with estimated variance. This is an asymptotic approximation; calibration supports only the simulated regimes that were measured. Mixing variance: 0.1600.

First sequential rejection day: none. First naive rejection day: 5.

| Final day | Method | Effect | Current interval | p-value |
| ---: | --- | ---: | --- | ---: |
| 30 | Sequential monitor, running-min p | -0.0057 | [-0.4381, 0.4267] | 0.077561 |
| 30 | Naive daily comparison | -0.0057 | [-0.2849, 0.2736] | 0.968243 |

The sequential p-value retains the strongest evidence from any earlier look. The displayed band is the current, un-intersected interval, so it can include zero after an earlier sequential rejection. The naive p-value uses only the current look.

## Secondary and segments

These are exploratory comparisons. Adjusted p-values are Benjamini-Hochberg corrections within separate secondary-metric and segment families. Pointwise intervals are not simultaneous confidence intervals.

| Comparison | Effect and interval | Raw p-value | Adjusted p-value | Raw verdict | Corrected verdict |
| --- | --- | ---: | ---: | --- | --- |
| Retention | -0.0045 [-0.0498, 0.0409] | 0.847157 | 0.847157 | not significant | not significant |
| Segment desktop: Value per exposed unit | 0.4750 [-0.0952, 1.0452] | 0.102327 | 0.342392 | not significant | not significant |
| Segment mobile: Value per exposed unit | -0.3729 [-0.9075, 0.1618] | 0.171196 | 0.342392 | not significant | not significant |
| Segment new: Value per exposed unit | 0.1279 [-0.4408, 0.6965] | 0.658707 | 0.658707 | not significant | not significant |
| Segment returning: Value per exposed unit | -0.2834 [-0.8471, 0.2803] | 0.323636 | 0.431515 | not significant | not significant |

## Decision

**NO_SHIP**

**PROVISIONAL: the registered sample horizon has not been reached.** This current fixed-horizon recommendation cannot authorize a launch. Achieved units: 950 control / 850 treatment. Registered targets: 883 control / 883 treatment.

The primary interval excludes the pre-registered MDE in the favorable direction.

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
uv run readout render null
```

Restore the committed relational evidence first with `uv run python -m scripts.restore_evidence`, or regenerate every source scenario with `uv run python -m scripts.reset_and_rederive`.
