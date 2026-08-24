"""Tests for CLI commands."""

import json
import subprocess
from pathlib import Path

FIXTURES = Path(__file__).parents[1] / "fixtures" / "sutra-feed-guard-fixtures-v1"
TMP = Path(__file__).parents[1] / "tmp"


def run_feedguard(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", "feedguard"] + args,
        capture_output=True,
        text=True,
        cwd=TMP.parent,
    )


def test_cli_accept_creates_journal() -> None:
    TMP.mkdir(exist_ok=True)
    journal_dir = TMP / "cli_test_journal"
    if journal_dir.exists():
        import shutil
        shutil.rmtree(journal_dir)

    result = run_feedguard(
        [
            "accept",
            str(FIXTURES / "historical" / "orders_2026-07-03.csv"),
            str(FIXTURES / "contracts" / "accepted_policy.yaml"),
            "-o",
            str(journal_dir),
        ]
    )

    assert result.returncode == 0
    assert "Accepted baseline with 100 rows" in result.stdout
    assert (journal_dir / "journal.jsonl").exists()
    assert (journal_dir / "accepted" / "baseline.canonical.json").exists()


def test_cli_check_unchanged_exit_0() -> None:
    TMP.mkdir(exist_ok=True)
    output_dir = TMP / "cli_unchanged"

    result = run_feedguard(
        [
            "check",
            str(FIXTURES / "historical" / "orders_2026-07-03.csv"),
            str(FIXTURES / "scenarios" / "01_unchanged" / "input.csv"),
            str(FIXTURES / "contracts" / "accepted_policy.yaml"),
            "-o",
            str(output_dir),
        ]
    )

    assert result.returncode == 0
    assert "Disposition: unchanged" in result.stdout
    assert (output_dir / "report.html").exists()
    assert (output_dir / "envelope.json").exists()


def test_cli_check_breaking_exit_3() -> None:
    TMP.mkdir(exist_ok=True)
    output_dir = TMP / "cli_breaking"

    result = run_feedguard(
        [
            "check",
            str(FIXTURES / "historical" / "orders_2026-07-03.csv"),
            str(FIXTURES / "scenarios" / "03_removed_required_column" / "input.csv"),
            str(FIXTURES / "contracts" / "accepted_policy.yaml"),
            "-o",
            str(output_dir),
        ]
    )

    assert result.returncode == 3
    assert "Disposition: breaking" in result.stdout
    assert "required_field_removed" in result.stdout


def test_cli_check_malformed_exit_4() -> None:
    TMP.mkdir(exist_ok=True)
    output_dir = TMP / "cli_malformed"

    result = run_feedguard(
        [
            "check",
            str(FIXTURES / "historical" / "orders_2026-07-03.csv"),
            str(FIXTURES / "scenarios" / "08_malformed_partial_delivery" / "input.csv"),
            str(FIXTURES / "contracts" / "accepted_policy.yaml"),
            "-o",
            str(output_dir),
        ]
    )

    assert result.returncode == 4
    assert "Disposition: invalid_observation" in result.stdout


def test_cli_help() -> None:
    result = run_feedguard(["--help"])
    assert result.returncode == 0
    assert "accept" in result.stdout
    assert "check" in result.stdout
