# API Reference — Sutra Feed Guard

## `feedguard.observation`

### `load_observation(path: Path | str) -> Observation`

Load a CSV or JSON feed file into a canonical observation.

**Parameters:**
- `path`: Path to `.csv` or `.json` file

**Returns:**
- `Observation` with normalized records and digests

**Raises:**
- `ValueError` if format is unsupported or JSON is not an array of objects
- `csv.Error` if CSV is malformed

**Example:**
```python
from feedguard.observation import load_observation
obs = load_observation("data/feed.csv")
print(obs.row_count, obs.canonical_digest)
```

---

## `feedguard.classification`

### `classify_change(baseline_path, observation_path, policy_path) -> ClassificationResult`

Classify the change between a baseline and an observation feed.

**Parameters:**
- `baseline_path`: Path to accepted baseline CSV or JSON
- `observation_path`: Path to new observation CSV or JSON
- `policy_path`: Path to `accepted_policy.yaml`

**Returns:**
- `ClassificationResult` with disposition, exit code, and affected counts

**Example:**
```python
from feedguard.classification import classify_change

result = classify_change(
    baseline_path="accepted/baseline.csv",
    observation_path="new/feed.csv",
    policy_path="contracts/policy.yaml",
)

if result.exit_code == 3:
    print(f"BLOCK: {result.primary_reason}")
elif result.exit_code == 2:
    print(f"REVIEW: {result.primary_reason}")
else:
    print(f"OK: {result.disposition}")
```

---

## `feedguard.journal`

### `accept_baseline(baseline_path, policy_path, journal_dir) -> Journal`

Accept a baseline feed and create an audit journal.

**Parameters:**
- `baseline_path`: Path to baseline CSV or JSON
- `policy_path`: Path to policy YAML
- `journal_dir`: Directory for journal output

**Returns:**
- `Journal` object with append-only log

**Side effects:**
- Creates `journal_dir/accepted/baseline.canonical.json`
- Creates `journal_dir/accepted/policy.yaml`
- Creates `journal_dir/accepted/envelope.json`
- Creates `journal_dir/journal.jsonl`

**Example:**
```python
from feedguard.journal import accept_baseline

journal = accept_baseline(
    baseline_path="data/baseline.csv",
    policy_path="contracts/policy.yaml",
    journal_dir=".feedguard",
)

print(f"Accepted {journal.entries[0]['row_count']} rows")
```

---

## `feedguard.report`

### `render_html_report(baseline_name, observation_name, result, output_path)`

Generate a human-readable HTML evidence report.

**Parameters:**
- `baseline_name`: Display name for baseline
- `observation_name`: Display name for observation
- `result`: `ClassificationResult` from `classify_change`
- `output_path`: Path for output HTML file

**Example:**
```python
from feedguard.report import render_html_report

render_html_report(
    baseline_name="orders_2026-07-03.csv",
    observation_name="scenario_03.csv",
    result=result,
    output_path="reports/scenario_03.html",
)
```

---

### `render_json_envelope(baseline_name, observation_name, result, output_path)`

Generate a machine-readable JSON evidence envelope.

**Parameters:** same as `render_html_report`

**Example:**
```python
from feedguard.report import render_json_envelope

render_json_envelope(
    baseline_name="orders_2026-07-03.csv",
    observation_name="scenario_03.csv",
    result=result,
    output_path="reports/scenario_03.json",
)
```

---

## `feedguard.ai_assist`

### `AISuggestion` (dataclass)

```python
@dataclass
class AISuggestion:
    model: str                    # e.g., "llama3.2:3b"
    prompt_hash: str              # SHA-256 first 16 chars
    suggestion_type: str          # "field_mapping" | "unit_trap_detection"
    suggestion: dict[str, Any]    # Model output (parsed JSON)
    confidence: float             # 0.0-1.0
    binding: bool = False         # Always False (non-binding)
```

### `suggest_field_mapping(observation_fields, baseline_fields, model="llama3.2:3b") -> AISuggestion`

Suggest field mappings between observation and baseline feeds.

**Parameters:**
- `observation_fields`: List of field names in observation
- `baseline_fields`: List of field names in baseline
- `model`: Ollama model name (default: `"llama3.2:3b"`)

**Returns:**
- `AISuggestion` with mappings and confidence

**Example:**
```python
from feedguard.ai_assist import suggest_field_mapping

suggestion = suggest_field_mapping(
    observation_fields=["total_amount", "order_id"],
    baseline_fields=["amount", "order_id"],
)

if suggestion.confidence > 0.9:
    print(f"Suggested: {suggestion.suggestion['mappings']}")
```

### `detect_unit_trap(baseline_amounts, observation_amounts, model="llama3.2:3b") -> AISuggestion`

Detect potential unit changes (rupees→paise, dollars→cents).

**Parameters:**
- `baseline_amounts`: List of baseline amount values
- `observation_amounts`: List of observation amount values
- `model`: Ollama model name

**Returns:**
- `AISuggestion` with hypothesis and reasoning

### `log_ai_interaction(journal_dir, suggestion, deterministic_disposition, final_disposition)`

Log AI interaction in journal with full audit trail.

**Parameters:**
- `journal_dir`: Path to journal directory
- `suggestion`: `AISuggestion` object
- `deterministic_disposition`: Core classification result
- `final_disposition`: Final decision (may differ if human overrides)

**Side effects:**
- Appends to `journal.jsonl` with timestamp, prompt_hash, audit_digest

---

## `feedguard.cli`

Command-line interface (entry point: `feedguard`).

### `feedguard accept <baseline> <policy> -o <journal_dir>`

Accept a baseline feed.

**Example:**
```bash
feedguard accept data/baseline.csv contracts/policy.yaml -o .feedguard
```

### `feedguard check <baseline> <observation> <policy> [-o <output_dir>]`

Check an observation against baseline.

**Example:**
```bash
feedguard check accepted/baseline.csv new/feed.csv contracts/policy.yaml -o reports
echo "Exit code: $?"  # 0, 2, 3, or 4
```

**Exit codes:**
- `0`: unchanged / safe_additive / known_variant
- `2`: review_required
- `3`: breaking
- `4`: invalid_observation

---

## Data classes

### `Observation`

```python
@dataclass(frozen=True)
class Observation:
    format: str
    row_count: int
    fields: tuple[str, ...]
    records: tuple[dict[str, Any], ...]
    source_digest: str
    canonical_digest: str
```

### `ClassificationResult`

```python
@dataclass(frozen=True)
class ClassificationResult:
    disposition: str
    exit_code: int
    primary_reason: str
    reason_codes: tuple[str, ...]
    affected_count: int | None
    nonempty_new_value_count: int | None
    changed_fields: tuple[str, ...]
    affected_order_ids: tuple[str, ...]
```

### `Journal`

```python
@dataclass
class Journal:
    dir: Path
    entries: list[dict[str, Any]]
    
    def append(self, entry: dict[str, Any]) -> None:
        """Append entry to journal.jsonl with UTC timestamp."""
```
