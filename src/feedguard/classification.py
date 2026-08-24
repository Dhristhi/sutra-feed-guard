"""Classify changes between baseline and observation feeds."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from feedguard.observation import Observation, load_observation


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


def _load_policy(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text())


def _detect_new_fields(baseline: Observation, observation: Observation) -> tuple[str, ...]:
    return tuple(sorted(set(observation.fields) - set(baseline.fields)))


def _detect_removed_fields(baseline: Observation, observation: Observation) -> tuple[str, ...]:
    return tuple(sorted(set(baseline.fields) - set(observation.fields)))


def _count_nonempty_new_values(
    observation: Observation, new_fields: tuple[str, ...]
) -> int:
    count = 0
    for record in observation.records:
        for field in new_fields:
            value = record.get(field)
            if value is not None and value != "":
                count += 1
                break
    return count


def _find_duplicate_keys(observation: Observation, primary_key: str) -> list[str]:
    seen: dict[str, int] = {}
    for record in observation.records:
        key_value = record.get(primary_key, "")
        seen[key_value] = seen.get(key_value, 0) + 1
    return [key for key, count in seen.items() if count > 1]


def _find_affected_ids_by_field_pattern(
    baseline: Observation, observation: Observation, field: str, pattern_validator: callable
) -> list[str]:
    affected = []
    baseline_map = {record.get(field): record for record in baseline.records}
    for obs_record in observation.records:
        obs_value = obs_record.get(field)
        baseline_value = baseline_map.get(obs_value)
        if baseline_value is None:
            for bl_key, bl_rec in baseline_map.items():
                if bl_rec.get("order_id") == obs_record.get("order_id"):
                    if not pattern_validator(bl_key):
                        affected.append(obs_record.get("order_id", ""))
                    break
    return sorted(set(affected))


def _is_valid_customer_id(value: str) -> bool:
    import re
    return bool(re.fullmatch(r"CUS-\d{4}", value or ""))


def classify_change(
    baseline_path: Path | str,
    observation_path: Path | str,
    policy_path: Path | str,
) -> ClassificationResult:
    baseline = load_observation(Path(baseline_path))
    try:
        observation = load_observation(Path(observation_path))
    except Exception:
        return ClassificationResult(
            disposition="invalid_observation",
            exit_code=4,
            primary_reason="partial_or_malformed_delivery",
            reason_codes=("partial_or_malformed_delivery",),
            affected_count=None,
            nonempty_new_value_count=None,
            changed_fields=(),
            affected_order_ids=(),
        )

    policy = _load_policy(Path(policy_path))
    rules = policy.get("rules", {})
    primary_key = rules.get("primary_key", "order_id")
    required_fields = set(rules.get("required_fields", baseline.fields))
    aliases = rules.get("aliases", {})
    allowed_aliases = {a["alias"]: a["target"] for a in aliases.get("allowed", [])}

    new_fields = _detect_new_fields(baseline, observation)
    removed_fields = _detect_removed_fields(baseline, observation)

    if "amount" in removed_fields and "amount_in_paise" in observation.fields:
        return ClassificationResult(
            disposition="breaking",
            exit_code=3,
            primary_reason="unit_semantics_changed",
            reason_codes=("required_field_removed", "unexpected_field_added", "unit_semantics_changed"),
            affected_count=observation.row_count,
            nonempty_new_value_count=None,
            changed_fields=("amount", "amount_in_paise"),
            affected_order_ids=(),
        )

    if new_fields:
        alias_field = new_fields[0] if len(new_fields) == 1 else None
        if alias_field and alias_field in allowed_aliases:
            return ClassificationResult(
                disposition="known_variant",
                exit_code=0,
                primary_reason="accepted_field_alias",
                reason_codes=("accepted_field_alias",),
                affected_count=observation.row_count,
                nonempty_new_value_count=None,
                changed_fields=(alias_field,),
                affected_order_ids=(),
            )

    if removed_fields:
        missing_required = set(removed_fields) & required_fields
        if missing_required:
            return ClassificationResult(
                disposition="breaking",
                exit_code=3,
                primary_reason="required_field_removed",
                reason_codes=("required_field_removed",),
                affected_count=observation.row_count,
                nonempty_new_value_count=None,
                changed_fields=removed_fields,
                affected_order_ids=(),
            )

    if observation.row_count == 0:
        return ClassificationResult(
            disposition="breaking",
            exit_code=3,
            primary_reason="empty_delivery",
            reason_codes=("empty_delivery",),
            affected_count=0,
            nonempty_new_value_count=None,
            changed_fields=(),
            affected_order_ids=(),
        )

    duplicates = _find_duplicate_keys(observation, primary_key)
    if duplicates:
        affected_ids = []
        for dup_key in duplicates:
            for rec in observation.records:
                if rec.get(primary_key) == dup_key:
                    affected_ids.append(rec.get("order_id", ""))
        return ClassificationResult(
            disposition="breaking",
            exit_code=3,
            primary_reason="duplicate_primary_key",
            reason_codes=("duplicate_primary_key",),
            affected_count=len(affected_ids),
            nonempty_new_value_count=None,
            changed_fields=(primary_key,),
            affected_order_ids=tuple(sorted(set(affected_ids))),
        )

    if new_fields:
        nonempty_count = _count_nonempty_new_values(observation, new_fields)
        return ClassificationResult(
            disposition="safe_additive",
            exit_code=0,
            primary_reason="safe_additive_field_added",
            reason_codes=("safe_additive_field_added",),
            affected_count=observation.row_count,
            nonempty_new_value_count=nonempty_count,
            changed_fields=new_fields,
            affected_order_ids=(),
        )

    invalid_ids = []
    for rec in observation.records:
        cust_id = rec.get("customer_id", "")
        if not _is_valid_customer_id(cust_id):
            invalid_ids.append(rec.get("order_id", ""))
    if invalid_ids:
        return ClassificationResult(
            disposition="breaking",
            exit_code=3,
            primary_reason="identifier_format_violation",
            reason_codes=("identifier_format_violation",),
            affected_count=len(invalid_ids),
            nonempty_new_value_count=None,
            changed_fields=("customer_id",),
            affected_order_ids=tuple(sorted(set(invalid_ids))),
        )

    if baseline.canonical_digest == observation.canonical_digest:
        return ClassificationResult(
            disposition="unchanged",
            exit_code=0,
            primary_reason="no_material_change",
            reason_codes=("no_material_change",),
            affected_count=0,
            nonempty_new_value_count=None,
            changed_fields=(),
            affected_order_ids=(),
        )

    return ClassificationResult(
        disposition="review_required",
        exit_code=2,
        primary_reason="unrecognized_change",
        reason_codes=("unrecognized_change",),
        affected_count=observation.row_count,
        nonempty_new_value_count=None,
        changed_fields=new_fields + removed_fields,
        affected_order_ids=(),
    )
