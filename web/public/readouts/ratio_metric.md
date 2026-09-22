# Correlated sessions

Source: **simulated**. Beta-binomial sessions share a user propensity; users remain the unit of inference.
Scenario: `ratio_metric`. Seed: 20260922.

Analysis recorded: 2026-09-22T15:57:15.395808+00:00. Input fingerprint: `64885fa388ec9c0ae353046490894683bd91c78967aac595566c290bc042705d`.

## Health

A p-value below the conventional SRM threshold triggers a warning; a p-value below the stricter platform threshold blocks analysis. Both outcomes remain visible. A warning permits analysis with a qualification.

| Check | Status | Statistic | p-value | Details |
| --- | --- | ---: | ---: | --- |
| srm_assigned | warn | 5.3290 | 0.020973 | treatment is short by 73.0 units versus configured allocation; block below 0.001, warn below 0.05. |
| srm_exposed | warn | 5.3290 | 0.020973 | treatment is short by 73.0 units versus configured allocation; block below 0.001, warn below 0.05. |
| exposure | pass | unavailable | unavailable | Analysis conditions on exposure. Random assignment alone does not identify this effect if treatment changes exposure. |
| missingness: conversion_per_session | pass | unavailable | unavailable | Missing metric values or ratio denominators by exposed arm; primary and guardrail metrics require two valid units per arm. Complete-case analysis assumes ignorable missingness. |
| missingness: quality | pass | unavailable | unavailable | Missing metric values or ratio denominators by exposed arm; primary and guardrail metrics require two valid units per arm. Complete-case analysis assumes ignorable missingness. |
| missingness: retained | pass | unavailable | unavailable | Missing metric values or ratio denominators by exposed arm; primary and guardrail metrics require two valid units per arm. Complete-case analysis assumes ignorable missingness. |

**assigned allocation:** conventional verdict **warn** at 0.050000; platform verdict **pass** at 0.001000.

| Variant | Observed units | Expected units |
| --- | ---: | ---: |
| control | 2073 | 2,000.0 |
| treatment | 1927 | 2,000.0 |

**exposed allocation:** conventional verdict **warn** at 0.050000; platform verdict **pass** at 0.001000.

| Variant | Observed units | Expected units |
| --- | ---: | ---: |
| control | 2073 | 2,000.0 |
| treatment | 1927 | 2,000.0 |

Exposure coverage: 100.00%. Control 100.00%; treatment 100.00%.
Missing conversion_per_session: control 0.00%; treatment 0.00%.
Missing quality: control 0.00%; treatment 0.00%.
Missing retained: control 0.00%; treatment 0.00%.

## Design

Beta-binomial sessions share a user propensity; users remain the unit of inference.

Frozen design hash: `3574432d060c5280a4e2cd4b64f5d63bf812a06d1f182f0e081813686c5edb4e`.

No changes to the registered design were recorded.

| Registered parameter | Value |
| --- | --- |
| Primary metric | conversion_per_session |
| Baseline | 0.4000 |
| Relative MDE | 5.00% |
| Alpha | 5.00% |
| Requested power | 80.00% |
| Planned units per arm | 2000 |
| Planned days | 30 |
| Mixing variance | 0.1600 |
| control allocation | 50.00% |
| treatment allocation | 50.00% |

| Metric | Type | Favorable direction | Winsorization policy |
| --- | --- | --- | --- |
| Conversion per session | ratio | higher_is_better | none |
| Quality score | mean | higher_is_better | none |
| Retention | proportion | higher_is_better | none |

## Primary metric

Intervals use the registered confidence level of 95.00%. Absolute effects are in metric units; relative effects are percent lift.

| Metric | Absolute effect and interval | Relative effect and interval | p-value | Control units | Treatment units |
| --- | --- | --- | ---: | ---: | ---: |
| Conversion per session | 0.0275 [0.0093, 0.0458] | 6.90% [2.18%, 11.63%] | 0.003095 | 2073 | 1927 |

Standard error: 0.0093. Method: unit delta method.

## Guardrails

| Metric | Absolute effect and interval | Relative effect and interval | Margin | Verdict | One-sided p-value |
| --- | --- | --- | ---: | --- | ---: |
| Quality score | 0.4255 [-0.1867, 1.0376] | 0.43% [-0.19%, 1.04%] | 5.00% | pass | 5.03e-67 |

Pass means the one-sided interval excludes degradation beyond the registered margin. Fail includes insufficient evidence of safety as well as demonstrated harm. Displayed two-sided effect intervals provide context; the verdict uses the one-sided test.

## Variance

CUPED not applicable: No complete pre-period covariate exists for this metric.

## Sequential

Sequential monitoring not applicable: No longitudinal timestamps are available, or this is a ratio metric.

## Secondary and segments

These are exploratory comparisons. Adjusted p-values are Benjamini-Hochberg corrections within separate secondary-metric and segment families. Pointwise intervals are not simultaneous confidence intervals.

| Comparison | Effect and interval | Raw p-value | Adjusted p-value | Raw verdict | Corrected verdict |
| --- | --- | ---: | ---: | --- | --- |
| Retention | 0.0228 [-0.0076, 0.0532] | 0.141186 | 0.141186 | not significant | not significant |
| Segment desktop: Conversion per session | 0.0382 [0.0012, 0.0751] | 0.042882 | 0.085764 | significant | not significant |
| Segment mobile: Conversion per session | 0.0175 [-0.0200, 0.0550] | 0.360660 | 0.480880 | not significant | not significant |
| Segment new: Conversion per session | 0.0587 [0.0239, 0.0934] | 0.000951 | 0.003804 | significant | significant |
| Segment returning: Conversion per session | -0.0065 [-0.0432, 0.0303] | 0.730544 | 0.730544 | not significant | not significant |

## Decision

**SHIP**

**PROVISIONAL: the registered sample horizon has not been reached.** This current fixed-horizon recommendation cannot authorize a launch. Achieved units: 2073 control / 1927 treatment. Registered targets: 2000 control / 2000 treatment.

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
uv run readout render ratio_metric
```

Restore the committed relational evidence first with `uv run python -m scripts.restore_evidence`, or regenerate every source scenario with `uv run python -m scripts.reset_and_rederive`.
