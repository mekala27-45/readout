# Health before results

The health gate tests assigned counts and exposed counts separately against the registered allocation using chi-square goodness of fit. The observed counts, expected counts, statistic, p-value, short arm and its shortage are recorded. A p-value below the registered platform blocking threshold of 0.001 blocks metric evaluation. A p-value below the conventional threshold of 0.05 warns. The tighter blocking threshold avoids turning frequent checks across many healthy experiments into constant outages; passing it does not prove the logging pipeline is correct.

A warning is visible and permits analysis. A block produces a health-only readout and a blocked decision. Zero assignments and zero exposures return `block` with `no data`, never a passing empty result. Duplicate or unrecognized randomized units are refused. Health records include a digest of the assignment and exposure population so a record from another population cannot silently unlock analysis.

Exposure coverage is exposed units divided by assigned units, both overall and per arm. Missingness is reported per metric and per exposed arm. Severe lack of primary observations blocks the run. Unequal missingness warns because complete-case comparisons may be selected. Assigned and exposed checks are repeated when a new analysis run is requested; this is a diagnostic gate, not an anytime-valid hypothesis test itself.

The sensitivity study draws a binomial assignment population, independently removes treatment records at the declared rate, and counts blocking verdicts. It varies sample size and dropout. A gate cannot reliably detect every small defect: the full sensitivity curve, including the no-defect false alarm rate, is rendered from calibration records in RESULTS.md.

The exposure dilution study explicitly generates exposure independently of assignment and potential outcomes. Only under that assumption does the assigned-population effect equal exposure rate times the effect among exposed units. Treatment-dependent exposure would require an intent-to-treat analysis or stronger causal assumptions.
