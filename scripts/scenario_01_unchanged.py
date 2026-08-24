#!/usr/bin/env uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["sutra-feed-guard"]
# ///
"""Scenario 01: unchanged feed should exit 0."""

import sys
from pathlib import Path
from feedguard.classification import classify_change

FIXTURES = Path(__file__).parent.parent / "fixtures" / "sutra-feed-guard-fixtures-v1"

result = classify_change(
    baseline_path=FIXTURES / "historical" / "orders_2026-07-03.csv",
    observation_path=FIXTURES / "scenarios" / "01_unchanged" / "input.csv",
    policy_path=FIXTURES / "contracts" / "accepted_policy.yaml",
)

assert result.disposition == "unchanged", f"Expected unchanged, got {result.disposition}"
assert result.exit_code == 0, f"Expected exit 0, got {result.exit_code}"
assert result.affected_count == 0

print("SCENARIO 01 PASS: unchanged")
sys.exit(0)
