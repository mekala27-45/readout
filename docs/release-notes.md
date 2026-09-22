# Initial release

Readout registers immutable experiment designs, assigns units deterministically, commits health checks before analysis, and renders decisions from queried records. The release includes seeded statistical calibration, the public Cookie Cats readout, independent persistence verification, and a static web experience with live-API fallback behavior.

The statistical method limitations and empirical results are in RESULTS.md. Public API hosting remains conditional on configured Neon credentials and an existing verified Fly allowance. The static bundle is sufficient for read-only review; uploads require a running API and its write token.
