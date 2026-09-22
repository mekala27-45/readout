import pytest
from readout_sim import design_for, generate, scenarios


@pytest.mark.parametrize("scenario", list(scenarios()))
def test_seeded_scenarios_are_reproducible(scenario):
    first = generate(scenario, 45, n_per_arm=50)
    assert first == generate(scenario, 45, n_per_arm=50)
    assert first != generate(scenario, 46, n_per_arm=50)
    assert all(row["unit_id"] and row["day"] >= 1 for row in first)


def test_simulation_rejects_unknown_scenario_and_bad_probability():
    with pytest.raises(ValueError):
        generate("unknown")
    with pytest.raises(ValueError):
        design_for("unknown")
    with pytest.raises(ValueError):
        generate("null", exposure_rate=2)
