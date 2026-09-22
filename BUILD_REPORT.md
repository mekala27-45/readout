# Delivery record

## File tree

```text
readout/
  .dockerignore
  .env.example
  .github/workflows/api.yml
  .github/workflows/ci.yml
  .github/workflows/pages.yml
  .github/workflows/release.yml
  .gitignore
  .python-version
  ARCHITECTURE.md
  BUILD_REPORT.md
  CONTRIBUTING.md
  Dockerfile
  LICENSE
  Makefile
  NOTICE
  README.md
  RESULTS.md
  THIRD_PARTY_NOTICES.md
  artifacts/coverage.xml
  artifacts/deployment.json
  artifacts/evidence.sql.gz
  artifacts/palette-validation.json
  artifacts/pytest-junit.xml
  artifacts/quality.json
  claude/build-series-log.md
  docs/case-study.md
  docs/cuped.md
  docs/decision-rules.md
  docs/demo-frames/frame-01.png
  docs/demo-frames/frame-02.png
  docs/demo-frames/frame-03.png
  docs/demo-frames/frame-04.png
  docs/demo-frames/registry-desktop.png
  docs/demo-frames/registry-mobile-light.png
  docs/demo-frames/registry-mobile.png
  docs/demo-frames/upload-success.png
  docs/demo.gif
  docs/linkedin-draft.md
  docs/methods.md
  docs/palette.md
  docs/port-provenance.md
  docs/power.md
  docs/release-notes.md
  docs/runbook.md
  docs/sequential.md
  docs/social-preview.png
  docs/srm.md
  docs/templates/README.md.jinja
  docs/templates/RESULTS.md.jinja
  docs/tree.txt
  experiments/cookie_cats/PROVENANCE.md
  experiments/cookie_cats/cookie_cats.csv
  experiments/cookie_cats/design.yaml
  experiments/cookie_cats/provenance.json
  experiments/pricepoint/assumptions.json
  experiments/pricepoint/source-elasticity.md
  experiments/pricepoint/source-plan_experiment.py
  experiments/pricepoint/source-results.md
  experiments/scenarios/at_mde.yaml
  experiments/scenarios/correlated_pre.yaml
  experiments/scenarios/guardrail_hit.yaml
  experiments/scenarios/heterogeneous.yaml
  experiments/scenarios/null.yaml
  experiments/scenarios/ratio_metric.yaml
  experiments/scenarios/srm_dropout.yaml
  fly.toml
  packages/api/alembic.ini
  packages/api/migrations/env.py
  packages/api/migrations/versions/0001_registry.py
  packages/api/pyproject.toml
  packages/api/src/readout_api/__init__.py
  packages/api/src/readout_api/app.py
  packages/api/src/readout_api/models.py
  packages/api/src/readout_api/py.typed
  packages/api/src/readout_api/repository.py
  packages/assign/pyproject.toml
  packages/assign/src/readout_assign/__init__.py
  packages/assign/src/readout_assign/py.typed
  packages/calibrate/pyproject.toml
  packages/calibrate/src/readout_calibrate/__init__.py
  packages/calibrate/src/readout_calibrate/harness.py
  packages/calibrate/src/readout_calibrate/py.typed
  packages/core/pyproject.toml
  packages/core/src/readout_core/__init__.py
  packages/core/src/readout_core/hashing.py
  packages/core/src/readout_core/logging.py
  packages/core/src/readout_core/models.py
  packages/core/src/readout_core/py.typed
  packages/render/pyproject.toml
  packages/render/src/readout_render/__init__.py
  packages/render/src/readout_render/cli.py
  packages/render/src/readout_render/py.typed
  packages/render/src/readout_render/renderer.py
  packages/sim/pyproject.toml
  packages/sim/src/readout_sim/__init__.py
  packages/sim/src/readout_sim/generator.py
  packages/sim/src/readout_sim/py.typed
  packages/stats/pyproject.toml
  packages/stats/src/readout_stats/__init__.py
  packages/stats/src/readout_stats/cityflow_fdr.py
  packages/stats/src/readout_stats/cuped.py
  packages/stats/src/readout_stats/decision.py
  packages/stats/src/readout_stats/delta.py
  packages/stats/src/readout_stats/engine.py
  packages/stats/src/readout_stats/fdr.py
  packages/stats/src/readout_stats/fixed.py
  packages/stats/src/readout_stats/guardrails.py
  packages/stats/src/readout_stats/health.py
  packages/stats/src/readout_stats/power.py
  packages/stats/src/readout_stats/py.typed
  packages/stats/src/readout_stats/sequential.py
  pyproject.toml
  readouts/at_mde.html
  readouts/at_mde.md
  readouts/cookie_cats.html
  readouts/cookie_cats.md
  readouts/correlated_pre.html
  readouts/correlated_pre.md
  readouts/guardrail_hit.html
  readouts/guardrail_hit.md
  readouts/heterogeneous.html
  readouts/heterogeneous.md
  readouts/null.html
  readouts/null.md
  readouts/ratio_metric.html
  readouts/ratio_metric.md
  readouts/srm_dropout.html
  readouts/srm_dropout.md
  readouts/templates/readout.html.jinja
  readouts/templates/readout.md.jinja
  scripts/__init__.py
  scripts/build_demo_gif.py
  scripts/build_handoff.py
  scripts/build_social_preview.py
  scripts/check_no_em_dash.py
  scripts/check_persistence.py
  scripts/check_published_numbers.py
  scripts/fetch_cookie_cats.py
  scripts/ingest_cookie_cats.py
  scripts/palette_core.cjs
  scripts/reset_and_rederive.py
  scripts/restore_evidence.py
  scripts/run_calibration.py
  scripts/seed_database.py
  scripts/start_api.py
  scripts/validate_palette.js
  tests/fixtures/upload_demo.csv
  tests/test_api_inference_contracts.py
  tests/test_api_persistence.py
  tests/test_api_startup.py
  tests/test_assignment.py
  tests/test_calibration.py
  tests/test_core_contracts.py
  tests/test_render.py
  tests/test_sim.py
  tests/test_stats.py
  uv.lock
  web/PALETTE.md
  web/next-env.d.ts
  web/next.config.ts
  web/package-lock.json
  web/package.json
  web/postcss.config.mjs
  web/public/readouts/at_mde.html
  web/public/readouts/at_mde.md
  web/public/readouts/cookie_cats.html
  web/public/readouts/cookie_cats.md
  web/public/readouts/correlated_pre.html
  web/public/readouts/correlated_pre.md
  web/public/readouts/guardrail_hit.html
  web/public/readouts/guardrail_hit.md
  web/public/readouts/heterogeneous.html
  web/public/readouts/heterogeneous.md
  web/public/readouts/null.html
  web/public/readouts/null.md
  web/public/readouts/ratio_metric.html
  web/public/readouts/ratio_metric.md
  web/public/readouts/srm_dropout.html
  web/public/readouts/srm_dropout.md
  web/public/results/bundle.json
  web/scripts/serve.mjs
  web/src/app/assign/page.tsx
  web/src/app/calibration/page.tsx
  web/src/app/design/page.tsx
  web/src/app/experiments/[key]/page.tsx
  web/src/app/experiments/page.tsx
  web/src/app/globals.css
  web/src/app/layout.tsx
  web/src/app/page.tsx
  web/src/app/upload/page.tsx
  web/src/components/assignment.tsx
  web/src/components/calibration.tsx
  web/src/components/charts.tsx
  web/src/components/design.tsx
  web/src/components/readout.tsx
  web/src/components/registry.tsx
  web/src/components/shell.tsx
  web/src/components/upload.tsx
  web/src/lib/data.ts
  web/src/lib/power.ts
  web/tests/power.test.ts
  web/tsconfig.json
```

## Peeking calibration

Source: simulated true null; daily checks. All rate intervals are Monte Carlo Wilson intervals.

| Checks | Naive rejection rate | Sequential rejection rate |
| ---: | --- | --- |
| 1 | 4.00% [2.95%, 5.40%] | 0.00% [0.00%, 0.38%] |
| 2 | 7.10% [5.67%, 8.86%] | 0.00% [0.00%, 0.38%] |
| 3 | 9.50% [7.83%, 11.48%] | 0.00% [0.00%, 0.38%] |
| 4 | 10.60% [8.84%, 12.66%] | 0.10% [0.02%, 0.56%] |
| 5 | 12.60% [10.69%, 14.80%] | 0.10% [0.02%, 0.56%] |
| 6 | 13.50% [11.52%, 15.76%] | 0.20% [0.05%, 0.73%] |
| 7 | 14.50% [12.45%, 16.82%] | 0.20% [0.05%, 0.73%] |
| 8 | 15.60% [13.48%, 17.98%] | 0.20% [0.05%, 0.73%] |
| 9 | 16.80% [14.61%, 19.24%] | 0.20% [0.05%, 0.73%] |
| 10 | 17.40% [15.18%, 19.87%] | 0.20% [0.05%, 0.73%] |
| 11 | 18.30% [16.03%, 20.82%] | 0.20% [0.05%, 0.73%] |
| 12 | 18.80% [16.50%, 21.34%] | 0.30% [0.10%, 0.88%] |
| 13 | 19.60% [17.26%, 22.17%] | 0.40% [0.16%, 1.02%] |
| 14 | 20.20% [17.83%, 22.80%] | 0.40% [0.16%, 1.02%] |
| 15 | 20.40% [18.02%, 23.01%] | 0.50% [0.21%, 1.17%] |
| 16 | 20.70% [18.30%, 23.32%] | 0.50% [0.21%, 1.17%] |
| 17 | 22.00% [19.54%, 24.67%] | 0.60% [0.28%, 1.30%] |
| 18 | 22.20% [19.73%, 24.88%] | 0.60% [0.28%, 1.30%] |
| 19 | 22.50% [20.02%, 25.19%] | 0.60% [0.28%, 1.30%] |
| 20 | 22.70% [20.21%, 25.40%] | 0.70% [0.34%, 1.44%] |
| 21 | 23.00% [20.50%, 25.71%] | 0.70% [0.34%, 1.44%] |
| 22 | 23.20% [20.69%, 25.92%] | 0.70% [0.34%, 1.44%] |
| 23 | 23.60% [21.07%, 26.33%] | 0.70% [0.34%, 1.44%] |
| 24 | 24.30% [21.74%, 27.05%] | 0.70% [0.34%, 1.44%] |
| 25 | 24.80% [22.22%, 27.57%] | 0.70% [0.34%, 1.44%] |
| 26 | 25.00% [22.42%, 27.78%] | 0.70% [0.34%, 1.44%] |
| 27 | 25.30% [22.70%, 28.09%] | 0.70% [0.34%, 1.44%] |
| 28 | 25.60% [22.99%, 28.39%] | 0.70% [0.34%, 1.44%] |
| 29 | 25.80% [23.18%, 28.60%] | 0.70% [0.34%, 1.44%] |
| 30 | 26.30% [23.67%, 29.12%] | 0.80% [0.41%, 1.57%] |

## Empirical power

| Planned sample multiple | Units per arm | Empirical power | Theoretical power |
| ---: | ---: | --- | ---: |
| 0.5 | 442 | 49.20% [44.84%, 53.57%] | 50.89% |
| 0.75 | 663 | 68.20% [63.99%, 72.13%] | 68.00% |
| 1 | 883 | 80.00% [76.27%, 83.27%] | 80.00% |
| 1.5 | 1325 | 93.60% [91.10%, 95.43%] | 92.95% |
| 2 | 1766 | 97.80% [96.10%, 98.77%] | 97.74% |

## SRM sensitivity

| Units per arm before defect | Treatment dropout | Blocking probability |
| ---: | ---: | --- |
| 1000 | 0.00% | 0.40% [0.11%, 1.45%] |
| 1000 | 1.00% | 0.00% [0.00%, 0.76%] |
| 1000 | 2.00% | 0.20% [0.04%, 1.12%] |
| 1000 | 3.00% | 0.20% [0.04%, 1.12%] |
| 1000 | 4.00% | 0.60% [0.20%, 1.75%] |
| 1000 | 5.00% | 1.40% [0.68%, 2.86%] |
| 1000 | 10.00% | 19.80% [16.54%, 23.52%] |
| 10000 | 0.00% | 0.00% [0.00%, 0.76%] |
| 10000 | 1.00% | 0.80% [0.31%, 2.04%] |
| 10000 | 2.00% | 2.00% [1.09%, 3.64%] |
| 10000 | 3.00% | 9.60% [7.32%, 12.50%] |
| 10000 | 4.00% | 31.40% [27.49%, 35.60%] |
| 10000 | 5.00% | 64.00% [59.70%, 68.09%] |
| 10000 | 10.00% | 100.00% [99.24%, 100.00%] |
| 100000 | 0.00% | 0.20% [0.04%, 1.12%] |
| 100000 | 1.00% | 15.00% [12.14%, 18.40%] |
| 100000 | 2.00% | 86.80% [83.55%, 89.49%] |
| 100000 | 3.00% | 100.00% [99.24%, 100.00%] |
| 100000 | 4.00% | 100.00% [99.24%, 100.00%] |
| 100000 | 5.00% | 100.00% [99.24%, 100.00%] |
| 100000 | 10.00% | 100.00% [99.24%, 100.00%] |

## Pricepoint reproduction

Calculated 820 per arm; published 820. Residual SD 1.03269289; log-scale effect 0.14296527. No missing variance assumption: sigma is the measured held-out log1p-demand forecast residual standard deviation. Serial dependence and interference still require a clustered pilot.

## Cookie Cats health

- srm_assigned: observed {'control': 44700, 'treatment': 45489}; expected {'control': 45094.5, 'treatment': 45094.5}; p 0.008608; conventional warn; blocking pass.
- srm_exposed: observed {'control': 44700, 'treatment': 45489}; expected {'control': 45094.5, 'treatment': 45094.5}; p 0.008608; conventional warn; blocking pass.

## Cookie Cats decision

**NO_SHIP**. The primary interval excludes the pre-registered MDE in the favorable direction.

> ship: health passes, the primary interval excludes zero in the good direction, and every guardrail passes its margin; no_ship: any guardrail fails or the primary interval excludes the MDE in the good direction; extend: unresolved with additional sample from the power calculator; blocked: health fails.

## Remaining dependencies and limits

GitHub Pages serves the canonical bundle. The local live API and CSV upload were verified in a real browser. Public Fly/Neon API deployment remains unverified: no provider configuration was available, Fly was signed out, and a general Fly free tier is no longer offered. No billable resources were provisioned.

Windows SciPy modules were blocked by Application Control; numerical runs and Postgres checks completed in Linux Docker. Cookie Cats has no actual gate-exposure records, timestamps or pre-period covariates; its protocol is retrospective. The mandated dark palette has one documented inherited color-vision separation exception, with redundant marks and labels. Optional stretch modules were deferred.
