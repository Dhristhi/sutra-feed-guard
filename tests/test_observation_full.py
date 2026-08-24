"""Tests for observation loading edge cases."""

import json
from pathlib import Path

from feedguard.observation import load_observation


FIXTURES = Path(__file__).parents[1] / "fixtures" / "sutra-feed-guard-fixtures-v1"


def test_load_csv_baseline() -> None:
    obs = load_observation(FIXTURES / "historical" / "orders_2026-07-03.csv")
    assert obs.format == "csv"
    assert obs.row_count == 100
    assert "order_id" in obs.fields
    assert "amount" in obs.fields


def test_load_json_baseline() -> None:
    obs = load_observation(FIXTURES / "historical" / "orders_2026-07-03.json")
    assert obs.format == "json"
    assert obs.row_count == 100
    assert obs.canonical_digest != obs.source_digest


def test_csv_json_logical_equivalence() -> None:
    csv_obs = load_observation(FIXTURES / "historical" / "orders_2026-07-03.csv")
    json_obs = load_observation(FIXTURES / "historical" / "orders_2026-07-03.json")
    assert csv_obs.row_count == json_obs.row_count
    assert csv_obs.canonical_digest == json_obs.canonical_digest


def test_load_malformed_csv_raises() -> None:
    import pytest
    with pytest.raises(Exception):
        load_observation(FIXTURES / "scenarios" / "08_malformed_partial_delivery" / "input.csv")


def test_load_malformed_json_raises() -> None:
    import pytest
    with pytest.raises(Exception):
        load_observation(FIXTURES / "scenarios" / "08_malformed_partial_delivery" / "input.json")
