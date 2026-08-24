from pathlib import Path

from feedguard.observation import load_observation


FIXTURES = Path(__file__).parents[1] / "fixtures" / "sutra-feed-guard-fixtures-v1"


def test_csv_and_json_baselines_have_identical_canonical_digest() -> None:
    csv_observation = load_observation(FIXTURES / "historical" / "orders_2026-07-03.csv")
    json_observation = load_observation(FIXTURES / "historical" / "orders_2026-07-03.json")

    assert csv_observation.format == "csv"
    assert json_observation.format == "json"
    assert csv_observation.row_count == 100
    assert csv_observation.fields == (
        "order_id",
        "customer_id",
        "order_date",
        "exported_at",
        "amount",
        "currency",
        "status",
        "country_code",
        "source_system",
    )
    assert csv_observation.canonical_digest == json_observation.canonical_digest


def test_scenario_01_unchanged_matches_baseline_digest() -> None:
    baseline_csv = load_observation(FIXTURES / "historical" / "orders_2026-07-03.csv")
    scenario_csv = load_observation(FIXTURES / "scenarios" / "01_unchanged" / "input.csv")
    scenario_json = load_observation(FIXTURES / "scenarios" / "01_unchanged" / "input.json")

    assert scenario_csv.row_count == 100
    assert scenario_csv.canonical_digest == baseline_csv.canonical_digest
    assert scenario_json.canonical_digest == baseline_csv.canonical_digest
