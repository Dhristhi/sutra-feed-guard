"""Accepted-state journal and baseline lifecycle."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from feedguard.observation import Observation, load_observation


@dataclass
class Journal:
    dir: Path
    entries: list[dict[str, Any]] = field(default_factory=list)

    def append(self, entry: dict[str, Any]) -> None:
        entry["timestamp"] = datetime.now(timezone.utc).isoformat()
        self.entries.append(entry)
        with open(self.dir / "journal.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")


def accept_baseline(
    baseline_path: Path | str,
    policy_path: Path | str,
    journal_dir: Path | str,
) -> Journal:
    source = Path(baseline_path)
    policy = Path(policy_path)
    journal_dir = Path(journal_dir)
    journal_dir.mkdir(parents=True, exist_ok=True)

    observation = load_observation(source)
    policy_bytes = policy.read_bytes()
    policy_digest = __import__("hashlib").sha256(policy_bytes).hexdigest()

    accepted_dir = journal_dir / "accepted"
    accepted_dir.mkdir(exist_ok=True)

    baseline_canonical_path = accepted_dir / "baseline.canonical.json"
    baseline_canonical_path.write_text(
        json.dumps(observation.records, indent=2, sort_keys=True)
    )

    baseline_policy_path = accepted_dir / "policy.yaml"
    shutil.copy2(policy, baseline_policy_path)

    envelope = {
        "version": 1,
        "action": "accept_baseline",
        "source_path": str(source),
        "source_digest": observation.source_digest,
        "canonical_digest": observation.canonical_digest,
        "policy_digest": policy_digest,
        "format": observation.format,
        "row_count": observation.row_count,
        "fields": observation.fields,
        "accepted_at": datetime.now(timezone.utc).isoformat(),
    }

    envelope_path = accepted_dir / "envelope.json"
    envelope_path.write_text(json.dumps(envelope, indent=2, sort_keys=True))

    journal = Journal(dir=journal_dir)
    journal.append(envelope)

    return journal
