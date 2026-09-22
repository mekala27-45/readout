# Operations and reproduction

## Local read-only evidence

Run `uv sync --frozen`, then `uv run python -m scripts.restore_evidence` into an absent local demo database. The committed compressed SQL snapshot preserves the actual analysis and calibration records. `uv run python -m scripts.check_published_numbers` uses a fresh temporary restoration and compares complete generated files. It never needs the public data host or a cloud account.

## Local live API and upload

Set `READOUT_WRITE_TOKEN` to a local development value and `READOUT_DATABASE_URL` to the intended database. Set `READOUT_CORS_ORIGINS` to the exact frontend origins. Run `uv run uvicorn readout_api.app:app --host 127.0.0.1 --port 8000`. The readiness endpoint is `/healthz`; API documentation is `/docs`.

Set `NEXT_PUBLIC_API_BASE_URL` when building or starting the frontend. In `web`, run `npm ci` and `npm run dev`. The upload form explains its CSV schema and requires the write token. Upload a unit identifier, variant and outcome column, then inspect the rendered health-first result. Uploaded designs are retrospective and assumptions are disclosed. Protect real private observations separately; this demo's registry is readable to anyone with network access.

## Windows numerical runtime

On this build machine, Windows Application Control rejected compiled SciPy modules. Security settings were left unchanged. The build and full statistical verification ran in the checked-in Linux Docker runtime:

```sh
docker build -t readout:local .
docker run --rm -p 8000:8000 -e READOUT_WRITE_TOKEN=local-development-only-change-me readout:local
```

For a development bind mount, use the repository's absolute path as `/app`. `UV_PROJECT_ENVIRONMENT` keeps the Linux environment outside the Windows virtual environment. Bulk canonical generation uses a temporary local database and copies the complete committed artifact back, avoiding slow random writes through a shared filesystem. Do not copy a live database while requests are writing to it.

## Reset after recording and before publication

Stop the local demo API before regenerating. Record the browser demonstration, then run `uv run python -m scripts.reset_and_rederive`. This rebuilds the named local canonical demo from the public source and seeded scenarios, reruns full calibration, persists readout hashes, renders documents and bundle, checks the gates and saves a compressed relational snapshot. It deliberately ignores cloud database environment variables and cannot reset a Neon project. The `make publish` target depends on this cycle.

Restart the API after regeneration so old database connections cannot retain the replaced file. Run the final tests and `uv run python -m scripts.check_published_numbers`, build the static web, and only then publish the final commit.

## GitHub Pages

The Pages workflow uses the repository base path, publishes the committed bundle and waits for successful CI. Configure Pages to use GitHub Actions. A configured API URL is optional for read-only exploration; without it, the client explicitly identifies bundled evidence. Pages cannot execute CSV analysis itself.

## Fly and Neon

The checked-in Fly configuration requires an existing app, a Neon Postgres connection string, a non-default write token and verified no-cost hosting allowance. Set those secrets in the provider's secret store, never in Git. Apply `uv run alembic -c packages/api/alembic.ini upgrade head` to the selected database. Load canonical experiments through a deliberate seed operation against that named database, then verify `/healthz`, `/api/bundle`, assignment and upload from a separate client.

Public API deployment is not claimed by this build unless separately verified. No Fly or Neon project configuration was provided in the workspace. Fly's current [cost-management documentation](https://fly.io/docs/about/cost-management/) states that it has no general free account or free tier. The deployment workflow therefore requires an explicit existing allowance attestation and will not create billable resources automatically. Neon credentials and account access were not fabricated.

## Failure handling

An SRM block is an analytical stop, not an infrastructure error. Its readout should contain health and a blocked decision with no metrics. Missing evidence makes the claim gate fail. A pending analysis after an exception retains its independently committed health rows; investigate the inputs and rerun only after resolving the cause. Never patch generated figures by hand.

Postgres tests use an availability probe. Local environments without Docker show a named skip; CI sets `READOUT_REQUIRE_POSTGRES` so an unavailable dependency fails the job. The out-of-process persistence script starts its own API and launches another database observer, so it can detect a request that flushed but never committed.
