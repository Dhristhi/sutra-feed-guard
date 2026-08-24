from pathlib import Path

from feedguard.report import render_html_report, render_json_envelope
from feedguard.classification import classify_change


FIXTURES = Path(__file__).parents[1] / "fixtures" / "sutra-feed-guard-fixtures-v1"
TMP = Path(__file__).parents[1] / "tmp"


def test_render_html_and_json_for_scenario_03() -> None:
    TMP.mkdir(exist_ok=True)

    result = classify_change(
        baseline_path=FIXTURES / "historical" / "orders_2026-07-03.csv",
        observation_path=FIXTURES / "scenarios" / "03_removed_required_column" / "input.csv",
        policy_path=FIXTURES / "contracts" / "accepted_policy.yaml",
    )

    html_path = TMP / "report_03.html"
    json_path = TMP / "envelope_03.json"

    render_html_report("orders_2026-07-03.csv", "scenario_03.csv", result, html_path)
    render_json_envelope("orders_2026-07-03.csv", "scenario_03.csv", result, json_path)

    assert html_path.exists()
    assert json_path.exists()

    html_content = html_path.read_text()
    assert "breaking" in html_content.lower()
    assert "required_field_removed" in html_content
    assert "currency" in html_content

    import json
    envelope = json.loads(json_path.read_text())
    assert envelope["disposition"] == "breaking"
    assert envelope["exit_code"] == 3
    assert "required_field_removed" in envelope["reason_codes"]
