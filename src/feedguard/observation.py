"""Load external feed files into a canonical local observation."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Observation:
    format: str
    row_count: int
    fields: tuple[str, ...]
    records: tuple[dict[str, Any], ...]
    source_digest: str
    canonical_digest: str


def _canonical_value(field: str, value: Any) -> Any:
    if value is None:
        return None
    if field in {"amount", "total_amount", "amount_in_paise"}:
        try:
            return format(Decimal(str(value)).normalize(), "f")
        except InvalidOperation:
            return str(value)
    return str(value)


def _canonical_records(records: list[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    normalized = [
        {field: _canonical_value(field, value) for field, value in record.items()}
        for record in records
    ]
    return tuple(sorted(normalized, key=lambda record: json.dumps(record, sort_keys=True)))


def load_observation(path: Path | str) -> Observation:
    source = Path(path)
    raw = source.read_bytes()
    suffix = source.suffix.lower()
    if suffix == ".csv":
        text = raw.decode("utf-8")
        reader = csv.DictReader(text.splitlines(), strict=True)
        records = [dict(record) for record in reader]
        fields = tuple(reader.fieldnames or ())
        file_format = "csv"
    elif suffix == ".json":
        payload = json.loads(raw)
        if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
            raise ValueError("JSON feed must be a top-level array of objects")
        records = [dict(item) for item in payload]
        fields = tuple(records[0].keys()) if records else ()
        file_format = "json"
    else:
        raise ValueError(f"unsupported feed format: {suffix or '<none>'}")

    canonical = _canonical_records(records)
    canonical_bytes = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    return Observation(
        format=file_format,
        row_count=len(records),
        fields=fields,
        records=canonical,
        source_digest=hashlib.sha256(raw).hexdigest(),
        canonical_digest=hashlib.sha256(canonical_bytes).hexdigest(),
    )
