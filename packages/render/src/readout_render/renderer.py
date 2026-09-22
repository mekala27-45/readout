"""One health-gated renderer for product readouts and repository claims."""

from __future__ import annotations

import difflib
import hashlib
import html
import json
from pathlib import Path
from typing import Any, Protocol

import markdown
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).resolve().parents[4]


class EvidenceRepository(Protocol):
    def list_experiments(self) -> list[dict[str, Any]]: ...
    def latest_manifest(self, key: str) -> dict[str, Any]: ...
    def get_calibration(self) -> dict[str, Any]: ...


def number(value: Any, places: int = 4) -> str:
    if value is None:
        return "unavailable"
    return f"{float(value):,.{places}f}"


def percent(value: Any, places: int = 2) -> str:
    if value is None:
        return "unavailable"
    return f"{float(value) * 100:.{places}f}%"


def pvalue(value: Any) -> str:
    if value is None:
        return "unavailable"
    return f"{float(value):.3g}" if 0 < float(value) < 0.0001 else number(value, 6)


def interval(metric: dict[str, Any], relative: bool = False) -> str:
    prefix = "relative_" if relative else ""
    formatter = percent if relative else number
    estimate = metric.get("relative" if relative else "estimate")
    return f"{formatter(estimate)} [{formatter(metric.get(prefix + 'ci_low'))}, {formatter(metric.get(prefix + 'ci_high'))}]"


def band(value: dict[str, Any]) -> str:
    return (
        f"{percent(value.get('rate'))} [{percent(value.get('low'))}, {percent(value.get('high'))}]"
    )


def _environment(root: Path) -> Environment:
    environment = Environment(
        loader=FileSystemLoader(str(root)),
        undefined=StrictUndefined,
        autoescape=False,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    environment.filters.update(
        number=number, percent=percent, interval=interval, band=band, pvalue=pvalue
    )
    environment.filters["json"] = lambda value: json.dumps(value, indent=2, sort_keys=True)
    return environment


def _check_text(text: str) -> None:
    if chr(0x2014) in text:
        raise ValueError("Forbidden punctuation in rendered output")


def validate_manifest(manifest: dict[str, Any]) -> None:
    if not manifest or not manifest.get("experiment") or not manifest.get("run"):
        raise ValueError("Cannot render without a stored experiment and analysis run")
    health = manifest.get("health")
    if not health or not any(
        str(row.get("kind", row.get("check", ""))).startswith("srm") for row in health
    ):
        raise ValueError("Cannot render metrics without a health check row")
    run = manifest["run"]
    for row in health:
        if row.get("analysis_run_id", run["id"]) != run["id"]:
            raise ValueError("Health check belongs to a different analysis run")
    results = run.get("results", manifest.get("results", {}))
    blocked = any(row["status"] == "block" for row in health)
    if blocked and (results.get("metrics") or results.get("primary")):
        raise ValueError("Blocked runs must not contain metric results")
    if not manifest.get("decision") and not results.get("decision"):
        raise ValueError("A decision record is required to render")


def render_manifest(manifest: dict[str, Any], root: Path = ROOT) -> dict[str, str]:
    validate_manifest(manifest)
    experiment = manifest["experiment"]
    results = manifest["run"].get("results", manifest.get("results", {}))
    context = {
        **manifest,
        "results": results,
        "design": experiment.get("registered_design") or experiment.get("design", {}),
        "decision": manifest.get("decision") or results["decision"],
        "blocked": any(row["status"] == "block" for row in manifest["health"]),
    }
    text = _environment(root).get_template("readouts/templates/readout.md.jinja").render(context)
    _check_text(text)
    body = markdown.markdown(html.escape(text), extensions=["tables", "fenced_code"])
    # Escape untrusted user content before Markdown conversion; the template uses escape filters.
    title = html.escape(experiment["name"])
    page = (
        _environment(root)
        .get_template("readouts/templates/readout.html.jinja")
        .render(
            title=title,
            body=body,
        )
    )
    _check_text(page)
    return {"markdown": text, "html": page}


def build_bundle(repository: EvidenceRepository) -> dict[str, Any]:
    registry = repository.list_experiments()
    experiments = [
        repository.latest_manifest(row["key"])
        for row in registry
        if row.get("status") not in {"draft", "running"}
    ]
    if not experiments:
        raise ValueError("No stored experiments")
    for experiment in experiments:
        validate_manifest(experiment)
    calibration = repository.get_calibration()
    if not calibration:
        raise ValueError("No measured calibration records")
    return {
        "schema_version": "1",
        "generated_at": calibration.get("computed_at", calibration.get("generated_at")),
        "experiments": experiments,
        "registry": registry,
        "calibration": calibration,
        "pricepoint": calibration.get("pricepoint", {}),
        "assignment": calibration.get("assignment", {}),
    }


def publish(repository: EvidenceRepository, root: Path = ROOT, write: bool = False) -> list[str]:
    """Re-query records, render whole files, and reject any changed byte of text."""
    bundle = build_bundle(repository)
    if not list((root / "docs/templates").glob("*.jinja")):
        raise ValueError("No document templates")
    rendered: dict[Path, str] = {}
    errors = []
    environment = _environment(root)
    for template in sorted((root / "docs/templates").glob("*.jinja")):
        rendered[root / template.name.removesuffix(".jinja")] = environment.get_template(
            template.relative_to(root).as_posix()
        ).render(**bundle)
    for manifest in bundle["experiments"]:
        readout = render_manifest(manifest, root)
        key = manifest["experiment"]["key"]
        decision = manifest.get("decision") or {}
        if not write and "rendered_readout_sha256" in decision:
            stored_digest = decision["rendered_readout_sha256"]
            actual_digest = hashlib.sha256(readout["markdown"].encode("utf-8")).hexdigest()
            if not stored_digest:
                errors.append(f"Missing stored readout digest: {key}")
            elif stored_digest != actual_digest:
                errors.append(f"Stored readout digest differs from rendered evidence: {key}")
        for extension, name in [("md", "markdown"), ("html", "html")]:
            rendered[root / "readouts" / f"{key}.{extension}"] = readout[name]
            rendered[root / "web/public/readouts" / f"{key}.{extension}"] = readout[name]
    rendered[root / "web/public/results/bundle.json"] = (
        json.dumps(bundle, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )
    for path, expected in rendered.items():
        _check_text(expected)
        if write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8", newline="\n")
        elif not path.exists():
            errors.append(f"Missing generated file: {path.relative_to(root)}")
        elif path.read_text(encoding="utf-8") != expected:
            actual = path.read_text(encoding="utf-8")
            differences = list(
                difflib.unified_diff(
                    actual.splitlines(),
                    expected.splitlines(),
                    fromfile=str(path),
                    tofile="stored-record render",
                    lineterm="",
                )
            )
            errors.append("\n".join(differences[:35]))
    return errors
