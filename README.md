# Sutra External Feed Guard

**Dependabot for external data feeds, with a reproducible incident packet.**

Local-first CLI that compares an external CSV or JSON observation against an explicitly accepted baseline and emits a deterministic decision envelope. It does not write to customer production data destinations.

## Quick start

```bash
uv sync --extra dev
uv run feedguard --help
```

See [`DEMO.md`](DEMO.md) for a self-guided walkthrough.

## Validation status

**Complete and ready for use:**

- ✅ CSV/JSON loading with canonical digests
- ✅ Classification for 8 scenarios (unchanged, additive, breaking, alias, malformed, etc.)
- ✅ Accepted-state journal with immutable envelope
- ✅ HTML and JSON evidence reports
- ✅ CLI with documented exit codes
- ✅ Self-checking scenario scripts
- ✅ 38 passing tests (74% coverage)
- ✅ Bounded AI assistance with local Ollama (`llama3.2:3b`)
- ✅ Field mapping suggestions (non-binding)
- ✅ Unit trap detection (rupees→paise)
- ✅ AI interactions logged in immutable journal
- ✅ Deterministic core remains authoritative

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | unchanged / safe_additive / known_variant |
| 2 | review_required |
| 3 | breaking |
| 4 | invalid_observation |

## How Feed Guard differs from other integration solutions

| Category | Typical approach | Feed Guard approach |
|----------|-----------------|---------------------|
| **Schema validation** | Static JSON Schema, Pandera, Frictionless — rigid, brittle | Canonical digests + policy-driven rules — detects structural AND semantic drift |
| **Field mapping** | Manual configuration or one-time AI inference | Deterministic alias table (auditable) + optional AI suggestions (logged, non-binding) |
| **Unit changes** | Silent corruption (rupees→paise) | Explicit detection via magnitude analysis + AI hypothesis generation |
| **Incident response** | Logs, alerts, manual investigation | Reproducible incident packet with exact affected records and contract impact |
| **Audit trail** | Ephemeral or separate system | Immutable journal with every decision, AI interaction, and human approval |
| **Integration posture** | Transform and publish (risky) | Observe and classify (fail-safe) — never writes to production destinations |
| **AI integration** | Black-box autonomous decisions | Bounded assistance: deterministic core first, AI suggestions second, human binds |

### The intelligence stack

```
┌─────────────────────────────────────────────────────────┐
│  Layer 3: AI Assistance (optional, non-binding)         │
│  - Suggests field mappings with confidence scores       │
│  - Detects unit traps (rupees→paise, dollars→cents)    │
│  - All suggestions logged with prompt hashes            │
│  - NEVER overrides deterministic disposition            │
└─────────────────────────────────────────────────────────┘
                        ↑
┌─────────────────────────────────────────────────────────┐
│  Layer 2: Deterministic Core (always authoritative)     │
│  - SHA-256 canonical digests (format-invariant)         │
│  - Policy-driven classification (explicit rules)        │
│  - Affected-record enumeration (exact blast radius)     │
│  - Exit codes: 0 (pass), 2 (review), 3 (breaking), 4    │
└─────────────────────────────────────────────────────────┘
                        ↑
┌─────────────────────────────────────────────────────────┐
│  Layer 1: Parsers (robust, local)                       │
│  - CSV: strict mode, no implicit coercion               │
│  - JSON: array-of-objects validation                    │
│  - Decimal normalization (currency-safe)                │
│  - Identifier format validation (leading zeros, etc.)   │
└─────────────────────────────────────────────────────────┘
```

**Why this matters:** Other tools are either purely static (rigid schemas) or AI-dependent (unpredictable). Feed Guard is **deterministic-first with bounded AI assistance** — you get the reliability of explicit rules with the adaptability of model suggestions, while maintaining a complete audit trail for regulated environments.

See `ARCHITECTURE.md` for the complete feature list and roadmap.

## License

Proprietary — for validation use only.
