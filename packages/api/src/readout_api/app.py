"""Async HTTP interface; durable work executes in FastAPI's bounded thread pool."""

from __future__ import annotations

import csv
import io
import os
import secrets
import statistics
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, Any, Literal, cast

import structlog
from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Query, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from pydantic import Field, ValidationError
from readout_core.logging import configure_logging
from readout_core.models import ExperimentCreate, StrictModel, UnitRow
from starlette.requests import Request

from readout_api.repository import ConflictError, NotFoundError, Repository


class AssignmentRequest(StrictModel):
    experiment_key: str
    unit_id: str = Field(min_length=1, max_length=256)


class AssignmentBatch(StrictModel):
    unit_ids: list[str] = Field(min_length=1, max_length=10000)


class ObservationBatch(StrictModel):
    rows: list[UnitRow] = Field(max_length=200000)


class DecisionRequest(StrictModel):
    analysis_run_id: str


class PowerRequest(StrictModel):
    baseline: float = Field(default=10.0, gt=0)
    mde_relative: float = Field(default=0.1, gt=0)
    alpha: float = Field(default=0.05, gt=0, lt=1)
    power: float = Field(default=0.8, gt=0, lt=1)
    allocation: float = Field(default=0.5, gt=0, lt=1)
    standard_deviation: float = Field(default=5.0, gt=0)
    kind: Literal["mean", "proportion"] = "mean"
    daily_units: float | None = Field(default=None, gt=0)


def parse_csv(contents: bytes) -> tuple[list[dict[str, Any]], list[str]]:
    if not contents:
        raise ValueError("CSV is empty")
    reader = csv.DictReader(io.StringIO(contents.decode("utf-8-sig")))
    fields = reader.fieldnames or []
    if not {"unit_id", "variant"}.issubset(fields):
        raise ValueError("CSV requires unit_id and variant columns")
    metric_fields = [field for field in fields if field == "value" or field.startswith("metric_")]
    if not metric_fields:
        raise ValueError("CSV requires value or metric_<name> columns")
    rows: list[dict[str, Any]] = []
    for number, row in enumerate(reader, start=2):
        if len(rows) >= 200000:
            raise ValueError("CSV exceeds the 200000 unit limit")
        variant = row["variant"].strip().lower()
        if variant not in {"control", "treatment"}:
            raise ValueError(f"row {number}: variant must be control or treatment")
        exposure = row.get("exposed", "true").strip().lower()
        if exposure not in {"1", "true", "yes", "0", "false", "no"}:
            raise ValueError(f"row {number}: exposed must be true or false")
        metrics: dict[str, float | None] = {}
        pre: dict[str, float | None] = {}
        denominators: dict[str, float | None] = {}
        for field in metric_fields:
            key = field.removeprefix("metric_")
            metrics[key] = float(row[field]) if row.get(field, "").strip() else None
            pre_field = "pre_value" if key == "value" else f"pre_{key}"
            denominator_field = f"denominator_{key}"
            if row.get(pre_field, "").strip():
                pre[key] = float(row[pre_field])
            if row.get(denominator_field, "").strip():
                denominators[key] = float(row[denominator_field])
        rows.append(UnitRow(unit_id=row["unit_id"], variant=cast(Literal["control", "treatment"], variant),
            exposed=exposure in {"1", "true", "yes"}, day=int(row.get("day", "1")),
            segment=row.get("segment", "all"), metrics=metrics, pre=pre,
            denominators=denominators).model_dump())
    if not rows:
        raise ValueError("CSV contains a header but no observations")
    return rows, [field.removeprefix("metric_") for field in metric_fields]


def retrospective_planning(rows: list[dict[str, Any]], primary: dict[str, Any]) -> dict[str, Any]:
    """Derive explicitly retrospective planning assumptions from control units."""
    from readout_stats.power import required_sample_size
    key, kind = primary["key"], primary["kind"]
    values = [float(row["metrics"][key]) / (float(row["denominators"][key]) if kind == "ratio" else 1)
              for row in rows if row["variant"] == "control" and row["exposed"]
              and row["metrics"].get(key) is not None]
    baseline = abs(statistics.fmean(values)) if values else 0.0
    fallback = baseline == 0 or (kind == "proportion" and baseline == 1)
    if fallback:
        baseline = 0.4 if kind == "proportion" else 1.0
    deviation = statistics.stdev(values) if len(values) >= 2 else 1.0
    deviation = deviation or 1.0
    mde = min(0.1, (1 - baseline) / (2 * baseline)) if kind == "proportion" else 0.1
    planned = required_sample_size(baseline, mde, standard_deviation=deviation,
                                   kind="mean" if kind == "ratio" else kind)
    return {"baseline": baseline, "standard_deviation": deviation, "mde_relative": mde,
            "planned_n_per_arm": planned["n_per_arm"], "fallback_baseline": fallback,
            "planning_method": "Retrospective control sample; ratio planning uses unit ratios and a mean approximation"}


def create_app(database_url: str | None = None, write_token: str | None = None) -> FastAPI:
    cloud = bool(os.getenv("FLY_APP_NAME")) or os.getenv("READOUT_ENV") == "production"
    token = write_token if write_token is not None else os.getenv("READOUT_WRITE_TOKEN")
    if cloud and (not token or token == "demo-write-token"):
        raise RuntimeError("cloud deployments require a non-default READOUT_WRITE_TOKEN")
    token = token or "demo-write-token"
    repository: Repository | None = None

    def repo() -> Repository:
        nonlocal repository
        if repository is None:
            repository = Repository(database_url)
            application.state.repository = repository
        return repository

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        configure_logging()
        await run_in_threadpool(repo)
        yield
        if repository is not None:
            repository.close()

    application = FastAPI(title="readout", version="0.1.0", lifespan=lifespan)
    origins = os.getenv("READOUT_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    application.add_middleware(CORSMiddleware, allow_origins=origins,
                               allow_methods=["GET", "POST", "PATCH"],
                               allow_headers=["Authorization", "Content-Type"])

    async def require_write(authorization: Annotated[str | None, Header()] = None) -> None:
        expected = f"Bearer {token}"
        if authorization is None or not secrets.compare_digest(authorization.encode(), expected.encode()):
            raise HTTPException(status_code=401, detail="A write bearer token is required")

    @application.exception_handler(NotFoundError)
    async def missing(_: Request, error: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(error)})

    @application.exception_handler(ConflictError)
    async def conflict(_: Request, error: ConflictError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(error)})

    @application.exception_handler(ValueError)
    async def invalid(_: Request, error: ValueError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(error)})

    @application.exception_handler(ValidationError)
    async def validation(_: Request, error: ValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(error)})

    @application.get("/healthz")
    async def healthz() -> dict[str, str]:
        await run_in_threadpool(repo().list_experiments)
        return {"status": "ok", "service": "readout"}

    @application.get("/api/bundle")
    async def bundle() -> dict[str, Any]:
        from readout_render.renderer import build_bundle
        return await run_in_threadpool(build_bundle, repo())

    @application.get("/api/experiments")
    async def experiments() -> list[dict[str, Any]]:
        return await run_in_threadpool(repo().list_experiments)

    @application.post("/api/experiments", status_code=201, dependencies=[Depends(require_write)])
    async def create(payload: ExperimentCreate) -> dict[str, Any]:
        return await run_in_threadpool(repo().create_experiment, payload)

    @application.get("/api/experiments/{key}")
    async def experiment(key: str) -> dict[str, Any]:
        return await run_in_threadpool(repo().get_experiment, key)

    @application.patch("/api/experiments/{key}", dependencies=[Depends(require_write)])
    async def update(key: str, payload: dict[str, Any]) -> dict[str, Any]:
        return await run_in_threadpool(repo().update_experiment, key, payload)

    @application.post("/api/experiments/{key}/start", dependencies=[Depends(require_write)])
    async def start(key: str) -> dict[str, Any]:
        return await run_in_threadpool(repo().start_experiment, key)

    @application.post("/api/assign")
    async def assignment(payload: AssignmentRequest) -> dict[str, Any]:
        result = await run_in_threadpool(repo().assignment, payload.experiment_key, payload.unit_id)
        structlog.get_logger().info("assignment_preview", unit_id=payload.unit_id,
                                   experiment_key=payload.experiment_key, bucket=result["bucket"])
        return result

    @application.get("/api/assign")
    async def assignment_get(experiment_key: str, unit_id: str) -> dict[str, Any]:
        return await assignment(AssignmentRequest(experiment_key=experiment_key, unit_id=unit_id))

    @application.post("/api/experiments/{key}/assign", dependencies=[Depends(require_write)])
    async def assignment_batch(key: str, payload: AssignmentBatch) -> list[dict[str, Any]]:
        return await run_in_threadpool(repo().assign_units, key, payload.unit_ids)

    @application.get("/api/experiments/{key}/assignments")
    async def assignments(key: str, limit: int = Query(default=1000, ge=1, le=10000)) -> list[dict[str, Any]]:
        return await run_in_threadpool(repo().get_assignments, key, limit=limit)

    @application.post("/api/experiments/{key}/observations", dependencies=[Depends(require_write)])
    async def observations(key: str, payload: ObservationBatch) -> dict[str, Any]:
        return await run_in_threadpool(repo().import_rows, key, [r.model_dump() for r in payload.rows])

    async def uploaded_rows(file: UploadFile) -> tuple[list[dict[str, Any]], list[str]]:
        contents = await file.read(20_000_001)
        await file.close()
        if len(contents) > 20_000_000:
            raise HTTPException(status_code=413, detail="CSV exceeds the 20 MB limit")
        return await run_in_threadpool(parse_csv, contents)

    @application.post("/api/experiments/{key}/upload", dependencies=[Depends(require_write)])
    async def upload_existing(key: str, file: Annotated[UploadFile, File()]) -> dict[str, Any]:
        rows, _ = await uploaded_rows(file)
        return await run_in_threadpool(repo().import_rows, key, rows)

    @application.post("/api/upload", dependencies=[Depends(require_write)])
    async def upload(file: Annotated[UploadFile, File()],
                     name: Annotated[str, Form()] = "Uploaded experiment") -> dict[str, Any]:
        from readout_render.renderer import render_manifest
        rows, keys = await uploaded_rows(file)
        key = f"upload-{secrets.token_hex(6)}"
        metric_definitions = [{"key": key, "name": key.replace("_", " ").title(),
            "kind": "ratio" if any(key in r["denominators"] for r in rows) else
                    "proportion" if all(r["metrics"].get(key) in {None, 0.0, 1.0} for r in rows) else "mean"}
            for key in keys]
        planning = await run_in_threadpool(retrospective_planning, rows, metric_definitions[0])
        await run_in_threadpool(repo().create_experiment, {
            "key": key, "name": name, "status": "running", "source": "uploaded",
            "source_detail": {"filename": file.filename, "provenance": "User supplied unit-level CSV",
                "protocol": "Retrospective design reconstructed at upload; not historical pre-registration",
                "description": "Planning assumptions are reconstructed from uploaded controls. Degenerate controls use a disclosed baseline assumption.",
                "planning": planning},
            "design": {"primary_metric_key": keys[0], "metrics": metric_definitions,
                       "secondary_metric_keys": keys[1:], "has_timestamps": any(r["day"] > 1 for r in rows),
                       **{field: planning[field] for field in ("baseline", "standard_deviation", "mde_relative", "planned_n_per_arm")}},
        })
        await run_in_threadpool(repo().import_rows, key, rows)
        await run_in_threadpool(repo().analyze, key)
        manifest = await run_in_threadpool(repo().latest_manifest, key)
        rendered = await run_in_threadpool(render_manifest, manifest)
        await run_in_threadpool(repo().record_readout, key, manifest["run"]["id"], rendered["markdown"])
        return {"manifest": manifest, **rendered}

    @application.post("/api/experiments/{key}/analyze", dependencies=[Depends(require_write)])
    async def analyze(key: str) -> dict[str, Any]:
        return await run_in_threadpool(repo().analyze, key)

    @application.get("/api/experiments/{key}/manifest")
    async def manifest(key: str) -> dict[str, Any]:
        return await run_in_threadpool(repo().latest_manifest, key)

    @application.get("/api/experiments/{key}/runs/{run_id}")
    async def run(key: str, run_id: str) -> dict[str, Any]:
        return await run_in_threadpool(repo().get_run, key, run_id)

    @application.get("/api/experiments/{key}/runs/{run_id}/health")
    async def run_health(key: str, run_id: str) -> list[dict[str, Any]]:
        return await run_in_threadpool(repo().get_health, key, run_id)

    @application.get("/api/experiments/{key}/decisions/{decision_id}")
    async def decision(key: str, decision_id: str) -> dict[str, Any]:
        return await run_in_threadpool(repo().get_decision, key, decision_id)

    @application.post("/api/experiments/{key}/decide", dependencies=[Depends(require_write)])
    async def decide(key: str, payload: DecisionRequest) -> dict[str, Any]:
        return await run_in_threadpool(repo().decide, key, payload.analysis_run_id)

    @application.get("/api/experiments/{key}/readout", response_model=None)
    async def readout(key: str, format: str = "markdown") -> HTMLResponse | PlainTextResponse:
        from readout_render.renderer import render_manifest
        if format not in {"html", "markdown"}:
            raise HTTPException(status_code=422, detail="format must be html or markdown")
        manifest = await run_in_threadpool(repo().latest_manifest, key)
        rendered = await run_in_threadpool(render_manifest, manifest)
        await run_in_threadpool(repo().record_readout, key, manifest["run"]["id"], rendered["markdown"])
        if format == "html":
            return HTMLResponse(rendered["html"])
        return PlainTextResponse(rendered["markdown"], media_type="text/markdown",
                                 headers={"Content-Disposition": f'attachment; filename="{key}.md"'})

    @application.get("/api/calibration")
    async def calibration() -> dict[str, Any]:
        return await run_in_threadpool(repo().get_calibration)

    @application.post("/api/design/power")
    async def power(payload: PowerRequest) -> dict[str, Any]:
        from readout_stats.power import design_power
        return await run_in_threadpool(design_power, payload.model_dump())

    return application


app = create_app()
