"""Every write commits, and health is independently durable before analysis."""

from __future__ import annotations

import copy
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

from readout_assign import assign
from readout_core.hashing import content_hash
from readout_core.models import Design, ExperimentCreate, UnitRow
from sqlalchemy import delete, event, insert
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, col, create_engine, select

from readout_api.models import (
    AnalysisRun,
    Assignment,
    Decision,
    Evidence,
    Experiment,
    Exposure,
    HealthCheck,
    UnitMetric,
    UnitObservation,
    identifier,
    now,
)


class NotFoundError(ValueError):
    """A resource does not exist inside the requested experiment."""


class ConflictError(ValueError):
    """A write violates the experiment lifecycle."""


def database_url() -> str:
    return os.getenv(
        "READOUT_DATABASE_URL", os.getenv("DATABASE_URL", "sqlite:///artifacts/readout.db")
    )


def make_engine(url: str) -> Engine:
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    kwargs: dict[str, Any] = {"pool_pre_ping": True}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False, "timeout": 30}
        if url in {"sqlite://", "sqlite:///:memory:"}:
            kwargs["poolclass"] = StaticPool
        elif url.startswith("sqlite:///"):
            Path(url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(url, **kwargs)
    if url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def configure_sqlite(connection: Any, _: Any) -> None:
            connection.execute("PRAGMA foreign_keys=ON")

    return engine


def serializable(value: Any) -> Any:
    return json.loads(json.dumps(value, allow_nan=False, default=lambda v: v.item()))


def _experiment(session: Session, key: str) -> Experiment:
    result = session.exec(select(Experiment).where(Experiment.key == key)).first()
    if result is None:
        raise NotFoundError(f"experiment {key!r} not found")
    return result


def experiment_dict(record: Experiment) -> dict[str, Any]:
    result = record.model_dump()
    result.update(copy.deepcopy(record.design))
    result["current_design"] = copy.deepcopy(record.design)
    return result


def health_dict(record: HealthCheck) -> dict[str, Any]:
    return {**record.model_dump(), **record.detail.get("health_record", {})}


class Repository:
    def __init__(self, database_url: str | None = None, *, create_tables: bool = True) -> None:
        self.engine = make_engine(database_url or globals()["database_url"]())
        if create_tables:
            SQLModel.metadata.create_all(self.engine)

    def close(self) -> None:
        self.engine.dispose()

    def create_experiment(self, payload: dict[str, Any] | ExperimentCreate) -> dict[str, Any]:
        if isinstance(payload, ExperimentCreate):
            request = payload
        else:
            values = copy.deepcopy(payload)
            flat = {k: values.pop(k) for k in list(values) if k in Design.model_fields}
            if flat:
                values["design"] = {**values.get("design", {}), **flat}
            request = ExperimentCreate.model_validate(values)
        values = request.model_dump()
        record = Experiment(**values)
        if record.status == "running":
            record.registered_design = copy.deepcopy(record.design)
            record.design_hash = content_hash(record.design)
            record.started_at = now()
        with Session(self.engine) as session:
            if session.exec(select(Experiment).where(Experiment.key == request.key)).first():
                raise ConflictError("experiment key already exists")
            session.add(record)
            session.commit()
            session.refresh(record)
            return experiment_dict(record)

    def get_experiment(self, key: str) -> dict[str, Any]:
        with Session(self.engine) as session:
            return experiment_dict(_experiment(session, key))

    def list_experiments(self) -> list[dict[str, Any]]:
        with Session(self.engine) as session:
            records = session.exec(select(Experiment).order_by(Experiment.key)).all()
            return [experiment_dict(record) for record in records]

    def start_experiment(self, key: str) -> dict[str, Any]:
        with Session(self.engine) as session:
            record = _experiment(session, key)
            if record.status != "draft":
                raise ConflictError("only a draft can be registered")
            record.registered_design = copy.deepcopy(record.design)
            record.design_hash = content_hash(record.design)
            record.started_at = now()
            record.status = "running"
            session.add(record)
            session.commit()
        return self.get_experiment(key)

    def update_experiment(self, key: str, payload: dict[str, Any]) -> dict[str, Any]:
        allowed = {"design", "name", "hypothesis", "owner", "reason"} | set(Design.model_fields)
        unknown = set(payload) - allowed
        if unknown:
            raise ValueError(f"unsupported experiment fields: {sorted(unknown)}")
        with Session(self.engine) as session:
            record = _experiment(session, key)
            previous = copy.deepcopy(record.design)
            design_updates = {
                **payload.get("design", {}),
                **{k: v for k, v in payload.items() if k in Design.model_fields},
            }
            current = Design.model_validate({**record.design, **design_updates}).model_dump()
            if record.design_hash is not None and current != previous:
                record.design_deviations = [
                    *record.design_deviations,
                    {
                        "recorded_at": now(),
                        "changed_fields": sorted(k for k in current if current[k] != previous[k]),
                        "previous_hash": content_hash(previous),
                        "new_hash": content_hash(current),
                        "registered_hash": record.design_hash,
                        "reason": payload.get("reason", "Design edited after registration"),
                    },
                ]
            record.design = current
            for field in ("name", "hypothesis", "owner"):
                if field in payload:
                    setattr(record, field, str(payload[field]))
            session.add(record)
            session.commit()
        return self.get_experiment(key)

    def assignment(self, key: str, unit_id: str) -> dict[str, Any]:
        return assign(self.get_experiment(key), unit_id)

    def assign_units(self, key: str, unit_ids: list[str]) -> list[dict[str, Any]]:
        with Session(self.engine) as session:
            experiment = _experiment(session, key)
            if experiment.status == "draft":
                raise ConflictError("register the experiment before assigning units")
            results = []
            for unit_id in dict.fromkeys(unit_ids):
                result = assign(experiment_dict(experiment), unit_id)
                existing = session.exec(
                    select(Assignment).where(
                        Assignment.experiment_id == experiment.id, Assignment.unit_id == unit_id
                    )
                ).first()
                if existing is None:
                    session.add(
                        Assignment(
                            experiment_id=experiment.id,
                            unit_id=unit_id,
                            variant=result["variant"],
                            bucket=result["bucket"],
                        )
                    )
                elif existing.variant != result["variant"]:
                    result["original_variant"] = existing.variant
                    result["ramp_changed"] = True
                results.append(result)
            session.commit()
            return results

    def get_assignments(self, key: str, *, limit: int = 1000) -> list[dict[str, Any]]:
        with Session(self.engine) as session:
            experiment = _experiment(session, key)
            records = session.exec(
                select(Assignment).where(Assignment.experiment_id == experiment.id).limit(limit)
            ).all()
            from readout_core.hashing import hash_unit_id

            return [
                {
                    "id": r.id,
                    "experiment_id": r.experiment_id,
                    "unit_id_hash": hash_unit_id(r.unit_id),
                    "variant": r.variant,
                    "bucket": r.bucket,
                    "assigned_at": r.assigned_at,
                }
                for r in records
            ]

    def import_rows(self, key: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
        normalized = [UnitRow.model_validate(row).model_dump() for row in rows]
        ids = [row["unit_id"] for row in normalized]
        if len(ids) != len(set(ids)):
            raise ValueError("unit_id must be unique within an experiment")
        with Session(self.engine) as session:
            experiment = _experiment(session, key)
            if experiment.status == "draft":
                raise ConflictError("register the experiment before importing observations")
            known_metrics = {m["key"] for m in experiment.registered_design["metrics"]}  # type: ignore[index]
            for row in normalized:
                if set(row["metrics"]) - known_metrics:
                    raise ValueError(
                        "observation contains a metric absent from the registered design"
                    )
            if session.exec(
                select(UnitObservation).where(UnitObservation.experiment_id == experiment.id)
            ).first():
                raise ConflictError(
                    "observations already imported; create a new experiment for a new dataset"
                )
            existing = {
                r.unit_id: r
                for r in session.exec(
                    select(Assignment).where(Assignment.experiment_id == experiment.id)
                ).all()
            }
            assignment_rows, exposure_rows, observation_rows, metric_rows = [], [], [], []
            timestamp = now()
            assignment_design = experiment_dict(experiment)
            for row in normalized:
                unit_id = row["unit_id"]
                if unit_id in existing and existing[unit_id].variant != row["variant"]:
                    raise ValueError("imported variant conflicts with audited assignment")
                if unit_id not in existing:
                    assignment_rows.append(
                        {
                            "id": identifier(),
                            "experiment_id": experiment.id,
                            "unit_id": unit_id,
                            "variant": row["variant"],
                            "bucket": assign(assignment_design, unit_id)["bucket"],
                            "assigned_at": timestamp,
                        }
                    )
                if row["exposed"]:
                    exposure_rows.append(
                        {
                            "id": identifier(),
                            "experiment_id": experiment.id,
                            "unit_id": unit_id,
                            "day": row["day"],
                            "first_exposed_at": timestamp,
                        }
                    )
                observation_rows.append(
                    {
                        "id": identifier(),
                        "experiment_id": experiment.id,
                        "unit_id": unit_id,
                        "row": row,
                    }
                )
                for metric_key, value in row["metrics"].items():
                    metric_rows.append(
                        {
                            "id": identifier(),
                            "experiment_id": experiment.id,
                            "unit_id": unit_id,
                            "metric_key": metric_key,
                            "value": value,
                            "pre_value": row["pre"].get(metric_key),
                            "sessions": row["denominators"].get(metric_key),
                        }
                    )
            for model, batch in (
                (Assignment, assignment_rows),
                (Exposure, exposure_rows),
                (UnitObservation, observation_rows),
                (UnitMetric, metric_rows),
            ):
                if batch:
                    session.execute(insert(model), batch)
            session.commit()
        return {
            "experiment_key": key,
            "rows": len(normalized),
            "inputs_hash": content_hash(normalized),
        }

    def get_rows(self, key: str) -> list[dict[str, Any]]:
        with Session(self.engine) as session:
            experiment = _experiment(session, key)
            observations = {
                r.unit_id: r.row
                for r in session.exec(
                    select(UnitObservation).where(UnitObservation.experiment_id == experiment.id)
                ).all()
            }
            assignments = session.exec(
                select(Assignment)
                .where(Assignment.experiment_id == experiment.id)
                .order_by(Assignment.unit_id)
            ).all()
            return [
                observations.get(
                    assignment.unit_id,
                    {
                        "unit_id": assignment.unit_id,
                        "variant": assignment.variant,
                        "exposed": False,
                        "day": 1,
                        "segment": "unobserved",
                        "metrics": {},
                        "pre": {},
                        "denominators": {},
                    },
                )
                for assignment in assignments
            ]

    def analyze(self, key: str) -> dict[str, Any]:
        experiment = self.get_experiment(key)
        if experiment["registered_design"] is None:
            raise ConflictError("register the design before analysis")
        from readout_stats.engine import analyze
        from readout_stats.health import check_health

        design = experiment["registered_design"]
        if content_hash(design) != experiment["design_hash"]:
            raise ConflictError("registered design hash mismatch")
        rows = self.get_rows(key)
        health = serializable(check_health(design, rows))
        if not health:
            raise ValueError("health checker must produce a record")
        run = AnalysisRun(
            experiment_id=experiment["id"],
            inputs_hash=content_hash(rows),
            design_hash=experiment["design_hash"],
            n_per_arm=dict(Counter(row["variant"] for row in rows if row["exposed"])),
        )
        run_id = run.id
        with Session(self.engine) as session:
            session.add(run)
            session.flush()
            for item in health:
                session.add(
                    HealthCheck(
                        analysis_run_id=run_id,
                        kind=item.get("kind", item.get("check", "unknown")),
                        statistic=item.get("statistic"),
                        p_value=item.get("p_value"),
                        status=item["status"],
                        detail={"health_record": item},
                    )
                )
            session.commit()
        persisted_health = self.get_health(key, run_id)
        results = serializable(analyze(design, rows, persisted_health))
        if any(h["status"] == "block" for h in persisted_health) and results.get("metrics"):
            raise ValueError("engine violated the health gate")
        decision_data = results.get(
            "decision", {"decision": "blocked", "reason": "No decision produced"}
        )
        with Session(self.engine) as session:
            stored = session.get(AnalysisRun, run_id)
            assert stored is not None
            stored.results = results
            stored.status = "complete"
            session.add(stored)
            session.add(
                Decision(
                    experiment_id=experiment["id"],
                    analysis_run_id=run_id,
                    decision=decision_data["decision"],
                    rule_applied=decision_data,
                )
            )
            record = _experiment(session, key)
            record.status = "readout"
            record.decision = decision_data["decision"]
            session.add(record)
            session.commit()
        return self.get_run(key, run_id)

    def get_run(self, key: str, run_id: str) -> dict[str, Any]:
        with Session(self.engine) as session:
            experiment = _experiment(session, key)
            run = session.get(AnalysisRun, run_id)
            if run is None or run.experiment_id != experiment.id:
                raise NotFoundError("analysis run not found in this experiment")
            return run.model_dump()

    def get_health(self, key: str, run_id: str) -> list[dict[str, Any]]:
        self.get_run(key, run_id)
        with Session(self.engine) as session:
            return [
                health_dict(row)
                for row in session.exec(
                    select(HealthCheck).where(HealthCheck.analysis_run_id == run_id)
                ).all()
            ]

    def get_decision(self, key: str, decision_id: str) -> dict[str, Any]:
        with Session(self.engine) as session:
            experiment = _experiment(session, key)
            decision = session.get(Decision, decision_id)
            if decision is None or decision.experiment_id != experiment.id:
                raise NotFoundError("decision not found in this experiment")
            return decision.model_dump()

    def latest_manifest(self, key: str) -> dict[str, Any]:
        with Session(self.engine) as session:
            experiment = _experiment(session, key)
            run = session.exec(
                select(AnalysisRun)
                .where(AnalysisRun.experiment_id == experiment.id)
                .order_by(col(AnalysisRun.ran_at).desc())
            ).first()
            if run is None:
                raise NotFoundError("experiment has no analysis run")
            decision = session.exec(
                select(Decision).where(
                    Decision.experiment_id == experiment.id, Decision.analysis_run_id == run.id
                )
            ).first()
            health = [
                health_dict(r)
                for r in session.exec(
                    select(HealthCheck).where(HealthCheck.analysis_run_id == run.id)
                ).all()
            ]
            return {
                "experiment": experiment_dict(experiment),
                "run": run.model_dump(),
                "health": health,
                "results": run.results,
                "decision": decision.model_dump() if decision else None,
            }

    def decide(self, key: str, run_id: str) -> dict[str, Any]:
        run = self.get_run(key, run_id)
        if run["status"] != "complete":
            raise ConflictError("only a completed analysis can be decided")
        recommendation = run["results"].get("decision", {})
        if recommendation.get("decision") == "ship" and recommendation.get("provisional"):
            raise ConflictError(
                "Cannot finalize a provisional ship recommendation: both arms must reach the registered sample horizon"
            )
        with Session(self.engine) as session:
            experiment = _experiment(session, key)
            record = session.exec(
                select(Decision).where(
                    Decision.experiment_id == experiment.id, Decision.analysis_run_id == run_id
                )
            ).first()
            if record is None:
                raise ConflictError("analysis has no recorded decision")
            experiment.status = "decided"
            experiment.decided_at = now()
            experiment.decision = record.decision
            session.add(experiment)
            session.commit()
            session.refresh(record)
            return record.model_dump()

    def save_evidence(self, name: str, payload: dict[str, Any]) -> dict[str, Any]:
        with Session(self.engine) as session:
            record = session.get(Evidence, name) or Evidence(name=name)
            record.payload = serializable(payload)
            record.recorded_at = now()
            session.add(record)
            session.commit()
            return record.payload

    def record_readout(self, key: str, run_id: str, markdown: str) -> str:
        """Bind the decision audit to the bytes actually rendered for download."""
        import hashlib

        self.get_run(key, run_id)
        digest = hashlib.sha256(markdown.encode("utf-8")).hexdigest()
        with Session(self.engine) as session:
            experiment = _experiment(session, key)
            decision = session.exec(
                select(Decision).where(
                    Decision.experiment_id == experiment.id, Decision.analysis_run_id == run_id
                )
            ).first()
            if decision is None:
                raise NotFoundError("decision not found in this experiment")
            decision.rendered_readout_sha256 = digest
            session.add(decision)
            session.commit()
        return digest

    def get_evidence(self, name: str) -> dict[str, Any]:
        with Session(self.engine) as session:
            record = session.get(Evidence, name)
            if record is None:
                raise NotFoundError(f"evidence {name!r} not found")
            return record.payload

    def save_calibration(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.save_evidence("calibration", payload)

    def get_calibration(self) -> dict[str, Any]:
        return self.get_evidence("calibration")

    def reset(self) -> None:
        with Session(self.engine) as session:
            for model in (
                Decision,
                HealthCheck,
                AnalysisRun,
                UnitMetric,
                UnitObservation,
                Exposure,
                Assignment,
                Experiment,
                Evidence,
            ):
                session.execute(delete(model))
            session.commit()
