# AntiGravity Prompt — Sutra Feed Guard Demo Generation

Copy this entire prompt into Google AntiGravity. Use **Local Mode** with the project folder `/Users/madhavraop/Code/sutra-feed-guard`.

---

You are a senior Python engineer building a **bounded AI assistance demo** for the Sutra Feed Guard project. This is a **reference-build demo** that must be fully self-guided and verifiable via CLI commands.

## Context

Sutra Feed Guard is a local-first change guard for external CSV/JSON feeds. The Week-1 deterministic core is complete. You are adding a **Week-2+ AI extension** that:

1. Uses **local Ollama MLX models only** (no network calls)
2. Provides **non-binding suggestions** (deterministic core remains authoritative)
3. Logs **all AI interactions in an immutable journal** with timestamps and digests
4. Demonstrates the thesis: *"Deterministic outside, probabilistic inside"*

## Your Task

Generate the following files in the existing project structure. Do **not** modify existing core modules (`observation.py`, `classification.py`, `journal.py`, `report.py`, `cli.py`). Create **new files only**.

## Files to Generate

### 1. `src/feedguard/ai_assist.py`

Bounded AI assistance module with these functions:

- `_ollama_chat(model: str, prompt: str) -> str`
  - Call local Ollama CLI (`ollama run <model> <prompt>`)
  - Strip ANSI escape codes from output
  - Timeout: 120 seconds
  - Raise `RuntimeError` on failure

- `_hash_prompt(prompt: str) -> str`
  - SHA-256 hash of prompt (first 16 chars)

- `suggest_field_mapping(observation_fields, baseline_fields, model="llama3.2:3b") -> AISuggestion`
  - Prompt: "You are a data integration assistant. Suggest field mappings..."
  - Force JSON-only output (no CoT, no markdown)
  - Return mappings with confidence scores
  - Handle parse failures gracefully

- `detect_unit_trap(baseline_amounts, observation_amounts, model="llama3.2:3b") -> AISuggestion`
  - Prompt: "You are a data quality assistant. Detect if amounts changed units..."
  - Detect rupees→paise, dollars→cents traps
  - Return hypothesis, confidence, reasoning

- `log_ai_interaction(journal_dir, suggestion, deterministic_disposition, final_disposition)`
  - Append to `journal.jsonl` with full audit trail
  - Include: timestamp, model, prompt_hash, suggestion, confidence, binding=False, audit_digest

Dataclass:
```python
@dataclass
class AISuggestion:
    model: str
    prompt_hash: str
    suggestion_type: str
    suggestion: dict[str, Any]
    confidence: float
    binding: bool = False
```

**Key invariants:**
- AI is **non-binding** (`binding=False` always)
- All prompts force **JSON-only output**
- All interactions **logged with digests**
- **Local model only** — no HTTP calls

### 2. `scripts/demo_ai_assistance.py`

End-to-end demo script (executable via `uv run python scripts/demo_ai_assistance.py`).

**Narrative flow (6 steps):**

1. **Accept baseline** — create fresh journal directory
2. **Run deterministic classification** — show Week-1 core output (disposition, exit code)
3. **Invoke bounded AI** — call both `suggest_field_mapping` and `detect_unit_trap`
4. **Log AI interactions** — write to journal with audit trail
5. **Verify audit trail** — count AI entries in journal
6. **Invariant check** — confirm AI did NOT override deterministic disposition

**Output requirements:**
- Print each step with clear headers
- Show model name, confidence, binding status
- Display AI suggestions (or parse errors)
- Show journal entry counts
- End with "DEMO COMPLETE" and key takeaways

**Exit code:** 0 on success

### 3. Update `README.md`

Add a new section after "Validation status":

```markdown
Week-2+ AI extension (demo):

- ✅ Bounded AI assistance with local Ollama (`llama3.2:3b`)
- ✅ Field mapping suggestions (non-binding)
- ✅ Unit trap detection (rupees→paise)
- ✅ AI interactions logged in immutable journal
- ✅ Deterministic core remains authoritative
```

### 4. Update `DEMO.md`

Add a new section after "Run all self-checking scenarios":

```markdown
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
```

### 5. Copy specification

Copy the full product specification into the source folder:

```bash
cp ../AS/Sutra/external-feed-change-guard-specification.md src/feedguard/specification.md
```

## Constraints

- Use `llama3.2:3b` as the default model (responds cleanly to JSON prompts)
- Strip ANSI escape codes from Ollama output
- Force JSON-only responses (no CoT tokens, no markdown)
- Handle parse failures gracefully (log raw output, continue)
- Do **not** modify deterministic core modules
- Do **not** add network dependencies
- All AI suggestions must have `binding=False`

## Verification

After generating files, run:

```bash
uv sync --extra dev
uv run python scripts/demo_ai_assistance.py
```

Expected output:
- Step 1: "Accepted baseline with 100 rows"
- Step 2: "Disposition: known_variant" (or scenario-dependent)
- Step 3: AI suggestions displayed (may have parse warnings)
- Step 4: "Logged 2 AI interactions"
- Step 5: "AI assistance entries: 2"
- Step 6: All invariants verified
- Final: "DEMO COMPLETE"

## Deliverables

1. All 5 files generated and written to disk
2. Demo runs successfully with `uv run python scripts/demo_ai_assistance.py`
3. Journal created at `demo_ai_journal/journal.jsonl`
4. Git commit: "Add bounded AI assistance demo with local Ollama"

**Do not** stop after writing stubs. **Execute the demo** and verify it runs end-to-end before marking complete.

---

**Start now.** Use AntiGravity's Local Mode to write files directly to `/Users/madhavraop/Code/sutra-feed-guard`.
