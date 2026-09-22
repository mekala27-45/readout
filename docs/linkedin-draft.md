# LinkedIn draft: calibration first

I ran 1,000 simulated A/B tests with no difference between groups and checked them daily for 30 days. Naive testing called a winner in 26.3% of experiments. A calibrated normal-mixture sequential method rejected in 0.8%.

Those simulation results, with uncertainty intervals, are published alongside the code. The sequential implementation uses an estimated-variance approximation, so the measured regimes and its limits are stated explicitly.

The platform also checks randomization health before analyzing a metric, freezes experiment designs, tests guardrails, and renders a decision document from stored records. Its public Cookie Cats readout explains exactly what the dataset can and cannot support.

https://mekala27-45.github.io/readout/

https://github.com/mekala27-45/readout

Draft only; not posted.
