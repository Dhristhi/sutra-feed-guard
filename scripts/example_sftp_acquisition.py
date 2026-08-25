#!/usr/bin/env uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["sutra-feed-guard", "paramiko", "boto3"]
# ///
"""Example: Download from SFTP and run Feed Guard classification.

Usage:
    uv run scripts/example_sftp_acquisition.py \
        sftp://partner.example.com/data/daily.csv \
        fixtures/contracts/accepted_policy.yaml

Environment:
    FEEDGUARD_SFTP_USER: SFTP username
    FEEDGUARD_SFTP_KEY: Path to private key file
"""

import sys
from pathlib import Path

from feedguard.acquisition import download_from_uri
from feedguard.classification import classify_change


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python example_sftp_acquisition.py <sftp_uri> <policy.yaml>")
        print("Example: python example_sftp_acquisition.py sftp://partner.com/data.csv policy.yaml")
        return 1

    sftp_uri = sys.argv[1]
    policy_path = Path(sys.argv[2])

    print(f"Downloading from {sftp_uri}...")
    result = download_from_uri(sftp_uri)

    try:
        print(f"Downloaded {result.bytes_downloaded:,} bytes to {result.local_path}")
        print()

        # Run Feed Guard classification on downloaded file
        print("Running Feed Guard classification...")
        classification = classify_change(
            baseline_path=Path("fixtures/historical/orders_2026-07-03.csv"),
            observation_path=result.local_path,
            policy_path=policy_path,
        )

        print(f"Disposition: {classification.disposition}")
        print(f"Exit code: {classification.exit_code}")
        print(f"Primary reason: {classification.primary_reason}")

        if classification.affected_count:
            print(f"Affected records: {classification.affected_count:,}")

        return classification.exit_code

    finally:
        # Clean up temp files
        result.cleanup()
        print("\nTemporary files cleaned up.")


if __name__ == "__main__":
    sys.exit(main())
