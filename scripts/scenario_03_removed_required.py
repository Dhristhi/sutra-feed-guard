#!/usr/bin/env uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["sutra-feed-guard"]
# ///
"""Scenario 03: removed required column should exit 3 (breaking)."""

import sys
from pathlib import Path
from feedguard.classification import classify_change

FIXTURES = Path(__file__).parent.parent / "fixtures" / "sutra-feed-guard-fixtures-v1"

result = classify_change(
    baseline_path=FIXTURES / "historical" / "orders_2026-07-03.csv",
    observation_path=FIXTURES / "scenarios" / "03_removed_required_column" / "input.csv",
    policy_path=FIXTURES / "contracts" / "accepted_policy.yaml",
)

assert result.disposition == "breaking", f"Expected breaking, got {result.disposition}"
assert result.exit_code == 3, f"Expected exit 3, got {result.exit_code}"
assert result.affected_count == 100
assert "required_field_removed" in result.reason_codes

print("SCENARIO 03 PASS: removed required column (breaking)")
sys.exit(0)
