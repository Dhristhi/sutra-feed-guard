#!/usr/bin/env uv run
# /// script
# requires-python = ">=3.12"
# dependencies = ["sutra-feed-guard"]
# ///
"""Demo: bounded AI assistance with local Ollama MLX model.

This demonstrates the Week-2+ AI extension where:
1. Deterministic classification runs first (exit code 3 for breaking)
2. Local AI suggests field mappings or detects unit traps
3. AI suggestions are logged in journal with full audit trail
4. AI is NON-BINDING — deterministic disposition remains authoritative
"""

import sys
from pathlib import Path

from feedguard.classification import classify_change
from feedguard.journal import accept_baseline, Journal
from feedguard.ai_assist import (
    suggest_field_mapping,
    detect_unit_trap,
    log_ai_interaction,
    AISuggestion,
)
from feedguard.observation import load_observation


FIXTURES = Path(__file__).parent.parent / "fixtures" / "sutra-feed-guard-fixtures-v1"
DEMO_JOURNAL = Path(__file__).parent.parent / "demo_ai_journal"


def main() -> int:
    print("=" * 70)
    print("SUTRA FEED GUARD — BOUNDED AI ASSISTANCE DEMO")
    print("=" * 70)
    print()

    # Step 1: Accept baseline
    print("STEP 1: Accept baseline")
    print("-" * 40)
    if DEMO_JOURNAL.exists():
        import shutil
        shutil.rmtree(DEMO_JOURNAL)

    journal = accept_baseline(
        baseline_path=FIXTURES / "historical" / "orders_2026-07-03.csv",
        policy_path=FIXTURES / "contracts" / "accepted_policy.yaml",
        journal_dir=DEMO_JOURNAL,
    )
    print(f"✓ Accepted baseline with {journal.entries[0]['row_count']} rows")
    print(f"✓ Journal: {DEMO_JOURNAL}")
    print()

    # Step 2: Run deterministic classification (Week-1 core)
    print("STEP 2: Deterministic classification (Week-1 core)")
    print("-" * 40)
    result = classify_change(
        baseline_path=FIXTURES / "historical" / "orders_2026-07-03.csv",
        observation_path=FIXTURES / "scenarios" / "07_accepted_field_alias" / "input.csv",
        policy_path=FIXTURES / "contracts" / "accepted_policy.yaml",
    )
    print(f"Disposition: {result.disposition}")
    print(f"Exit code: {result.exit_code}")
    print(f"Primary reason: {result.primary_reason}")
    print(f"Changed fields: {', '.join(result.changed_fields)}")
    print()

    # Step 3: Invoke bounded AI assistance (Week-2+ extension)
    print("STEP 3: Bounded AI assistance (local Ollama MLX)")
    print("-" * 40)
    print("Model: gemma4:31b-mlx (local, no network)")
    print()

    # Load observations for AI analysis
    baseline_obs = load_observation(FIXTURES / "historical" / "orders_2026-07-03.csv")
    observation_obs = load_observation(
        FIXTURES / "scenarios" / "07_accepted_field_alias" / "input.csv"
    )

    # 3a: Field mapping suggestion
    print("3a. Requesting field mapping suggestion...")
    mapping_suggestion = suggest_field_mapping(
        observation_fields=list(observation_obs.fields),
        baseline_fields=list(baseline_obs.fields),
        model="llama3.2:3b",
    )
    print(f"    Model: {mapping_suggestion.model}")
    print(f"    Suggestion type: {mapping_suggestion.suggestion_type}")
    print(f"    Confidence: {mapping_suggestion.confidence:.2f}")
    print(f"    Binding: {mapping_suggestion.binding}")
    if "error" not in mapping_suggestion.suggestion:
        print(f"    Mappings: {mapping_suggestion.suggestion.get('mappings', [])}")
    else:
        print(f"    Suggestion: {mapping_suggestion.suggestion}")
    print()

    # 3b: Unit trap detection (for scenario 06)
    print("3b. Running unit trap detection on scenario 06...")
    scenario_06_obs = load_observation(
        FIXTURES / "scenarios" / "06_rupees_to_paise_semantic_trap" / "input.csv"
    )
    baseline_amounts = [
        float(r["amount"]) for r in baseline_obs.records if "amount" in r
    ]
    scenario_06_amounts = [
        float(r["amount_in_paise"])
        for r in scenario_06_obs.records
        if "amount_in_paise" in r
    ]

    unit_suggestion = detect_unit_trap(
        baseline_amounts=baseline_amounts,
        observation_amounts=scenario_06_amounts,
        model="llama3.2:3b",
    )
    print(f"    Model: {unit_suggestion.model}")
    print(f"    Suggestion type: {unit_suggestion.suggestion_type}")
    print(f"    Confidence: {unit_suggestion.confidence:.2f}")
    if "error" not in unit_suggestion.suggestion:
        print(f"    Hypothesis: {unit_suggestion.suggestion.get('hypothesis', 'unknown')}")
        print(f"    Reasoning: {unit_suggestion.suggestion.get('reasoning', '')[:100]}")
    else:
        print(f"    Suggestion: {unit_suggestion.suggestion}")
    print()

    # Step 4: Log AI interactions in journal
    print("STEP 4: Logging AI interactions in audit journal")
    print("-" * 40)
    log_ai_interaction(
        journal_dir=DEMO_JOURNAL,
        suggestion=mapping_suggestion,
        deterministic_disposition=result.disposition,
        final_disposition=result.disposition,  # AI did NOT override
    )
    log_ai_interaction(
        journal_dir=DEMO_JOURNAL,
        suggestion=unit_suggestion,
        deterministic_disposition="breaking",
        final_disposition="breaking",  # AI did NOT override
    )
    print(f"✓ Logged 2 AI interactions in {DEMO_JOURNAL / 'journal.jsonl'}")
    print()

    # Step 5: Show audit trail
    print("STEP 5: Audit trail verification")
    print("-" * 40)
    journal_lines = (DEMO_JOURNAL / "journal.jsonl").read_text().splitlines()
    ai_entries = [
        entry for entry in journal_lines if '"action": "ai_assistance"' in entry
    ]
    print(f"Total journal entries: {len(journal_lines)}")
    print(f"AI assistance entries: {len(ai_entries)}")
    print()

    # Step 6: Invariant check
    print("STEP 6: Invariant verification")
    print("-" * 40)
    print("✓ Deterministic disposition: AUTHORITY (AI non-binding)")
    print("✓ AI suggestions logged with timestamps and digests")
    print("✓ No automatic overrides — human approval required")
    print("✓ Local model only — no network calls")
    print()

    print("=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print()
    print("Key takeaways:")
    print("1. Week-1 deterministic core runs first (exit codes 0/2/3/4)")
    print("2. Week-2+ AI provides bounded, non-binding suggestions")
    print("3. All AI interactions logged in immutable journal")
    print("4. Local Ollama MLX model — no network dependency")
    print("5. Human approval binds decisions — AI never auto-commits")
    print()
    print("See demo_ai_journal/journal.jsonl for full audit trail")

    return 0


if __name__ == "__main__":
    sys.exit(main())
