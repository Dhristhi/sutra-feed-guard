"""Tests for bounded AI assistance module."""

import json
from pathlib import Path
from unittest.mock import patch

from feedguard.ai_assist import (
    AISuggestion,
    _hash_prompt,
    _ollama_chat,
    detect_unit_trap,
    log_ai_interaction,
    suggest_field_mapping,
)


FIXTURES = Path(__file__).parents[1] / "fixtures" / "sutra-feed-guard-fixtures-v1"
TMP = Path(__file__).parents[1] / "tmp"


def test_hash_prompt_is_deterministic() -> None:
    h1 = _hash_prompt("test prompt")
    h2 = _hash_prompt("test prompt")
    h3 = _hash_prompt("different prompt")
    assert h1 == h2
    assert h1 != h3
    assert len(h1) == 16


def test_ollama_chat_strips_ansi() -> None:
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = '{"test": true}'
        mock_run.return_value.returncode = 0
        result = _ollama_chat("llama3.2:3b", "test")
        assert "\x1b" not in result
        assert json.loads(result) == {"test": True}


def test_suggest_field_mapping_parses_valid_json() -> None:
    with patch("feedguard.ai_assist._ollama_chat") as mock_chat:
        mock_chat.return_value = '{"mappings": [{"observation": "total_amount", "baseline": "amount", "confidence": 0.95}]}'
        result = suggest_field_mapping(["total_amount"], ["amount"])
        assert result.suggestion_type == "field_mapping"
        assert result.binding is False
        assert result.confidence == 0.95
        assert "mappings" in result.suggestion


def test_suggest_field_mapping_handles_parse_failure() -> None:
    with patch("feedguard.ai_assist._ollama_chat") as mock_chat:
        mock_chat.return_value = "not json at all"
        result = suggest_field_mapping(["field1"], ["field2"])
        assert result.confidence == 0.0
        assert result.suggestion.get("error") == "parse_failed"


def test_detect_unit_trap_detects_rupees_to_paise() -> None:
    with patch("feedguard.ai_assist._ollama_chat") as mock_chat:
        mock_chat.return_value = '{"likely_unit_change": true, "hypothesis": "rupees_to_paise", "confidence": 0.99, "reasoning": "100x ratio"}'
        baseline = [100.0, 200.0, 300.0]
        observation = [10000.0, 20000.0, 30000.0]
        result = detect_unit_trap(baseline, observation)
        assert result.suggestion_type == "unit_trap_detection"
        assert result.confidence == 0.99
        assert result.suggestion.get("likely_unit_change") is True


def test_detect_unit_trap_handles_parse_failure() -> None:
    with patch("feedguard.ai_assist._ollama_chat") as mock_chat:
        mock_chat.return_value = "invalid"
        result = detect_unit_trap([100.0], [100.0])
        assert result.confidence == 0.0
        assert result.suggestion.get("error") == "parse_failed"


def test_log_ai_interaction_writes_to_journal() -> None:
    TMP.mkdir(exist_ok=True)
    journal_dir = TMP / "test_ai_journal"
    if journal_dir.exists():
        import shutil
        shutil.rmtree(journal_dir)

    suggestion = AISuggestion(
        model="llama3.2:3b",
        prompt_hash="abc123",
        suggestion_type="field_mapping",
        suggestion={"test": True},
        confidence=0.95,
        binding=False,
    )

    log_ai_interaction(
        journal_dir=journal_dir,
        suggestion=suggestion,
        deterministic_disposition="known_variant",
        final_disposition="known_variant",
    )

    journal_path = journal_dir / "journal.jsonl"
    assert journal_path.exists()
    lines = journal_path.read_text().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["action"] == "ai_assistance"
    assert entry["model"] == "llama3.2:3b"
    assert entry["binding"] is False
    assert "audit_digest" in entry
