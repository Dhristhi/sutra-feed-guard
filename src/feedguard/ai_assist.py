"""Bounded AI assistance for Feed Guard — local Ollama MLX models only."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class AISuggestion:
    model: str
    prompt_hash: str
    suggestion_type: str
    suggestion: dict[str, Any]
    confidence: float
    binding: bool = False


def _clean_ansi(text: str) -> str:
    """Emulate cursor movement and clear line escape sequences to get clean text."""
    lines = [""]
    r, c = 0, 0
    i = 0
    n = len(text)
    while i < n:
        char = text[i]
        if char == '\n':
            r += 1
            if r >= len(lines):
                lines.append("")
            c = 0
            i += 1
        elif char == '\r':
            c = 0
            i += 1
        elif char == '\b':
            c = max(0, c - 1)
            i += 1
        elif char == '\x1b':
            if i + 1 < n and text[i+1] == '[':
                j = i + 2
                while j < n and not text[j].isalpha():
                    j += 1
                if j < n:
                    cmd = text[j]
                    args = text[i+2:j]
                    if cmd == 'D':
                        dist = int(args) if args.isdigit() else 1
                        c = max(0, c - dist)
                    elif cmd == 'K':
                        mode = int(args) if args.isdigit() else 0
                        if mode == 0:
                            lines[r] = lines[r][:c]
                        elif mode == 1:
                            lines[r] = " " * c + lines[r][c:]
                        elif mode == 2:
                            lines[r] = ""
                    i = j + 1
                else:
                    i += 1
            else:
                i += 1
        else:
            line = lines[r]
            if c < len(line):
                lines[r] = line[:c] + char + line[c+1:]
            else:
                lines[r] = line + " " * (c - len(line)) + char
            c += 1
            i += 1
    return "\n".join(lines)


def _ollama_chat(model: str, prompt: str) -> str:
    """Call local Ollama with MLX model. No network calls."""
    full_prompt = f"""You must respond with ONLY valid JSON. No explanations, no thinking tokens, no markdown.

{prompt}

JSON response:"""
    result = subprocess.run(
        ["ollama", "run", model, "--format", "json", "--nowordwrap", full_prompt],
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Ollama failed: {result.stderr}")
    return _clean_ansi(result.stdout)


def _hash_prompt(prompt: str) -> str:
    import hashlib
    return hashlib.sha256(prompt.encode()).hexdigest()[:16]


def suggest_field_mapping(
    observation_fields: list[str],
    baseline_fields: list[str],
    model: str = "llama3.2:3b",
) -> AISuggestion:
    """Suggest field mappings between observation and baseline."""
    prompt = f"""You are a data integration assistant. Suggest field mappings between an observation feed and an accepted baseline.

Baseline fields: {", ".join(baseline_fields)}
Observation fields: {", ".join(observation_fields)}

Return ONLY valid JSON with this structure:
{{
  "mappings": [
    {{"observation": "field_name", "baseline": "field_name", "confidence": 0.95}}
  ],
  "unmapped_observation": ["field1"],
  "unmapped_baseline": ["field2"]
}}

Rules:
- Match semantically equivalent fields (e.g., total_amount → amount)
- Do not map fields with different units (e.g., amount vs amount_in_paise)
- Confidence must be 0.0-1.0
- Leave unmapped if uncertain"""

    response = _ollama_chat(model, prompt)
    try:
        # Try to extract JSON from response (may have trailing whitespace)
        response = response.strip()
        # Find first { and last }
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            suggestion_json = json.loads(response[start:end])
        else:
            raise json.JSONDecodeError("No JSON found", response, 0)
        confidence = sum(m.get("confidence", 0.5) for m in suggestion_json.get("mappings", [])) / max(len(suggestion_json.get("mappings", [1])), 1)
    except (json.JSONDecodeError, ValueError, KeyError, TypeError) as e:
        suggestion_json = {"error": "parse_failed", "raw": response[:300]}
        confidence = 0.0

    return AISuggestion(
        model=model,
        prompt_hash=_hash_prompt(prompt),
        suggestion_type="field_mapping",
        suggestion=suggestion_json,
        confidence=confidence,
        binding=False,
    )


def detect_unit_trap(
    baseline_amounts: list[float],
    observation_amounts: list[float],
    model: str = "llama3.2:3b",
) -> AISuggestion:
    """Detect potential unit changes (e.g., rupees → paise)."""
    prompt = f"""You are a data quality assistant. Detect if amounts changed units between baseline and observation.

Baseline amounts (sample): {baseline_amounts[:10]}
Observation amounts (sample): {observation_amounts[:10]}
Baseline mean: {sum(baseline_amounts)/len(baseline_amounts):.2f}
Observation mean: {sum(observation_amounts)/len(observation_amounts):.2f}
Ratio: {(sum(observation_amounts)/len(observation_amounts)) / max(sum(baseline_amounts)/len(baseline_amounts), 0.01):.2f}x

Rules:
- If the Ratio is approximately 100.00x, then set likely_unit_change to true, hypothesis to rupees_to_paise (or dollars_to_cents depending on currency), and confidence to 0.95.
- If the Ratio is approximately 1.00x, then set likely_unit_change to false, hypothesis to none, and confidence to 1.00.

Return ONLY valid JSON:
{{
  "likely_unit_change": true/false,
  "hypothesis": "rupees_to_paise" | "dollars_to_cents" | "none",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}}"""

    response = _ollama_chat(model, prompt)
    try:
        response = response.strip()
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            suggestion_json = json.loads(response[start:end])
        else:
            raise json.JSONDecodeError("No JSON found", response, 0)
        confidence = suggestion_json.get("confidence", 0.5)
    except (json.JSONDecodeError, ValueError, KeyError, TypeError) as e:
        suggestion_json = {"error": "parse_failed", "raw": response[:300]}
        confidence = 0.0

    return AISuggestion(
        model=model,
        prompt_hash=_hash_prompt(prompt),
        suggestion_type="unit_trap_detection",
        suggestion=suggestion_json,
        confidence=confidence,
        binding=False,
    )


def log_ai_interaction(
    journal_dir: Path | str,
    suggestion: AISuggestion,
    deterministic_disposition: str,
    final_disposition: str,
) -> None:
    """Log AI interaction in journal with full audit trail."""
    import hashlib
    from datetime import datetime, timezone

    journal_path = Path(journal_dir) / "journal.jsonl"
    journal_path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "version": 1,
        "action": "ai_assistance",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": suggestion.model,
        "prompt_hash": suggestion.prompt_hash,
        "suggestion_type": suggestion.suggestion_type,
        "suggestion": suggestion.suggestion,
        "confidence": suggestion.confidence,
        "binding": suggestion.binding,
        "deterministic_disposition": deterministic_disposition,
        "final_disposition": final_disposition,
        "ai_overridden": deterministic_disposition != final_disposition and suggestion.binding,
        "audit_digest": hashlib.sha256(
            json.dumps(suggestion.suggestion, sort_keys=True).encode()
        ).hexdigest(),
    }

    with open(journal_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
