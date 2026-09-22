"""Boundary checks that bind decisions to persisted health and registered horizons."""

import copy

import pytest
from readout_api.repository import ConflictError, Repository
from readout_sim import design_for, generate
from readout_stats.decision import decide
from readout_stats.engine import analyze
from readout_stats.health import check_health
from readout_stats.power import achieved_power, required_sample_size


def test_health_fingerprint_covers_outcomes_covariates_and_design():
    design, rows = design_for("null"), generate("null", seed=42)
    health = check_health(design, rows)
    for field in ("metrics", "pre"):
        changed = copy.deepcopy(rows)
        changed[0][field]["value"] = None
        with pytest.raises(ValueError, match="different observation"):
            analyze(design, changed, health)
    changed_design = {**design, "alpha": 0.04}
    with pytest.raises(ValueError, match="different experiment design"):
        analyze(changed_design, rows, health)
    incomplete_health = copy.deepcopy(health)
    incomplete_health[0].pop("data_digest")
    with pytest.raises(ValueError, match="different observation"):
        analyze(design, rows, incomplete_health)


def test_missing_guardrail_blocks_but_missing_secondary_is_explicitly_unavailable():
    design, rows = design_for("null"), generate("null", seed=42)
    for row in rows:
        row["metrics"]["retained"] = None
    result = analyze(design, rows, check_health(design, rows))
    assert result["primary"]
    assert result["secondary"] == []
    assert result["unavailable_metrics"][0]["key"] == "retained"
    assert any("Unavailable metric retained" in note for note in result["limitations"])
    for row in rows:
        row["metrics"]["quality"] = None
    result = analyze(design, rows, check_health(design, rows))
    assert result["decision"]["decision"] == "blocked"
    assert result["metrics"] == []


def test_missing_ratio_denominator_is_a_health_failure():
    design, rows = design_for("ratio_metric"), generate("ratio_metric", seed=42)
    for row in rows:
        row["denominators"] = {}
    result = analyze(design, rows, check_health(design, rows))
    assert result["decision"]["decision"] == "blocked"


def test_provisional_ship_cannot_be_finalized(tmp_path):
    repo = Repository(f"sqlite:///{tmp_path / 'horizon.db'}")
    data = [
        {
            "unit_id": str(i),
            "variant": "control" if i % 2 == 0 else "treatment",
            "metrics": {"value": 10.0 + i % 3 + (i % 2) * 4},
        }
        for i in range(40)
    ]
    for key, planned in (("provisional", 1000), ("complete", 20)):
        repo.create_experiment(
            {"key": key, "name": key, "status": "running", "design": {"planned_n_per_arm": planned}}
        )
        repo.import_rows(key, data)
        run = repo.analyze(key)
        recommendation = run["results"]["decision"]
        assert recommendation["decision"] == "ship"
        assert recommendation["provisional"] == (key == "provisional")
        if key == "provisional":
            with pytest.raises(ConflictError, match="registered sample horizon"):
                repo.decide(key, run["id"])
        else:
            assert repo.decide(key, run["id"])["decision"] == "ship"
    repo.close()


def test_unequal_allocation_controls_projection_extension_and_horizon():
    design = {
        **design_for("at_mde"),
        "guardrail_metric_keys": [],
        "secondary_metric_keys": [],
        "planned_n_per_arm": 100,
        "metrics": [{"key": "value", "name": "Value", "kind": "mean"}],
        "variants": [
            {"name": "control", "allocation": 0.25},
            {"name": "treatment", "allocation": 0.75},
        ],
    }
    primary = {
        "ci_low": -0.1,
        "ci_high": 0.7,
        "estimate": 0.3,
        "n_control": 100,
        "n_treatment": 300,
    }
    result = decide(design, primary, [], [{"status": "pass"}])
    required = required_sample_size(10, 0.03, standard_deviation=3, allocation=0.75)
    assert result["decision"] == "extend"
    assert result["additional_n_by_arm"] == {
        "control": max(required["n_control"] - 100, 10),
        "treatment": max(required["n_treatment"] - 300, 30),
    }
    assert result["planned_n_by_arm"] == {"control": 100, "treatment": 300}
    assert not result["provisional"]
    assert decide(design, {**primary, "n_treatment": 299}, [], [{"status": "pass"}])["provisional"]
    rows = [
        {
            "unit_id": str(i),
            "variant": "control" if i < 100 else "treatment",
            "metrics": {"value": float(10 + i % 7)},
            "exposed": True,
            "day": 1,
        }
        for i in range(400)
    ]
    analyzed = analyze(design, rows, check_health(design, rows))
    expected = achieved_power(100, 10, 0.04, allocation=0.75, standard_deviation=3)
    assert analyzed["primary"]["design_effect_projected_power"] == pytest.approx(expected)
