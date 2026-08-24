# DEMO — Sutra External Feed Change Guard

A self-guided walkthrough. All commands run locally with no network calls.

## Prerequisites

```bash
cd /Users/madhavraop/Code/sutra-feed-guard
uv sync --extra dev
```

## 1. Accept a baseline

```bash
uv run feedguard accept \
  fixtures/sutra-feed-guard-fixtures-v1/historical/orders_2026-07-03.csv \
  fixtures/sutra-feed-guard-fixtures-v1/contracts/accepted_policy.yaml \
  -o .feedguard
```

Expected output:

```text
Accepted baseline with 100 rows
Journal: .feedguard
```

Verify the journal was created:

```bash
ls -la .feedguard/accepted/
cat .feedguard/journal.jsonl
```

You should see:
- `baseline.canonical.json` (100 normalized records)
- `envelope.json` (digests, row count, timestamp)
- `policy.yaml` (copy of the accepted policy)
- `journal.jsonl` (append-only audit log)

## 2. Check an unchanged feed

```bash
uv run feedguard check \
  .feedguard/accepted/baseline.canonical.json \
  fixtures/sutra-feed-guard-fixtures-v1/scenarios/01_unchanged/input.csv \
  fixtures/sutra-feed-guard-fixtures-v1/contracts/accepted_policy.yaml \
  -o demo/01_unchanged
```

Expected:

```text
Disposition: unchanged
Exit code: 0
Affected records: 0
```

Open `demo/01_unchanged/report.html` in your browser to see the visual report.

## 3. Check a breaking change (removed column)

```bash
uv run feedguard check \
  fixtures/sutra-feed-guard-fixtures-v1/historical/orders_2026-07-03.csv \
  fixtures/sutra-feed-guard-fixtures-v1/scenarios/03_removed_required_column/input.csv \
  fixtures/sutra-feed-guard-fixtures-v1/contracts/accepted_policy.yaml \
  -o demo/03_breaking
```

Expected:

```text
Disposition: breaking
Exit code: 3
Primary reason: required_field_removed
Affected records: 100
```

The HTML report shows which field was removed and the severity.

## 4. Check a known variant (accepted alias)

```bash
uv run feedguard check \
  fixtures/sutra-feed-guard-fixtures-v1/historical/orders_2026-07-03.csv \
  fixtures/sutra-feed-guard-fixtures-v1/scenarios/07_accepted_field_alias/input.csv \
  fixtures/sutra-feed-guard-fixtures-v1/contracts/accepted_policy.yaml \
  -o demo/07_alias
```

Expected:

```text
Disposition: known_variant
Exit code: 0
Primary reason: accepted_field_alias
```

This demonstrates the policy-driven alias `total_amount → amount`.

## 5. Check a malformed delivery

```bash
uv run feedguard check \
  fixtures/sutra-feed-guard-fixtures-v1/historical/orders_2026-07-03.csv \
  fixtures/sutra-feed-guard-fixtures-v1/scenarios/08_malformed_partial_delivery/input.csv \
  fixtures/sutra-feed-guard-fixtures-v1/contracts/accepted_policy.yaml \
  -o demo/08_malformed
```

Expected:

```text
Disposition: invalid_observation
Exit code: 4
Affected records: unknown (parsing failed)
```

The tool refuses to classify when parsing fails.

## 6. Run all self-checking scenarios

```bash
for s in scripts/scenario_*.py; do
  echo "Running $s"
  uv run python "$s"
done
```

Expected:

```text
SCENARIO 01 PASS: unchanged
SCENARIO 03 PASS: removed required column (breaking)
SCENARIO 08 PASS: malformed partial delivery
```

## 7. Run the full test suite

```bash
uv run pytest tests/ -q
uv run pytest tests/ --cov=feedguard --cov-report=term-missing
```

Expected: all tests pass with >90% coverage.

## 8. Demo: bounded AI assistance (Week-2+)

```bash
uv run python scripts/demo_ai_assistance.py
```

This demonstrates:
- Deterministic classification runs first (exit code 0/2/3/4)
- Local Ollama MLX model (`llama3.2:3b`) suggests field mappings
- AI detects unit traps (rupees→paise)
- All AI interactions logged in immutable journal
- AI is **non-binding**—deterministic disposition remains authoritative

See `demo_ai_journal/journal.jsonl` for the full audit trail.

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | unchanged, safe_additive, or known_variant |
| 2 | review_required (unrecognized change) |
| 3 | breaking (critical schema or data violation) |
| 4 | invalid_observation (parsing failure) |

## What's next

This is the Week-1 tracer bullet. The four-week validation boundary adds:
- Scheduled GitHub Action execution
- Redacted incident packets
- Five real customer artifact bundles
- Paid shadow pilots with three teams

See `src/feedguard/specification.md` for the full specification.
