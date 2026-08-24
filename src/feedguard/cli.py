"""Command-line interface for Feed Guard."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from feedguard.classification import classify_change
from feedguard.journal import accept_baseline, Journal
from feedguard.report import render_html_report, render_json_envelope


def cmd_accept(args: argparse.Namespace) -> int:
    journal = accept_baseline(
        baseline_path=args.baseline,
        policy_path=args.policy,
        journal_dir=args.output,
    )
    print(f"Accepted baseline with {journal.entries[0]['row_count']} rows")
    print(f"Journal: {journal.dir}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    result = classify_change(
        baseline_path=args.baseline,
        observation_path=args.observation,
        policy_path=args.policy,
    )

    output_dir = Path(args.output) if args.output else Path.cwd()
    output_dir.mkdir(parents=True, exist_ok=True)

    html_path = output_dir / "report.html"
    json_path = output_dir / "envelope.json"

    render_html_report(
        Path(args.baseline).name,
        Path(args.observation).name,
        result,
        html_path,
    )
    render_json_envelope(
        Path(args.baseline).name,
        Path(args.observation).name,
        result,
        json_path,
    )

    print(f"Disposition: {result.disposition}")
    print(f"Exit code: {result.exit_code}")
    print(f"Primary reason: {result.primary_reason}")
    if result.affected_count is not None:
        print(f"Affected records: {result.affected_count:,}")
    if result.nonempty_new_value_count is not None:
        print(f"Non-empty new values: {result.nonempty_new_value_count:,}")
    print(f"HTML report: {html_path}")
    print(f"JSON envelope: {json_path}")

    return result.exit_code


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="feedguard",
        description="Local-first change guard for external CSV and JSON feeds",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    accept_parser = subparsers.add_parser("accept", help="Accept a baseline feed")
    accept_parser.add_argument("baseline", type=Path, help="Path to baseline CSV or JSON")
    accept_parser.add_argument(
        "policy", type=Path, help="Path to accepted_policy.yaml"
    )
    accept_parser.add_argument(
        "-o", "--output", type=Path, required=True, help="Journal output directory"
    )
    accept_parser.set_defaults(func=cmd_accept)

    check_parser = subparsers.add_parser("check", help="Check an observation against baseline")
    check_parser.add_argument("baseline", type=Path, help="Path to accepted baseline CSV or JSON")
    check_parser.add_argument("observation", type=Path, help="Path to observation CSV or JSON")
    check_parser.add_argument(
        "policy", type=Path, help="Path to accepted_policy.yaml"
    )
    check_parser.add_argument(
        "-o", "--output", type=Path, help="Output directory for reports (default: cwd)"
    )
    check_parser.set_defaults(func=cmd_check)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
