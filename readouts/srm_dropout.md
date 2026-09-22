# Treatment logging dropout

Source: **simulated**. A logging defect removes ten percent of assigned treatment records.
Scenario: `srm_dropout`. Seed: 20260922.

Analysis recorded: 2026-09-22T15:57:13.193697+00:00. Input fingerprint: `8d4f355306f1ed6ed90623612f85c8b6195c35f30b800617c6878316611482e0`.

## Health

A p-value below the conventional SRM threshold triggers a warning; a p-value below the stricter platform threshold blocks analysis. Both outcomes remain visible. A warning permits analysis with a qualification.

| Check | Status | Statistic | p-value | Details |
| --- | --- | ---: | ---: | --- |
| srm_assigned | block | 48.5359 | 3.24e-12 | treatment is short by 480.0 units versus configured allocation; block below 0.001, warn below 0.05. |
| srm_exposed | block | 48.5359 | 3.24e-12 | treatment is short by 480.0 units versus configured allocation; block below 0.001, warn below 0.05. |
| exposure | pass | unavailable | unavailable | Analysis conditions on exposure. Random assignment alone does not identify this effect if treatment changes exposure. |
| missingness: value | pass | unavailable | unavailable | Missing metric values or ratio denominators by exposed arm; primary and guardrail metrics require two valid units per arm. Complete-case analysis assumes ignorable missingness. |
| missingness: quality | pass | unavailable | unavailable | Missing metric values or ratio denominators by exposed arm; primary and guardrail metrics require two valid units per arm. Complete-case analysis assumes ignorable missingness. |
| missingness: retained | pass | unavailable | unavailable | Missing metric values or ratio denominators by exposed arm; primary and guardrail metrics require two valid units per arm. Complete-case analysis assumes ignorable missingness. |

**assigned allocation:** conventional verdict **warn** at 0.050000; platform verdict **block** at 0.001000.

| Variant | Observed units | Expected units |
| --- | ---: | ---: |
| control | 9974 | 9,494.0 |
| treatment | 9014 | 9,494.0 |

**exposed allocation:** conventional verdict **warn** at 0.050000; platform verdict **block** at 0.001000.

| Variant | Observed units | Expected units |
| --- | ---: | ---: |
| control | 9974 | 9,494.0 |
| treatment | 9014 | 9,494.0 |

Exposure coverage: 100.00%. Control 100.00%; treatment 100.00%.
Missing value: control 0.00%; treatment 0.00%.
Missing quality: control 0.00%; treatment 0.00%.
Missing retained: control 0.00%; treatment 0.00%.

## Design

A logging defect removes ten percent of assigned treatment records.

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

Analysis stopped at the health gate. No metric results were produced.

## Decision

**BLOCKED**


Health gate blocked analysis; no metric verdict is available.

Registered rule:

> Blocked health blocks analysis. A failing guardrail gives no_ship. Otherwise ship when the primary interval excludes zero in the good direction. Otherwise no_ship when the interval excludes the MDE in the good direction. Otherwise extend using the design calculator. Guardrail, ship, futility, extend is the precedence.


## Limitations

Simulations validate implementation under their stated data-generating assumptions. Exposure-conditioned comparisons require exposure independent of treatment and potential outcomes; conditioning on treatment-dependent exposure can bias causal effects. The platform does not identify interference or unmeasured post-randomization selection.

## Reproduce

```sh
uv run readout render srm_dropout
```

Restore the committed relational evidence first with `uv run python -m scripts.restore_evidence`, or regenerate every source scenario with `uv run python -m scripts.reset_and_rederive`.
