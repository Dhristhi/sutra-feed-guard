"""Tests for report rendering."""

import json
from pathlib import Path

from feedguard.classification import classify_change
from feedguard.report import render_html_report, render_json_envelope


FIXTURES = Path(__file__).parents[1] / "fixtures" / "sutra-feed-guard-fixtures-v1"
TMP = Path(__file__).parents[1] / "tmp"


def test_render_html_for_breaking_change() -> None:
    TMP.mkdir(exist_ok=True)
    result = classify_change(
        baseline_path=FIXTURES / "historical" / "orders_2026-07-03.csv",
        observation_path=FIXTURES / "scenarios" / "03_removed_required_column" / "input.csv",
        policy_path=FIXTURES / "contracts" / "accepted_policy.yaml",
    )
    html_path = TMP / "test_breaking.html"
    render_html_report("baseline.csv", "scenario_03.csv", result, html_path)
    assert html_path.exists()
    content = html_path.read_text()
    assert "breaking" in content.lower()
    assert "required_field_removed" in content


def test_render_json_envelope_structure() -> None:
    TMP.mkdir(exist_ok=True)
    result = classify_change(
        baseline_path=FIXTURES / "historical" / "orders_2026-07-03.csv",
        observation_path=FIXTURES / "scenarios" / "07_accepted_field_alias" / "input.csv",
        policy_path=FIXTURES / "contracts" / "accepted_policy.yaml",
    )
    json_path = TMP / "test_envelope.json"
    render_json_envelope("baseline.csv", "scenario_07.csv", result, json_path)
    assert json_path.exists()
    envelope = json.loads(json_path.read_text())
    assert envelope["version"] == 1
    assert envelope["disposition"] == "known_variant"
    assert envelope["exit_code"] == 0
    assert "baseline_name" in envelope
    assert "observation_name" in envelope
