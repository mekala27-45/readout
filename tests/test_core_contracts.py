import pytest
from pydantic import ValidationError
from readout_core.hashing import content_hash, hash_unit_id
from readout_core.logging import redact_unit_ids
from readout_core.models import Design, ExperimentCreate, Metric, UnitRow


def test_strict_contract_rejects_unknown_and_nonfinite_values():
    with pytest.raises(ValidationError):
        Design(alpha=0.05, silent_option=True)
    with pytest.raises(ValidationError):
        Design(alpha="0.05")
    with pytest.raises(ValidationError):
        UnitRow(unit_id="u", variant="control", metrics={"value": float("nan")})


@pytest.mark.parametrize(
    "updates",
    [
        {"primary_metric_key": "absent"},
        {
            "variants": [
                {"name": "control", "allocation": 0.3},
                {"name": "treatment", "allocation": 0.3},
            ]
        },
        {"metrics": [{"key": "value", "name": "First"}, {"key": "value", "name": "Second"}]},
        {"secondary_metric_keys": ["value"]},
        {"guardrail_metric_keys": ["value"], "secondary_metric_keys": ["value"]},
        {
            "variants": [
                {"name": "control", "allocation": 0.5},
                {"name": "control", "allocation": 0.5},
            ]
        },
    ],
)
def test_design_rejects_incoherent_registration(updates):
    with pytest.raises(ValidationError):
        Design.model_validate(updates)


def test_normalized_rows_and_metric_policies():
    with pytest.raises(ValidationError):
        UnitRow(
            unit_id="u", variant="treatment", metrics={"value": 1.0}, denominators={"value": 0.0}
        )
    with pytest.raises(ValidationError):
        Metric(key="value", name="Value", winsor_upper_percentile=0.2)
    assert ExperimentCreate(key="demo", name="Demo").design.alpha == 0.05


def test_canonical_hash_and_logging_redaction():
    assert content_hash({"a": 1, "b": 2}) == content_hash({"b": 2, "a": 1})
    result = redact_unit_ids(
        None, "info", {"unit_id": "private", "unit_ids": ["other"], "event": "assigned"}
    )
    assert "unit_id" not in result and "unit_ids" not in result
    assert result["unit_id_hash"] == hash_unit_id("private")
    assert result["unit_id_hashes"] == [hash_unit_id("other")]
