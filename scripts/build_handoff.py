"""Print the requested delivery tables and tree from canonical persisted evidence."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from readout_api.repository import Repository
from readout_render.renderer import band, number, percent

from scripts.restore_evidence import ROOT, restore


def main() -> None:
    with TemporaryDirectory(prefix="readout-handoff-") as directory:
        database = Path(directory) / "evidence.db"
        restore(database)
        repository = Repository("sqlite:///" + database.as_posix())
        try:
            calibration = repository.get_calibration()
            cookie = repository.latest_manifest("cookie_cats")
        finally:
            repository.close()
    paths = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.splitlines()
    paths = sorted(set(p for p in paths if not p.startswith("docs/demo-frames/")))
    tree = "\n".join(paths)
    lines = [
        "# Delivery record",
        "",
        "## File tree",
        "",
        "```text",
        "readout/",
        *["  " + path for path in paths],
        "```",
        "",
        "## Peeking calibration",
        "",
        "Source: simulated true null; daily checks. All rate intervals are Monte Carlo Wilson intervals.",
        "",
        "| Checks | Naive rejection rate | Sequential rejection rate |",
        "| ---: | --- | --- |",
    ]
    lines.extend(
        f"| {row['day']} | {band(row['naive'])} | {band(row['sequential'])} |"
        for row in calibration["peeking"]
    )
    lines.extend(
        [
            "",
            "## Empirical power",
            "",
            "| Planned sample multiple | Units per arm | Empirical power | Theoretical power |",
            "| ---: | ---: | --- | ---: |",
        ]
    )
    lines.extend(
        f"| {row['multiple']} | {row['n_per_arm']} | {band(row)} | {percent(row['theoretical'])} |"
        for row in calibration["power"]
    )
    lines.extend(
        [
            "",
            "## SRM sensitivity",
            "",
            "| Units per arm before defect | Treatment dropout | Blocking probability |",
            "| ---: | ---: | --- |",
        ]
    )
    lines.extend(
        f"| {row['n_per_arm']} | {percent(row['dropout'])} | {band(row)} |"
        for row in calibration["srm"]
    )
    reproduction = calibration["pricepoint"]
    lines.extend(
        [
            "",
            "## Pricepoint reproduction",
            "",
            f"Calculated {reproduction['n_per_arm']} per arm; published {reproduction['published_n_per_arm']}. Residual SD {number(reproduction['standard_deviation'], 8)}; log-scale effect {number(reproduction['effect_absolute'], 8)}. {reproduction['documentation_gap']}",
            "",
            "## Cookie Cats health",
            "",
        ]
    )
    for check in cookie["health"]:
        if check.get("check", "").startswith("srm"):
            lines.append(
                f"- {check['check']}: observed {check['observed']}; expected {check['expected']}; p {number(check['p_value'], 6)}; conventional {check['conventional_verdict']}; blocking {check['blocking_verdict']}."
            )
    decision = cookie["run"]["results"]["decision"]
    lines.extend(
        [
            "",
            "## Cookie Cats decision",
            "",
            f"**{decision['decision'].upper()}**. {decision['reason']}",
            "",
            "> " + cookie["experiment"]["registered_design"]["decision_rule"]["text"],
            "",
            "## Remaining dependencies and limits",
            "",
            "GitHub Pages serves the canonical bundle. The local live API and CSV upload were verified in a real browser. Public Fly/Neon API deployment remains unverified: no provider configuration was available, Fly was signed out, and a general Fly free tier is no longer offered. No billable resources were provisioned.",
            "",
            "Windows SciPy modules were blocked by Application Control; numerical runs and Postgres checks completed in Linux Docker. Cookie Cats has no actual gate-exposure records, timestamps or pre-period covariates; its protocol is retrospective. The mandated dark palette has one documented inherited color-vision separation exception, with redundant marks and labels. Optional stretch modules were deferred.",
            "",
        ]
    )
    report = "\n".join(lines)
    (ROOT / "BUILD_REPORT.md").write_text(report, encoding="utf-8", newline="\n")
    (ROOT / "docs/tree.txt").write_text("readout/\n" + tree + "\n", encoding="utf-8")
    final = calibration["peeking"][-1]
    post = f"# LinkedIn draft: calibration first\n\nI ran {final['naive']['total']:,} simulated A/B tests with no difference between groups and checked them daily for {final['day']} days. Naive testing called a winner in {percent(final['naive']['rate'], 1)} of experiments. A calibrated normal-mixture sequential method rejected in {percent(final['sequential']['rate'], 1)}.\n\nThose simulation results, with uncertainty intervals, are published alongside the code. The sequential implementation uses an estimated-variance approximation, so the measured regimes and its limits are stated explicitly.\n\nThe platform also checks randomization health before analyzing a metric, freezes experiment designs, tests guardrails, and renders a decision document from stored records. Its public Cookie Cats readout explains exactly what the dataset can and cannot support.\n\nhttps://mekala27-45.github.io/readout/\n\nhttps://github.com/mekala27-45/readout\n\nDraft only; not posted.\n"
    (ROOT / "docs/linkedin-draft.md").write_text(post, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "report": "BUILD_REPORT.md",
                "files": len(paths),
                "peeking_final": final,
                "pricepoint": reproduction,
                "cookie_decision": decision,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
