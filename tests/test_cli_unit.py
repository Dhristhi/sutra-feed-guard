"""Unit tests for CLI internals (no subprocess)."""

import argparse
from pathlib import Path
from unittest.mock import patch

from feedguard.cli import cmd_accept, cmd_check


FIXTURES = Path(__file__).parents[1] / "fixtures" / "sutra-feed-guard-fixtures-v1"
TMP = Path(__file__).parents[1] / "tmp"


def test_cmd_accept_returns_zero() -> None:
    TMP.mkdir(exist_ok=True)
    journal_dir = TMP / "cli_unit_journal"
    if journal_dir.exists():
        import shutil
        shutil.rmtree(journal_dir)

    args = argparse.Namespace(
        baseline=FIXTURES / "historical" / "orders_2026-07-03.csv",
        policy=FIXTURES / "contracts" / "accepted_policy.yaml",
        output=journal_dir,
    )

    with patch("sys.stdout"):
        result = cmd_accept(args)

    assert result == 0
    assert (journal_dir / "journal.jsonl").exists()


def test_cmd_check_known_variant_returns_zero() -> None:
    TMP.mkdir(exist_ok=True)
    output_dir = TMP / "cli_unit_check"

    args = argparse.Namespace(
        baseline=FIXTURES / "historical" / "orders_2026-07-03.csv",
        observation=FIXTURES / "scenarios" / "07_accepted_field_alias" / "input.csv",
        policy=FIXTURES / "contracts" / "accepted_policy.yaml",
        output=output_dir,
    )

    with patch("sys.stdout"):
        result = cmd_check(args)

    assert result == 0
    assert (output_dir / "report.html").exists()
    assert (output_dir / "envelope.json").exists()


def test_cmd_check_breaking_returns_three() -> None:
    TMP.mkdir(exist_ok=True)
    output_dir = TMP / "cli_unit_breaking"

    args = argparse.Namespace(
        baseline=FIXTURES / "historical" / "orders_2026-07-03.csv",
        observation=FIXTURES / "scenarios" / "03_removed_required_column" / "input.csv",
        policy=FIXTURES / "contracts" / "accepted_policy.yaml",
        output=output_dir,
    )

    with patch("sys.stdout"):
        result = cmd_check(args)

    assert result == 3
    assert (output_dir / "report.html").exists()
