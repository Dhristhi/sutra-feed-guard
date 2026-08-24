from pathlib import Path

from feedguard.classification import classify_change


FIXTURES = Path(__file__).parents[1] / "fixtures" / "sutra-feed-guard-fixtures-v1"


def test_scenario_02_safe_additive_column() -> None:
    result = classify_change(
        baseline_path=FIXTURES / "historical" / "orders_2026-07-03.csv",
        observation_path=FIXTURES / "scenarios" / "02_safe_additive_column" / "input.csv",
        policy_path=FIXTURES / "contracts" / "accepted_policy.yaml",
    )
    assert result.disposition == "safe_additive"
    assert result.exit_code == 0
    assert result.affected_count == 100
    assert result.nonempty_new_value_count == 20


def test_scenario_03_removed_required_column() -> None:
    result = classify_change(
        baseline_path=FIXTURES / "historical" / "orders_2026-07-03.csv",
        observation_path=FIXTURES / "scenarios" / "03_removed_required_column" / "input.csv",
        policy_path=FIXTURES / "contracts" / "accepted_policy.yaml",
    )
    assert result.disposition == "breaking"
    assert result.exit_code == 3
    assert result.affected_count == 100
    assert "required_field_removed" in result.reason_codes


def test_scenario_04_duplicate_primary_key() -> None:
    result = classify_change(
        baseline_path=FIXTURES / "historical" / "orders_2026-07-03.csv",
        observation_path=FIXTURES / "scenarios" / "04_duplicate_primary_key" / "input.csv",
        policy_path=FIXTURES / "contracts" / "accepted_policy.yaml",
    )
    assert result.disposition == "breaking"
    assert result.exit_code == 3
    assert result.affected_count == 2
    assert "duplicate_primary_key" in result.reason_codes


def test_scenario_05_identifier_leading_zero() -> None:
    result = classify_change(
        baseline_path=FIXTURES / "historical" / "orders_2026-07-03.csv",
        observation_path=FIXTURES / "scenarios" / "05_identifier_leading_zero" / "input.csv",
        policy_path=FIXTURES / "contracts" / "accepted_policy.yaml",
    )
    assert result.disposition == "breaking"
    assert result.exit_code == 3
    assert result.affected_count == 12
    assert "identifier_format_violation" in result.reason_codes


def test_scenario_06_rupees_to_paise_semantic_trap() -> None:
    result = classify_change(
        baseline_path=FIXTURES / "historical" / "orders_2026-07-03.csv",
        observation_path=FIXTURES / "scenarios" / "06_rupees_to_paise_semantic_trap" / "input.csv",
        policy_path=FIXTURES / "contracts" / "accepted_policy.yaml",
    )
    assert result.disposition == "breaking"
    assert result.exit_code == 3
    assert result.affected_count == 100
    assert "unit_semantics_changed" in result.reason_codes


def test_scenario_07_accepted_field_alias() -> None:
    result = classify_change(
        baseline_path=FIXTURES / "historical" / "orders_2026-07-03.csv",
        observation_path=FIXTURES / "scenarios" / "07_accepted_field_alias" / "input.csv",
        policy_path=FIXTURES / "contracts" / "accepted_policy.yaml",
    )
    assert result.disposition == "known_variant"
    assert result.exit_code == 0
    assert result.affected_count == 100
    assert "accepted_field_alias" in result.reason_codes


def test_scenario_08_malformed_partial_delivery() -> None:
    result = classify_change(
        baseline_path=FIXTURES / "historical" / "orders_2026-07-03.csv",
        observation_path=FIXTURES / "scenarios" / "08_malformed_partial_delivery" / "input.csv",
        policy_path=FIXTURES / "contracts" / "accepted_policy.yaml",
    )
    assert result.disposition == "invalid_observation"
    assert result.exit_code == 4
    assert result.affected_count is None
    assert "partial_or_malformed_delivery" in result.reason_codes
