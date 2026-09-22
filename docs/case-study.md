# The engine does not grade itself

The difficult part of an experimentation platform is deciding when its outputs deserve trust. A significant effect can come from a broken randomization pipeline, an unstated stopping rule or treating repeated sessions as independent users. A polished chart cannot repair any of those mistakes.

Readout puts the dependencies in order. It freezes the design, records assignment and exposure, commits health checks, then analyzes and renders a decision. A blocked experiment still has an inspectable health record and document. It has no metric results to tempt a reader into making an exception.

The central design decision is the separate calibration harness. It generates samples from known parameters, passes only observations to the engine and counts the engine's conclusions. Power is measured at the detection threshold. Sequential monitoring is measured under the true null. Ratio intervals are measured against a generator with correlated sessions. CUPED's reported reduction is checked against variation of estimates across independent replicates. The result tables live in [RESULTS.md](../RESULTS.md).

The renderer is both infrastructure and product. The same query-backed, whole-file claim gate produces this repository's published results and the documents someone downloads to make a launch decision. It enforces a health-first order and displays protocol deviations. Its fidelity tests catch wrong field names that would otherwise silently hide multiple-comparison adjustments or outlier sensitivity.

The public Cookie Cats analysis demonstrates the workflow without pretending to have evidence the source does not contain. Its design is a retrospective reconstruction. Gate exposure, timestamps and pre-period covariates are unavailable, so the readout explains why some panels cannot be populated. The observed assignment split is evaluated against both warning and blocking thresholds, and the rounds metric is shown under the declared policy and without it.

Two operational lessons mattered during this build. Durability was observed through a second database connection and through a different process. The demo recording is followed by a canonical reset and complete rederivation, so browser activity does not become published experimental evidence. These patterns are reusable wherever a system makes a statistical claim or emits a decision document.
