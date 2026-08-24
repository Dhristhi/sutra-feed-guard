from pathlib import Path

from feedguard.journal import accept_baseline, Journal


FIXTURES = Path(__file__).parents[1] / "fixtures" / "sutra-feed-guard-fixtures-v1"
TMP = Path(__file__).parents[1] / "tmp"


def test_accept_baseline_creates_journal_and_envelope() -> None:
    TMP.mkdir(exist_ok=True)
    journal_dir = TMP / "test_journal"
    if journal_dir.exists():
        import shutil
        shutil.rmtree(journal_dir)

    journal = accept_baseline(
        baseline_path=FIXTURES / "historical" / "orders_2026-07-03.csv",
        policy_path=FIXTURES / "contracts" / "accepted_policy.yaml",
        journal_dir=journal_dir,
    )

    assert journal_dir.exists()
    assert (journal_dir / "journal.jsonl").exists()
    assert (journal_dir / "accepted" / "baseline.canonical.json").exists()

    entry = journal.entries[0]
    assert entry["action"] == "accept_baseline"
    assert entry["source_digest"] is not None
    assert entry["canonical_digest"] is not None
    assert entry["row_count"] == 100
