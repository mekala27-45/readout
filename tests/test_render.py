"""The product and publication gates fail closed on empty or inconsistent evidence."""

import copy
import hashlib
import shutil
from pathlib import Path
from typing import Any

import pytest
from readout_render.renderer import ROOT, build_bundle, publish, render_manifest

from scripts.check_no_em_dash import check


@pytest.fixture
def manifest() -> dict[str, Any]:
    return {
        "experiment": {
            "key": "fixture",
            "name": "Fixture",
            "source": "simulated",
            "source_detail": {},
            "design": {
                "alpha": 0.05,
                "power": 0.8,
                "mde_relative": 0.04,
                "planned_n_per_arm": 100,
                "decision_rule": {"text": "Health must pass."},
            },
            "design_hash": "hash",
            "design_deviations": [],
        },
        "run": {
            "id": "run",
            "ran_at": "today",
            "results": {
                "primary": {
                    "key": "value",
                    "name": "Value",
                    "estimate": 0.4,
                    "ci_low": 0.2,
                    "ci_high": 0.6,
                    "relative": 0.04,
                    "relative_ci_low": 0.02,
                    "relative_ci_high": 0.06,
                    "n_control": 100,
                    "n_treatment": 100,
                    "p_value": 0.001,
                },
                "metrics": [],
                "decision": {"decision": "ship", "reason": "Primary passed"},
            },
        },
        "health": [
            {
                "id": "check",
                "analysis_run_id": "run",
                "kind": "srm",
                "status": "pass",
                "statistic": 0,
                "p_value": 1,
                "detail": {},
            }
        ],
        "decision": {"decision": "ship"},
    }


def test_renderer_clean_pass(manifest: dict[str, Any]) -> None:
    result = render_manifest(manifest)
    assert "## Health" in result["markdown"]
    assert "## Primary metric" in result["markdown"]
    assert result["markdown"].index("## Health") < result["markdown"].index("## Primary metric")
    assert "<table>" in result["html"]


def test_renderer_refuses_metrics_without_health(manifest: dict[str, Any]) -> None:
    manifest["health"] = []
    with pytest.raises(ValueError, match="health check"):
        render_manifest(manifest)


def test_renderer_refuses_empty() -> None:
    with pytest.raises(ValueError, match="stored experiment"):
        render_manifest({})


def test_blocked_readout_has_health_but_no_metrics(manifest: dict[str, Any]) -> None:
    manifest["health"][0]["status"] = "block"
    with pytest.raises(ValueError, match="Blocked"):
        render_manifest(manifest)
    manifest["run"]["results"]["primary"] = None
    manifest["decision"]["decision"] = "blocked"
    result = render_manifest(manifest)
    assert "## Health" in result["markdown"]
    assert "## Primary metric" not in result["markdown"]
    assert "**BLOCKED**" in result["markdown"]


def test_renderer_rejects_cross_run_health(manifest: dict[str, Any]) -> None:
    manifest["health"][0]["analysis_run_id"] = "another-run"
    with pytest.raises(ValueError, match="different analysis"):
        render_manifest(manifest)


def test_html_escapes_uploaded_names(manifest: dict[str, Any]) -> None:
    manifest["experiment"]["name"] = '<script>alert("bad")</script>'
    assert "<script>" not in render_manifest(manifest)["html"]


class Records:
    def __init__(self, manifest: dict[str, Any]) -> None:
        self.manifest = manifest

    def list_experiments(self) -> list[dict[str, Any]]:
        return [self.manifest["experiment"]] if self.manifest else []

    def latest_manifest(self, key: str) -> dict[str, Any]:
        return copy.deepcopy(self.manifest)

    def get_calibration(self) -> dict[str, Any]:
        return {"generated_at": "today", "measured": 0.123}


def test_claim_gate_pass_and_deliberate_violation(tmp_path: Path, manifest: dict[str, Any]) -> None:
    shutil.copytree(ROOT / "readouts/templates", tmp_path / "readouts/templates")
    folder = tmp_path / "docs/templates"
    folder.mkdir(parents=True)
    (folder / "README.md.jinja").write_text("Measured: {{ calibration.measured }}\n")
    repository = Records(manifest)
    assert publish(repository, tmp_path, write=True) == []
    assert publish(repository, tmp_path) == []
    (tmp_path / "README.md").write_text("Measured: 0.999\n")
    assert publish(repository, tmp_path)
    (tmp_path / "README.md").unlink()
    assert "Missing generated file" in publish(repository, tmp_path)[0]


def test_claim_gate_refuses_nothing() -> None:
    with pytest.raises(ValueError, match="No stored experiments"):
        build_bundle(Records({}))


def test_punctuation_gate_pass_violation_and_nothing(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="No text files"):
        check(tmp_path)
    template = tmp_path / "readout.md.jinja"
    template.write_text("Clean text.")
    assert check(tmp_path) == []
    template.write_text("Bad " + chr(0x2014) + " text.", encoding="utf-8")
    assert check(tmp_path) == ["readout.md.jinja:1"]


def test_renderer_refuses_forbidden_punctuation(manifest: dict[str, Any]) -> None:
    manifest["experiment"]["name"] = chr(0x2014)
    with pytest.raises(ValueError, match="Forbidden punctuation"):
        render_manifest(manifest)


def test_renderer_preserves_fdr_and_raw_sensitivity(manifest: dict[str, Any]) -> None:
    results = manifest["run"]["results"]
    metric = {
        **results["primary"],
        "segment": "returning",
        "p_adjusted": 0.012345,
        "significant": True,
        "significant_adjusted": True,
    }
    results["segments"] = [metric]
    results["guardrails"] = [
        {**metric, "margin": 0.05, "passed": True, "noninferiority_p_value": 1e-8}
    ]
    results["raw_metrics"] = [{**metric, "estimate": 0.3, "ci_low": 0.1, "ci_high": 0.5}]
    text = render_manifest(manifest)["markdown"]
    assert "Segment returning: Value" in text
    assert "0.012345" in text
    assert "Value without winsorization | 0.3000 [0.1000, 0.5000]" in text
    assert "1e-08" in text


def test_claim_gate_checks_stored_readout_digest(tmp_path: Path, manifest: dict[str, Any]) -> None:
    shutil.copytree(ROOT / "readouts/templates", tmp_path / "readouts/templates")
    folder = tmp_path / "docs/templates"
    folder.mkdir(parents=True)
    (folder / "README.md.jinja").write_text("Measured: {{ calibration.measured }}\n")
    repository = Records(manifest)
    text = render_manifest(manifest, tmp_path)["markdown"]
    manifest["decision"]["rendered_readout_sha256"] = hashlib.sha256(text.encode()).hexdigest()
    assert publish(repository, tmp_path, write=True) == []
    assert publish(repository, tmp_path) == []
    manifest["decision"]["rendered_readout_sha256"] = "incorrect"
    assert any("Stored readout digest differs" in error for error in publish(repository, tmp_path))
    manifest["decision"]["rendered_readout_sha256"] = None
    assert any("Missing stored readout digest" in error for error in publish(repository, tmp_path))
