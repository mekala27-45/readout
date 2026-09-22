import pytest
from readout_calibrate.harness import binomial, run_calibration


@pytest.fixture(scope="module")
def calibration():
    return run_calibration(full=True)


@pytest.mark.calibration
def test_sequential_false_positives_with_monte_carlo_tolerance(calibration):
    for key in ["peeking", "peeking_proportion"]:
        final = calibration[key][-1]
        assert len(calibration[key]) == 30 and final["sequential"]["total"] >= 1000
        # A one-sided claim of control: the lower confidence bound must not exceed alpha.
        assert final["sequential"]["low"] <= 0.05
        assert final["naive"]["low"] > 0.05


@pytest.mark.calibration
def test_empirical_power_at_planned_sample(calibration):
    for key in ["power", "power_proportion"]:
        row = next(r for r in calibration[key] if r["multiple"] == 1)
        assert row["total"] >= 500
        assert row["low"] <= 0.8 <= row["high"]


@pytest.mark.calibration
def test_cuped_recovers_truth_and_rho_squared(calibration):
    row = calibration["cuped"]
    assert row["ci_low"] <= 0.4 <= row["ci_high"]
    # Paired bootstrap of estimates across seeds uses no engine variance formula.
    assert row["empirical_low"] <= 0.64 <= row["empirical_high"]


@pytest.mark.calibration
def test_delta_coverage_with_binomial_uncertainty(calibration):
    row = calibration["delta"]
    assert row["delta"]["low"] <= 0.95 <= row["delta"]["high"]
    assert row["naive"]["high"] < 0.95


@pytest.mark.calibration
def test_srm_dropout_sensitivity(calibration):
    row = next(r for r in calibration["srm"] if r["n_per_arm"] == 10000 and r["dropout"] == 0.1)
    assert row["low"] > 0.95


@pytest.mark.calibration
def test_exposure_dilution(calibration):
    row = calibration["exposure"]
    assert row["assigned"]["ci_low"] <= 0.24 <= row["assigned"]["ci_high"]
    assert row["exposed"]["ci_low"] <= 0.4 <= row["exposed"]["ci_high"]
    assert row["assigned"]["estimate"] < row["exposed"]["estimate"]


def test_binomial_interval_refuses_empty():
    with pytest.raises(ValueError):
        binomial(0, 0)
