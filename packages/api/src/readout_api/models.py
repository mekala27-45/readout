"""Durable SQLModel records, shared by SQLite demos and Postgres deployments."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import JSON, Column, UniqueConstraint
from sqlmodel import Field, SQLModel


def now() -> str:
    return datetime.now(UTC).isoformat()


def identifier() -> str:
    return str(uuid4())


class Experiment(SQLModel, table=True):
    id: str = Field(default_factory=identifier, primary_key=True)
    key: str = Field(unique=True, index=True)
    name: str
    hypothesis: str
    owner: str
    unit_type: str
    salt: str
    status: str = "draft"
    source: str
    source_detail: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    design: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    registered_design: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    design_hash: str | None = None
    design_deviations: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: str = Field(default_factory=now)
    started_at: str | None = None
    decided_at: str | None = None
    decision: str | None = None


class Assignment(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("experiment_id", "unit_id"),)
    id: str = Field(default_factory=identifier, primary_key=True)
    experiment_id: str = Field(foreign_key="experiment.id", index=True)
    unit_id: str
    variant: str
    bucket: int
    assigned_at: str = Field(default_factory=now)


class Exposure(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("experiment_id", "unit_id"),)
    id: str = Field(default_factory=identifier, primary_key=True)
    experiment_id: str = Field(foreign_key="experiment.id", index=True)
    unit_id: str
    first_exposed_at: str = Field(default_factory=now)
    day: int


class UnitObservation(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("experiment_id", "unit_id"),)
    id: str = Field(default_factory=identifier, primary_key=True)
    experiment_id: str = Field(foreign_key="experiment.id", index=True)
    unit_id: str
    row: dict[str, Any] = Field(sa_column=Column(JSON))


class UnitMetric(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("experiment_id", "unit_id", "metric_key"),)
    id: str = Field(default_factory=identifier, primary_key=True)
    experiment_id: str = Field(foreign_key="experiment.id", index=True)
    unit_id: str
    metric_key: str
    value: float | None = None
    pre_value: float | None = None
    sessions: float | None = None


class AnalysisRun(SQLModel, table=True):
    id: str = Field(default_factory=identifier, primary_key=True)
    experiment_id: str = Field(foreign_key="experiment.id", index=True)
    ran_at: str = Field(default_factory=now)
    as_of: str = Field(default_factory=now)
    n_per_arm: dict[str, int] = Field(default_factory=dict, sa_column=Column(JSON))
    inputs_hash: str
    code_version: str = "0.1.0"
    results: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    design_hash: str
    status: str = "health_recorded"


class HealthCheck(SQLModel, table=True):
    id: str = Field(default_factory=identifier, primary_key=True)
    analysis_run_id: str = Field(foreign_key="analysisrun.id", index=True)
    kind: str
    statistic: float | None = None
    p_value: float | None = None
    status: str
    detail: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))


class Decision(SQLModel, table=True):
    id: str = Field(default_factory=identifier, primary_key=True)
    experiment_id: str = Field(foreign_key="experiment.id", index=True)
    analysis_run_id: str = Field(foreign_key="analysisrun.id", index=True)
    decision: str
    rule_applied: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    rendered_readout_sha256: str | None = None
    decided_at: str = Field(default_factory=now)


class Evidence(SQLModel, table=True):
    name: str = Field(primary_key=True)
    recorded_at: str = Field(default_factory=now)
    payload: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
