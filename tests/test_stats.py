"""Independent cross checks and the health-first contract."""

import copy
import math

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from readout_calibrate.harness import pricepoint_reproduction
from readout_sim import design_for, generate
from readout_stats import cuped, delta, fdr, fixed, guardrails, power, sequential
from readout_stats.decision import decide
from readout_stats.engine import analyze
from readout_stats.health import check_health, srm
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportions_ztest
from statsmodels.stats.weightstats import ttest_ind


def test_srm_gate_clean_pass():
    rows, design = generate("null", seed=42), design_for("null")
    health = check_health(design, rows)
    assert all(r["status"] == "pass" for r in health)
    assert analyze(design, rows, health)["primary"] is not None


def test_srm_gate_deliberate_violation_names_short_arm():
    rows, design = generate("srm_dropout"), design_for("srm_dropout")
    records = check_health(design, rows)
    assert records[0]["status"] == "block"
    assert records[0]["short_arm"] == "treatment"
    assert records[0]["short_by"] > 0
    result = analyze(design, rows, records)
    assert result["health"] and result["metrics"] == [] and result["primary"] is None
    assert result["decision"]["decision"] == "blocked"


def test_srm_gate_refuses_nothing():
    records = check_health(design_for("null"), [])
    assert records[0]["status"] == "block" and records[0]["detail"] == "no data"
    assert analyze(design_for("null"), [], records)["decision"]["decision"] == "blocked"


def test_engine_refuses_missing_or_stale_health():
    rows, design = generate("null"), design_for("null")
    with pytest.raises(ValueError, match="health"):
        analyze(design, rows, [])
    health = check_health(design, rows)
    rows[0]["exposed"] = False
    with pytest.raises(ValueError, match="different"):
        analyze(design, rows, health)


def test_health_validates_units_and_reports_missingness():
    rows, design = generate("null"), design_for("null")
    with pytest.raises(ValueError, match="unique"):
        check_health(design, rows + rows[:1])
    invalid = copy.deepcopy(rows)
    invalid[0]["variant"] = "other"
    with pytest.raises(ValueError, match="Unknown"):
        check_health(design, invalid)
    for row in rows:
        if row["variant"] == "treatment":
            row["metrics"]["value"] = None
    assert any(
        h["status"] == "block" and h.get("metric_key") == "value"
        for h in check_health(design, rows)
    )


def test_proportions_crosscheck_statsmodels():
    c, t = np.r_[np.ones(400), np.zeros(600)], np.r_[np.ones(460), np.zeros(540)]
    result = fixed.compare(c, t, "proportion")
    _, p = proportions_ztest([t.sum(), c.sum()], [len(t), len(c)])
    assert result["p_value"] == pytest.approx(p)
    assert result["se"] == pytest.approx(math.sqrt(0.4 * 0.6 / 1000 + 0.46 * 0.54 / 1000))


def test_welch_crosscheck_statsmodels():
    rng = np.random.default_rng(73)
    c, t = rng.normal(10, 3, 100), rng.normal(10.4, 5, 170)
    result = fixed.compare(c, t)
    _, p, df = ttest_ind(t, c, usevar="unequal")
    assert result["p_value"] == pytest.approx(p)
    assert result["df"] == pytest.approx(df)


@given(
    st.lists(
        st.floats(min_value=-1e3, max_value=1e3, allow_nan=False, allow_infinity=False),
        min_size=2,
        max_size=80,
    ),
    st.lists(
        st.floats(min_value=-1e3, max_value=1e3, allow_nan=False, allow_infinity=False),
        min_size=2,
        max_size=80,
    ),
)
@settings(max_examples=50)
def test_every_interval_contains_estimate_and_p_is_a_probability(c, t):
    result = fixed.compare(c, t)
    assert result["ci_low"] <= result["estimate"] <= result["ci_high"]
    assert 0 <= result["p_value"] <= 1


def test_fixed_input_edge_cases():
    with pytest.raises(ValueError):
        fixed.compare([], [1, 2])
    with pytest.raises(ValueError):
        fixed.compare([0, 2], [0, 1], "proportion")
    with pytest.raises(ValueError):
        fixed.compare([0, 1], [0, 1], "ratio")
    result = fixed.compare([0, 0, 0], [0, 0, 0])
    assert result["relative"] is None and result["p_value"] == 1
    assert fixed.compare([1, 1], [2, 2])["p_value"] == 0


def test_fdr_crosscheck_statsmodels():
    p = [0.001, 0.025, 0.04, 0.2, 0.89]
    assert fdr.benjamini_hochberg(p) == pytest.approx(multipletests(p, method="fdr_bh")[1])
    assert fdr.benjamini_hochberg([]) == []
    with pytest.raises(ValueError):
        fdr.benjamini_hochberg([2])


def test_cityflow_port_excludes_unavailable_tests_and_preserves_boundary():
    from readout_stats.cityflow_fdr import benjamini_hochberg

    result = benjamini_hochberg([0.025, 0.05, np.nan], q=0.05)
    assert result.n_comparisons == 2 and result.n_rejected == 2
    assert result.rejected.tolist() == [True, True, False]
    assert np.isnan(result.adjusted[-1])
    with pytest.raises(ValueError):
        benjamini_hochberg([0.5], q=0)


def test_reproduces_pricepoint_power():
    result = pricepoint_reproduction()
    assert result["n_per_arm"] == result["published_n_per_arm"] == 820
    effect = abs(-1.5 * math.log1p(0.1))
    independent_n = NormalIndPower().solve_power(
        effect_size=effect / result["standard_deviation"], alpha=0.05, power=0.8, ratio=1
    )
    assert math.ceil(independent_n) == 820


@given(st.floats(min_value=0.005, max_value=0.3), st.floats(min_value=0.6, max_value=0.95))
def test_sample_size_monotone(mde, requested_power):
    base = power.required_sample_size(10, mde, power=requested_power)
    assert (
        power.required_sample_size(10, mde * 1.2, power=requested_power)["n_per_arm"]
        <= base["n_per_arm"]
    )
    assert (
        power.required_sample_size(10, mde, power=(requested_power + 1) / 2)["n_per_arm"]
        >= base["n_per_arm"]
    )


def test_power_calculator_allocation_and_inverse():
    planned = power.required_sample_size(
        10, 0.04, standard_deviation=3, allocation=0.3, daily_units=300
    )
    assert planned["n_treatment"] == math.ceil(planned["n_control"] * 0.3 / 0.7)
    assert planned["days"] > 0
    inverted = power.minimum_detectable_effect(884, 10, standard_deviation=3)
    assert inverted == pytest.approx(0.04, abs=0.0001)
    for bad in [{"baseline": 0}, {"allocation": 0}, {"daily_units": -1}, {"kind": "ratio"}]:
        with pytest.raises(ValueError):
            power.design_power({"baseline": 10, "mde_relative": 0.04, **bad})
    with pytest.raises(ValueError):
        power.required_sample_size(0.99, 0.2, kind="proportion")


def test_cuped_zero_covariance_returns_unadjusted():
    c, t, pre = (
        np.array([1.0, 2.0, 1.0, 2.0]),
        np.array([2.0, 3.0, 2.0, 3.0]),
        np.array([-1.0, -1.0, 1.0, 1.0]),
    )
    result = cuped.adjust(c, t, pre, pre)
    assert result["theta"] == 0
    assert result["adjusted"]["estimate"] == result["unadjusted"]["estimate"]
    assert result["variance_reduction"] == 0
    with pytest.raises(ValueError):
        cuped.adjust(c, t, pre[:2], pre)


def test_delta_preserves_unit_correlation_and_rejects_bad_denominator():
    c, t, d = [0, 0, 5, 5], [0, 5, 5, 5], [5, 5, 5, 5]
    result = delta.compare_ratio(c, t, d, d)
    naive = delta.naive_session_interval(c, t, d, d)
    assert result["se"] > naive["se"]
    with pytest.raises(ValueError):
        delta.compare_ratio(c, t, [0, 5, 5, 5], d)


def test_sequential_running_minimum_and_algebra():
    estimate = [0.1, 0.2, 0.3]
    variance = [0.04, 0.02, 0.01]
    result = sequential.monitor_summaries(estimate, variance)
    assert all(a >= b for a, b in zip(result["p_value"], result["p_value"][1:], strict=False))
    v, d, tau = 0.01, 0.3, 0.16
    lr = math.sqrt(v / (v + tau)) * math.exp(d * d * tau / (2 * v * (v + tau)))
    assert result["log_likelihood_ratio"][-1] == pytest.approx(math.log(lr))
    for point, lower, upper in zip(estimate, result["ci_low"], result["ci_high"], strict=True):
        assert lower <= point <= upper
    with pytest.raises(ValueError):
        sequential.monitor_summaries([], [])
    assert not sequential.monitor([1, 2], [2, 3], [1, 1], [1, 1])["applicable"]


def test_guardrails_direction_and_noninferiority():
    metric = fixed.compare([100, 101, 99] * 100, [95, 96, 94] * 100)
    assert not guardrails.evaluate(metric, {"guardrail_margin_relative": 0.02})["passed"]
    assert guardrails.evaluate(
        metric, {"guardrail_margin_relative": 0.02, "direction": "lower_is_better"}
    )["passed"]
    with pytest.raises(ValueError):
        guardrails.evaluate(metric, {})


@pytest.mark.parametrize(
    "interval,guardrails_list,expected",
    [
        ((0.1, 0.7), [], "ship"),
        ((-0.1, 0.2), [], "no_ship"),
        ((-0.1, 0.6), [], "extend"),
        ((0.1, 0.7), [{"passed": False}], "no_ship"),
    ],
)
def test_decision_rule_branches(interval, guardrails_list, expected):
    primary = {
        "ci_low": interval[0],
        "ci_high": interval[1],
        "estimate": sum(interval) / 2,
        "n_control": 200,
        "n_treatment": 200,
    }
    assert (
        decide(design_for("at_mde"), primary, guardrails_list, [{"status": "pass"}])["decision"]
        == expected
    )


def test_guardrail_hit_overrides_primary_ship():
    design, rows = design_for("guardrail_hit"), generate("guardrail_hit")
    result = analyze(design, rows, check_health(design, rows))
    assert result["primary"]["ci_low"] > 0
    assert result["decision"]["decision"] == "no_ship"


def test_lower_is_better_decision_and_missing_primary():
    design = design_for("at_mde")
    design["metrics"][0]["direction"] = "lower_is_better"
    primary = {
        "ci_low": -0.7,
        "ci_high": -0.1,
        "estimate": -0.4,
        "n_control": 200,
        "n_treatment": 200,
    }
    assert decide(design, primary, [], [{"status": "pass"}])["decision"] == "ship"
    assert decide(design, None, [], [{"status": "pass"}])["decision"] == "blocked"


def test_outlier_policy_recorded_and_no_preperiod_or_time_is_honest():
    design, rows = design_for("null"), generate("null")
    design["metrics"][0]["winsor_upper_percentile"] = 0.99
    design["has_timestamps"] = False
    rows[0]["metrics"]["value"] = 100000
    for row in rows:
        row["pre"] = {}
    result = analyze(design, rows, check_health(design, rows))
    assert result["primary"]["outlier_policy"]["threshold"] < 100000
    assert result["primary_without_outlier_policy"]["estimate"] != result["primary"]["estimate"]
    assert not result["cuped"]["applicable"] and not result["sequential"]["applicable"]


def test_srm_thresholds_match_chisquare():
    observed = {"control": 44700, "treatment": 45500}
    result = srm(observed)
    assert result["p_value"] == pytest.approx(stats.chisquare(list(observed.values())).pvalue)
    assert result["status"] == "warn"
    with pytest.raises(ValueError):
        srm(observed, {"control": 0.2, "treatment": 0.2})
