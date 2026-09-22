import os
import shutil
import subprocess
import sys

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from readout_assign import assign
from scipy.stats import chisquare

EXPERIMENT = {
    "key": "demo",
    "salt": "salt-one",
    "variants": [{"name": "control", "allocation": 0.5}, {"name": "treatment", "allocation": 0.5}],
}


@given(st.text())
@settings(max_examples=100)
def test_assignment_is_deterministic(unit_id):
    first = assign(EXPERIMENT, unit_id)
    assert first == assign(dict(EXPERIMENT), unit_id)
    assert 0 <= first["bucket"] < 10000
    assert len(first["hash"]) == 64


def test_assignment_is_uniform():
    counts = np.bincount(
        [assign(EXPERIMENT, f"unit-{i}")["bucket"] for i in range(100000)], minlength=10000
    )
    assert chisquare(counts).pvalue > 0.001
    from readout_stats.health import srm

    verdict = srm({"treatment": int(sum(counts[:5000])), "control": int(sum(counts[5000:]))})
    assert verdict["status"] != "block"


def test_salt_decorrelates_experiments():
    other = {**EXPERIMENT, "salt": "salt-two"}
    first = [assign(EXPERIMENT, f"unit-{i}")["bucket"] for i in range(10000)]
    second = [assign(other, f"unit-{i}")["bucket"] for i in range(10000)]
    assert abs(float(np.corrcoef(first, second)[0, 1])) < 0.04


def test_ramp_is_stable():
    ramp = {
        **EXPERIMENT,
        "variants": [
            {"name": "control", "allocation": 0.9},
            {"name": "treatment", "allocation": 0.1},
        ],
    }
    for i in range(10000):
        if assign(ramp, str(i))["variant"] == "treatment":
            assert assign(EXPERIMENT, str(i))["variant"] == "treatment"


@pytest.mark.external
def test_assignment_is_deterministic_across_processes():
    if not shutil.which(sys.executable):
        pytest.skip("python_process_unavailable: current interpreter cannot be launched")
    code = "from readout_assign import assign; print(assign({'key':'demo','salt':'salt-one'},'restarted')['hash'])"
    first = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
        env=os.environ,
        timeout=30,
    )
    second = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
        env=os.environ,
        timeout=30,
    )
    assert first.stdout == second.stdout == assign(EXPERIMENT, "restarted")["hash"] + "\n"
