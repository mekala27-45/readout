# Cookie Cats: moving the gate

Source: **public**. Public randomized mobile-game assignment data, analyzed retrospectively.

Analysis recorded: 2026-09-22T15:57:26.911681+00:00. Input fingerprint: `b8dd30e6dcf85e161498df86f02eea0cf28455bbb1f623687dc96b1ffa8bdfd7`.

## Health

A p-value below the conventional SRM threshold triggers a warning; a p-value below the stricter platform threshold blocks analysis. Both outcomes remain visible. A warning permits analysis with a qualification.

| Check | Status | Statistic | p-value | Details |
| --- | --- | ---: | ---: | --- |
| srm_assigned | warn | 6.9024 | 0.008608 | control is short by 394.5 units versus configured allocation; block below 0.001, warn below 0.05. |
| srm_exposed | warn | 6.9024 | 0.008608 | control is short by 394.5 units versus configured allocation; block below 0.001, warn below 0.05. |
| exposure | pass | unavailable | unavailable | Actual gate exposure is unobserved. All assigned players are included; the reported coverage is an analysis inclusion flag. |
| missingness: retention_7 | pass | unavailable | unavailable | Missing metric values or ratio denominators by exposed arm; primary and guardrail metrics require two valid units per arm. Complete-case analysis assumes ignorable missingness. |
| missingness: retention_1 | pass | unavailable | unavailable | Missing metric values or ratio denominators by exposed arm; primary and guardrail metrics require two valid units per arm. Complete-case analysis assumes ignorable missingness. |
| missingness: rounds | pass | unavailable | unavailable | Missing metric values or ratio denominators by exposed arm; primary and guardrail metrics require two valid units per arm. Complete-case analysis assumes ignorable missingness. |

**assigned allocation:** conventional verdict **warn** at 0.050000; platform verdict **pass** at 0.001000.

| Variant | Observed units | Expected units |
| --- | ---: | ---: |
| control | 44700 | 45,094.5 |
| treatment | 45489 | 45,094.5 |

**exposed allocation:** conventional verdict **warn** at 0.050000; platform verdict **pass** at 0.001000.

| Variant | Observed units | Expected units |
| --- | ---: | ---: |
| control | 44700 | 45,094.5 |
| treatment | 45489 | 45,094.5 |

Analysis inclusion: 100.00% of assigned players. Actual gate exposure was not observed; this is an assignment-effect analysis.
Missing retention_7: control 0.00%; treatment 0.00%.
Missing retention_1: control 0.00%; treatment 0.00%.
Missing rounds: control 0.00%; treatment 0.00%.

## Design

Retrospective reconstruction: moving the wait gate should improve seven-day retention by at least five percent relative, roughly one percentage point at the assumed planning baseline. This practical threshold and the rounds outlier policy were chosen with the public dataset already available; they are not historical pre-registration.

Frozen design hash: `edf6ff5688b2c86a591fd9d668d3acc177610bda7914f9df1f37492e76d7d6f9`.

This is a retrospective reconstruction registered before this platform's analysis. It is not evidence of historical pre-registration by the experiment's original team.
No changes to the registered design were recorded.

| Registered parameter | Value |
| --- | --- |
| Primary metric | retention_7 |
| Baseline | 0.1900 |
| Relative MDE | 5.00% |
| Alpha | 5.00% |
| Requested power | 80.00% |
| Planned units per arm | 27276 |
| Planned days | 14 |
| Mixing variance | 0.0001 |
| control allocation | 50.00% |
| treatment allocation | 50.00% |

| Metric | Type | Favorable direction | Winsorization policy |
| --- | --- | --- | --- |
| Seven-day retention | proportion | higher_is_better | none |
| One-day retention | proportion | higher_is_better | none |
| Rounds played | mean | higher_is_better | 99.90% |

## Primary metric

Intervals use the registered confidence level of 95.00%. Absolute effects are in metric units; relative effects are percent lift.

| Metric | Absolute effect and interval | Relative effect and interval | p-value | Control units | Treatment units |
| --- | --- | --- | ---: | ---: | ---: |
| Seven-day retention | -0.0082 [-0.0133, -0.0031] | -4.31% [-6.92%, -1.70%] | 0.001554 | 44700 | 45489 |

Standard error: 0.0026. Method: pooled two-sample z; unpooled Wald interval.
Projected power at the registered effect and achieved sample: 94.97%. This is a design projection, not observed-effect evidence.
Unit bootstrap cross check: -0.0082 [-0.0136, -0.0034]. Resamples: 400; seed: 20260922.

## Guardrails

| Metric | Absolute effect and interval | Relative effect and interval | Margin | Verdict | One-sided p-value |
| --- | --- | --- | ---: | --- | ---: |
| One-day retention | -0.0059 [-0.0124, 0.0006] | -1.32% [-2.76%, 0.12%] | 3.00% | pass | 0.010913 |
| Rounds played | -0.0956 [-1.3735, 1.1822] | -0.19% [-2.69%, 2.31%] | 5.00% | pass | 8.15e-05 |
| Rounds played without winsorization | -1.1575 [-3.7197, 1.4047] | -2.21% [-7.00%, 2.58%] | same registered margin | sensitivity only | not a separate decision |

Pass means the one-sided interval excludes degradation beyond the registered margin. Fail includes insufficient evidence of safety as well as demonstrated harm. Displayed two-sided effect intervals provide context; the verdict uses the one-sided test.
Rounds played uses a pooled upper threshold of 1,073.6240. The threshold is estimated from these outcomes; the analytic interval conditions on that threshold.

## Variance

CUPED not applicable: No complete pre-period covariate exists for this metric.

## Sequential

Sequential monitoring not applicable: No longitudinal timestamps are available, or this is a ratio metric.

## Secondary and segments

These are exploratory comparisons. Adjusted p-values are Benjamini-Hochberg corrections within separate secondary-metric and segment families. Pointwise intervals are not simultaneous confidence intervals.

| Comparison | Effect and interval | Raw p-value | Adjusted p-value | Raw verdict | Corrected verdict |
| --- | --- | ---: | ---: | --- | --- |
| Segment all: Seven-day retention | -0.0082 [-0.0133, -0.0031] | 0.001554 | 0.001554 | significant | significant |

## Decision

**NO_SHIP**


The primary interval excludes the pre-registered MDE in the favorable direction.

Registered rule:

> ship: health passes, the primary interval excludes zero in the good direction, and every guardrail passes its margin; no_ship: any guardrail fails or the primary interval excludes the MDE in the good direction; extend: unresolved with additional sample from the power calculator; blocked: health fails.


## Limitations

The source has no exposure timestamps or pre-period covariates. Allocation is observed at installation; actual gate exposure is unavailable. All randomized players are retained, so this readout estimates assignment effects. No temporal sequential monitor or CUPED result can be recovered from this file. The reconstructed design and outlier policy were chosen with public data already available.
- Exposure-conditioned analysis needs treatment-independent exposure and ignorable missingness.
- Plug-in mSPRT monitoring is an asymptotic approximation, evaluated on the committed simulated distributions.
- Segment and secondary metric families are adjusted separately using Benjamini-Hochberg; dependence assumptions still apply.
- The primary decision uses the registered fixed horizon; daily fixed-horizon decisions must not become a stopping policy.

## Reproduce

```sh
uv run readout render cookie_cats
```

Restore the committed relational evidence first with `uv run python -m scripts.restore_evidence`, or regenerate every source scenario with `uv run python -m scripts.reset_and_rederive`.
