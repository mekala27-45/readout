"""StrictModel ported from pricepoint, with experiment-specific invariants."""

from __future__ import annotations

import math
from typing import Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)


class Variant(StrictModel):
    name: Literal["control", "treatment"]
    allocation: float = Field(gt=0, lt=1)


class Metric(StrictModel):
    key: str = Field(pattern=r"^[a-z][a-z0-9_]{0,63}$")
    name: str
    kind: Literal["proportion", "mean", "ratio"] = "mean"
    numerator: str | None = None
    denominator: str | None = None
    direction: Literal["higher_is_better", "lower_is_better"] = "higher_is_better"
    guardrail_margin_relative: float | None = Field(default=None, ge=0, lt=1)
    winsor_upper_percentile: float | None = Field(default=None, gt=0.5, le=1)


DEFAULT_RULE = (
    "ship: health passes, the primary interval excludes zero in the good direction, "
    "and every guardrail passes its margin; no_ship: any guardrail fails or the "
    "primary interval excludes the MDE in the good direction; extend: unresolved "
    "with additional sample from the power calculator; blocked: health fails."
)


class DecisionRule(StrictModel):
    text: str = DEFAULT_RULE


class Design(StrictModel):
    primary_metric_key: str = "value"
    metrics: list[Metric] = Field(default_factory=lambda: [Metric(key="value", name="Outcome")])
    guardrail_metric_keys: list[str] = Field(default_factory=list)
    secondary_metric_keys: list[str] = Field(default_factory=list)
    variants: list[Variant] = Field(default_factory=lambda: [
        Variant(name="control", allocation=0.5), Variant(name="treatment", allocation=0.5)
    ])
    alpha: float = Field(default=0.05, gt=0, lt=0.5)
    power: float = Field(default=0.8, gt=0.5, lt=1)
    mde_relative: float = Field(default=0.1, gt=0)
    baseline: float = Field(default=10.0, gt=0)
    standard_deviation: float = Field(default=5.0, gt=0)
    planned_n_per_arm: int = Field(default=1000, ge=2)
    planned_days: int = Field(default=30, ge=1)
    mixing_variance: float = Field(default=1.0, gt=0)
    bootstrap_seed: int = 20260922
    bootstrap_resamples: int = Field(default=400, ge=100, le=10000)
    has_timestamps: bool = True
    fdr_q: float = Field(default=0.05, gt=0, lt=1)
    decision_rule: DecisionRule = Field(default_factory=DecisionRule)

    @model_validator(mode="after")
    def coherent_design(self) -> Self:
        keys = [metric.key for metric in self.metrics]
        if len(keys) != len(set(keys)):
            raise ValueError("metric keys must be unique")
        selected = [self.primary_metric_key, *self.guardrail_metric_keys, *self.secondary_metric_keys]
        if any(key not in keys for key in selected):
            raise ValueError("every selected metric must have a definition")
        if set(self.guardrail_metric_keys) & set(self.secondary_metric_keys):
            raise ValueError("guardrail and secondary metric roles must be disjoint")
        if self.primary_metric_key in self.guardrail_metric_keys + self.secondary_metric_keys:
            raise ValueError("the primary metric cannot have another role")
        if any(metric.key in self.guardrail_metric_keys and metric.guardrail_margin_relative is None
               for metric in self.metrics):
            raise ValueError("every guardrail must declare its non-inferiority margin")
        if sorted(v.name for v in self.variants) != ["control", "treatment"]:
            raise ValueError("exactly one control and one treatment variant are required")
        if not math.isclose(sum(v.allocation for v in self.variants), 1.0, abs_tol=1e-9):
            raise ValueError("variant allocation must sum to one")
        return self


class ExperimentCreate(StrictModel):
    key: str = Field(pattern=r"^[a-z][a-z0-9_-]{0,63}$")
    name: str = Field(min_length=1, max_length=200)
    hypothesis: str = "Treatment changes the pre-registered primary outcome."
    owner: str = "readout demo"
    unit_type: str = "user"
    salt: str = "readout-v1"
    status: Literal["draft", "running"] = "draft"
    source: Literal["simulated", "uploaded", "public"] = "simulated"
    source_detail: dict[str, Any] = Field(default_factory=dict)
    design: Design = Field(default_factory=Design)


class UnitRow(StrictModel):
    unit_id: str = Field(min_length=1, max_length=256)
    variant: Literal["control", "treatment"]
    exposed: bool = True
    day: int = Field(default=1, ge=1)
    segment: str = "all"
    metrics: dict[str, float | None]
    pre: dict[str, float | None] = Field(default_factory=dict)
    denominators: dict[str, float | None] = Field(default_factory=dict)

    @model_validator(mode="after")
    def positive_denominators(self) -> Self:
        if any(v is not None and v <= 0 for v in self.denominators.values()):
            raise ValueError("ratio denominators must be positive")
        return self
