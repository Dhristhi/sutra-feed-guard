#!/usr/bin/env uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["sutra-feed-guard"]
# ///
"""Scenario 08: malformed partial delivery should exit 4."""

import sys
from pathlib import Path
from feedguard.classification import classify_change

FIXTURES = Path(__file__).parent.parent / "fixtures" / "sutra-feed-guard-fixtures-v1"

result = classify_change(
    baseline_path=FIXTURES / "historical" / "orders_2026-07-03.csv",
    observation_path=FIXTURES / "scenarios" / "08_malformed_partial_delivery" / "input.csv",
    policy_path=FIXTURES / "contracts" / "accepted_policy.yaml",
)

assert result.disposition == "invalid_observation", f"Expected invalid_observation, got {result.disposition}"
assert result.exit_code == 4, f"Expected exit 4, got {result.exit_code}"
assert result.affected_count is None
assert "partial_or_malformed_delivery" in result.reason_codes

print("SCENARIO 08 PASS: malformed partial delivery")
sys.exit(0)
