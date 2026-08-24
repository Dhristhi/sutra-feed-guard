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

Week-1 tracer bullet complete:

- ✅ CSV/JSON loading with canonical digests
- ✅ Classification for 8 scenarios (unchanged, additive, breaking, alias, malformed, etc.)
- ✅ Accepted-state journal with immutable envelope
- ✅ HTML and JSON evidence reports
- ✅ CLI with documented exit codes
- ✅ Self-checking scenario scripts
- ✅ 11 passing tests

Week-2+ AI extension (demo):

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

## Specification

This is a four-week paid validation experiment. See the full specification at `specification.md`.

## License

Proprietary — for validation use only.
