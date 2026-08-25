# Architecture — Sutra Feed Guard

## Thesis

External feed changes are a **change-control and evidence problem**, not merely a data-integration problem. The guard:

1. Loads an observation (CSV or JSON) into a **canonical local form**
2. Computes a **content-addressed digest** independent of row order, quoting, or JSON whitespace
3. Compares against an **explicitly accepted baseline**
4. Classifies the change using a **policy-driven ruleset**
5. Emits a **deterministic decision envelope** with HTML and JSON evidence
6. Records acceptance and changes in an **append-only journal**

The product does **not** write to customer production destinations. It produces evidence packets for human review and approval.

## Data model

### Observation

```python
@dataclass(frozen=True)
class Observation:
    format: str                    # "csv" or "json"
    row_count: int                 # number of records
    fields: tuple[str, ...]        # field names in file order
    records: tuple[dict, ...]      # normalized records
    source_digest: str             # SHA-256 of raw bytes
    canonical_digest: str          # SHA-256 of normalized JSON
```

**Canonicalization rules:**
- `amount`-like fields normalized via `Decimal` to preserve precision
- Records sorted by JSON serialization (deterministic order)
- Nulls preserved but not specially treated
- Field order from file preserved in metadata, not in digest

### Classification result

```python
@dataclass(frozen=True)
class ClassificationResult:
    disposition: str               # unchanged, safe_additive, known_variant, review_required, breaking, invalid_observation
    exit_code: int                 # 0, 2, 3, or 4
    primary_reason: str            # machine-readable code
    reason_codes: tuple[str, ...]  # all applicable codes
    affected_count: int | None     # number of affected records (None if unknown)
    nonempty_new_value_count: int | None
    changed_fields: tuple[str, ...]
    affected_order_ids: tuple[str, ...]
```

### Journal entry

```python
{
  "version": 1,
  "action": "accept_baseline" | "check_observation",
  "source_digest": str,
  "canonical_digest": str,
  "policy_digest": str,
  "format": str,
  "row_count": int,
  "fields": [...],
  "timestamp": ISO-8601 UTC
}
```

## Module responsibilities

| Module | Responsibility |
|--------|----------------|
| `observation.py` | Parse CSV/JSON, normalize amounts, compute digests |
| `classification.py` | Policy loading, change detection, disposition logic |
| `journal.py` | Append-only audit log, baseline acceptance, envelope persistence |
| `report.py` | HTML and JSON evidence rendering |
| `cli.py` | `accept` and `check` subcommands, exit codes |
| `ai_assist.py` | Bounded AI assistance (local Ollama), field mapping suggestions, unit trap detection, AI interaction logging |

## Classification decision tree

```
malformed CSV/JSON?
  └─ yes → invalid_observation (exit 4)

amount removed AND amount_in_paise added?
  └─ yes → breaking: unit_semantics_changed (exit 3)

new field is accepted alias?
  └─ yes → known_variant (exit 0)

required field removed?
  └─ yes → breaking: required_field_removed (exit 3)

duplicate primary key?
  └─ yes → breaking: duplicate_primary_key (exit 3)

new fields present?
  └─ yes → safe_additive (exit 0)

customer_id format violation?
  └─ yes → breaking: identifier_format_violation (exit 3)

canonical digest unchanged?
  └─ yes → unchanged (exit 0)

otherwise → review_required (exit 2)
```

## Exit codes

| Code | Dispositions | Meaning |
|------|--------------|---------|
| 0 | unchanged, safe_additive, known_variant | No action required |
| 2 | review_required | Human review needed |
| 3 | breaking (all variants) | Critical violation; block processing |
| 4 | invalid_observation | Parsing failed; cannot classify |

## Policy structure

```yaml
policy_name: sutra_feed_guard_accepted_policy
version: "1.0.0"
rules:
  primary_key: order_id
  required_fields: [order_id, customer_id, ...]
  field_constraints:
    order_id:
      type: string
      pattern: "^ORD-[0-9]{6}$"
    customer_id:
      type: string
      pattern: "^CUS-[0-9]{4}$"
  classifications:
    duplicate_primary_key: critical
    missing_required_field: critical
  additive_fields:
    allow_additive: true
    restrictions: "Must not alter existing fields..."
  ordering:
    field_order_significant: false
    row_order_significant: false
  aliases:
    allowed:
      - alias: total_amount
        target: amount
        scope: scenario_07
    disallowed: [customer_id, amount_in_paise, currency]
  baseline_widening:
    automatic: false
  override_authority:
    model_generated_suggestions: not_authorized
```

## Evidence envelope

The JSON envelope (`envelope.json`) contains:

```json
{
  "version": 1,
  "baseline_name": "...",
  "observation_name": "...",
  "disposition": "breaking",
  "exit_code": 3,
  "primary_reason": "required_field_removed",
  "reason_codes": ["required_field_removed"],
  "affected_count": 100,
  "changed_fields": ["currency"],
  "affected_order_ids": []
}
```

The HTML report (`report.html`) renders this in a human-readable format with color-coded disposition badges.

## Determinism guarantees

- Same input files → same canonical digest
- Same classification inputs → same disposition and exit code
- Journal entries are append-only with UTC timestamps
- ZIP fixtures use fixed timestamps for reproducibility

## Limitations (current release)

The current release is **local-first and observational**:

- No scheduled execution (manual CLI invocation)
- No SFTP/S3 acquisition (local files only)
- No production writes (read-only analysis)
- No remote AI integration (local Ollama only)
- No multi-user approval workflows
- No cryptographic tamper resistance (digests are not signatures)

## Extension points

To extend this release:

1. Add `feedguard/schedule.py` for GitHub Action entry point
2. Add `feedguard/acquisition.py` for SFTP/S3 connectors
3. Add `feedguard/approvals.py` for multi-signature envelopes
4. Add `feedguard/remote_ai.py` for bounded model assistance (requires egress authorization record)
5. Add statistical drift framework for historical baseline comparison

## Current capabilities

| Feature | Status |
|---------|--------|
| CSV/JSON parsing | ✅ Deterministic, format-invariant |
| Canonical digests | ✅ SHA-256 |
| Classification rules | ✅ Policy-driven (8 scenarios) |
| Journal + envelope | ✅ Append-only audit trail |
| HTML/JSON reports | ✅ Local rendering |
| CLI commands | ✅ `accept` / `check` |
| AI field mapping | ✅ Local Ollama (`llama3.2:3b`), non-binding |
| AI unit trap detection | ✅ Rupees→paise, dollars→cents |
| AI audit logging | ✅ Full interaction trail |

## Roadmap (future)

| Feature | Status |
|---------|--------|
| SFTP/S3 acquisition | 🔜 Production connectors |

## Future features (exploratory)

These are design concepts, not committed deliverables. Implementation depends on customer workflow requirements.

### Multi-user approval workflows

The current release is single-user CLI. For regulated environments requiring multiple sign-offs, we are evaluating:

| Approach | How it works | Trade-offs |
|----------|--------------|------------|
| **Shared journal directory** | Network mount (S3, NFS) where multiple users run `feedguard approve --sign` | Requires infra setup; file locking complexity |
| **Signature chain** | Each approver adds cryptographic signature to `envelope.json` | Complex key management; verifiable audit trail |
| **Email/Slack workflow** | CLI outputs evidence packet → humans approve via existing tools → log decision | Manual, but matches real workflows; no new infrastructure |
| **Hosted control plane** | Sutra Control Plane tracks approvals; CLI checks in before accepting | Requires building the hosted product; cleanest UX |

**Design principle:** Multi-user approval must not compromise the local-first, auditable core. We will implement based on actual customer sign-off processes, not hypothetical requirements.

## When AI is invoked

The AI assistance layer is **optional** and **non-binding**:

1. **Deterministic core runs first** — Classification completes with exit code 0/2/3/4
2. **AI invoked for suggestions only** — Field mapping, unit trap detection
3. **AI cannot override disposition** — Deterministic result remains authoritative
4. **All AI interactions logged** — Full audit trail in `journal.jsonl`
5. **Local model only** — Ollama (`llama3.2:3b`), no network calls

```
┌─────────────────────────────────────────┐
│  Week-1: Deterministic Core (always)    │
│  - Parse → Digest → Classify → Report   │
│  - Exit code: 0/2/3/4                   │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Week-2: AI Assistance (optional)       │
│  - Field mapping suggestions            │
│  - Unit trap detection                  │
│  - Logged in journal (non-binding)      │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Human Review / Approval                │
│  - Binds the final decision             │
│  - AI never auto-commits                │
└─────────────────────────────────────────┘
```

See `scripts/demo_ai_assistance.py` for a complete end-to-end demonstration.

See `specification.md` for the full four-week scope.
