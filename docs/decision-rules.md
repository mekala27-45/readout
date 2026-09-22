# Decision rules

The registered rule is stored as data and quoted verbatim in each readout. Its implemented precedence resolves the overlap between a statistically significant small effect and an interval that excludes the MDE:

1. Any blocking health verdict produces `blocked`, with no metric analysis.
2. Any guardrail that fails to demonstrate non-inferiority produces `no_ship`.
3. Otherwise, a primary interval excluding zero in the favorable direction produces `ship`.
4. Otherwise, a primary interval whose favorable upper endpoint is below the MDE produces `no_ship`.
5. Otherwise, the recommendation is `extend`.

A guardrail uses a one-sided relative-lift interval in the favorable direction and passes only if its lower endpoint is above the negative registered margin. Failing this test includes both demonstrated harm and insufficient evidence of safety. The readout says which criterion was used rather than calling every uncertain guardrail harmful. Requiring every guardrail to pass is an intersection-union safety rule.

The default gives statistical improvement precedence over the MDE futility rule. It can therefore ship an effect smaller than the MDE. A team that requires practical superiority should register a different policy before launch; changing the prose after observing results is a protocol deviation, not an implementation of a new test. The current engine implements the default deterministic policy; custom freeform text is descriptive and must not be mistaken for executable policy code.

The extension calculation uses the smaller of the registered MDE and the observed effect magnitude, bounded away from zero at half the MDE, to provide a planning heuristic. It returns at least a modest increment when the target sample has already been reached. This is not a license for repeated fixed-horizon testing. Continuing requires a new stated horizon or use of the registered sequential method. A fixed-horizon decision is only interpretable at its pre-specified horizon; the demo exposes the rule's current recommendation but does not create an automatic launch action.

The test suite exercises every branch, both benefit directions, the empty-health refusal and the scenario where the primary alone would ship while a guardrail prevents launch. The renderer preserves the preregistered design hash and flags later design changes.
