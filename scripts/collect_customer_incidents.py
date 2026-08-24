#!/usr/bin/env python3
"""Customer discovery script — collect 5 real incident bundles.

Usage:
    python scripts/collect_customer_incidents.py <customer_name> <output_dir>

Each incident bundle should contain:
1. baseline.csv or baseline.json (last accepted delivery)
2. changed.csv or changed.json (new delivery with issues)
3. known_issues.txt (what went wrong, impact, investigation time)
4. policy.yaml (optional — field constraints, aliases)

Gate: 5 bundles collected → proceed to paid pilot outreach
"""

import sys
from pathlib import Path
from datetime import datetime, timezone


def create_incident_template(output_dir: Path, customer_name: str) -> None:
    """Create a template folder for one customer incident."""
    incident_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    bundle_dir = output_dir / f"{customer_name}_{incident_id}"
    bundle_dir.mkdir(parents=True, exist_ok=True)

    (bundle_dir / "baseline.csv").write_text("# Replace with actual baseline CSV\norder_id,customer_id,amount\n")
    (bundle_dir / "changed.csv").write_text("# Replace with actual changed CSV\norder_id,customer_id,amount\n")
    (bundle_dir / "known_issues.txt").write_text("""# Known Issues Template

## What changed?
Describe the schema/data change that caused problems.

## Impact
- Engineering hours spent: ?
- Business impact (delayed reports, incorrect payouts, etc.): ?
- Root cause discovered: ?

## Expected behavior
What should Feed Guard have detected?

## Actual behavior
What actually happened?
""")
    (bundle_dir / "policy.yaml").write_text("""# Optional: Field constraints and aliases
policy_name: customer_policy
version: "1.0.0"
rules:
  primary_key: order_id
  required_fields: [order_id, customer_id, amount]
  aliases:
    allowed: []
""")
    (bundle_dir / "README.md").write_text(f"""# Incident Bundle: {customer_name}

**Collected:** {datetime.now(timezone.utc).isoformat()}

## Files
- `baseline.csv` — Last accepted delivery
- `changed.csv` — New delivery with issues
- `known_issues.txt` — What went wrong
- `policy.yaml` — Field constraints (optional)

## Next steps
1. Replace placeholder files with real data
2. Redact sensitive fields (customer PII, amounts if confidential)
3. Run Feed Guard: `feedguard check baseline.csv changed.csv policy.yaml`
4. Verify detection matches known issues
""")

    print(f"✓ Created incident bundle template: {bundle_dir}")


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python collect_customer_incidents.py <customer_name> <output_dir>")
        print("Example: python collect_customer_incidents.py acme_corp ./customer_incidents")
        return 1

    customer_name = sys.argv[1]
    output_dir = Path(sys.argv[2])
    output_dir.mkdir(parents=True, exist_ok=True)

    create_incident_template(output_dir, customer_name)

    print()
    print("Next steps:")
    print("1. Ask customer for real baseline/changed files")
    print("2. Redact sensitive data (PII, confidential amounts)")
    print("3. Fill in known_issues.txt with actual impact")
    print("4. Run Feed Guard and verify detection")
    print()
    print("Gate: 5 bundles → proceed to paid pilot outreach ($99 shadow pilot)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
