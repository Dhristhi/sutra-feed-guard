"""Generate HTML and JSON evidence reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from feedguard.classification import ClassificationResult


def render_html_report(
    baseline_name: str,
    observation_name: str,
    result: ClassificationResult,
    output_path: Path | str,
) -> None:
    disposition_colors = {
        "unchanged": "#22c55e",
        "safe_additive": "#84cc16",
        "known_variant": "#06b6d4",
        "review_required": "#f59e0b",
        "breaking": "#ef4444",
        "invalid_observation": "#7f1d1d",
    }

    color = disposition_colors.get(result.disposition, "#6b7280")

    reason_items = "".join(f"<li><code>{r}</code></li>" for r in result.reason_codes)

    if result.affected_count is None:
        affected_html = "<p><strong>Affected records:</strong> unknown (parsing failed)</p>"
    else:
        affected_html = f"<p><strong>Affected records:</strong> {result.affected_count:,}</p>"

    if result.affected_order_ids:
        ids_preview = ", ".join(result.affected_order_ids[:10])
        if len(result.affected_order_ids) > 10:
            ids_preview += f" … and {len(result.affected_order_ids) - 10} more"
        affected_html += f"<p><strong>Affected IDs:</strong> {ids_preview}</p>"

    if result.nonempty_new_value_count is not None:
        affected_html += f"<p><strong>Non-empty new values:</strong> {result.nonempty_new_value_count:,}</p>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Feed Guard Report — {result.disposition.replace('_', ' ').title()}</title>
<style>
  :root {{ --fg: #111827; --muted: #6b7280; --border: #e5e7eb; --bg: #ffffff; --card: #f9fafb; }}
  body {{ font-family: system-ui, -apple-system, sans-serif; color: var(--fg); background: var(--bg); margin: 0; padding: 2rem; }}
  .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 1.5rem; max-width: 720px; margin: 0 auto; }}
  h1 {{ font-size: 1.25rem; margin: 0 0 1rem 0; }}
  .status {{ display: inline-block; padding: 0.25rem 0.75rem; border-radius: 999px; color: white; font-weight: 600; background: {color}; }}
  .meta {{ color: var(--muted); font-size: 0.875rem; margin: 1rem 0; }}
  .section {{ margin-top: 1.5rem; border-top: 1px solid var(--border); padding-top: 1rem; }}
  code {{ background: #f3f4f6; padding: 0.125rem 0.375rem; border-radius: 4px; font-size: 0.875rem; }}
  ul {{ margin: 0.5rem 0; padding-left: 1.5rem; }}
</style>
</head>
<body>
<div class="card">
<h1>Feed Guard Classification Report</h1>
<p><span class="status">{result.disposition.replace('_', ' ').title()}</span></p>
<div class="meta">
<p><strong>Baseline:</strong> {baseline_name}<br>
<strong>Observation:</strong> {observation_name}<br>
<strong>Exit code:</strong> {result.exit_code}</p>
</div>
<div class="section">
<h2>Classification</h2>
<p><strong>Primary reason:</strong> <code>{result.primary_reason}</code></p>
<p><strong>Reason codes:</strong></p>
<ul>{reason_items}</ul>
{affected_html}
<p><strong>Changed fields:</strong> {', '.join(result.changed_fields) if result.changed_fields else '<em>none</em>'}</p>
</div>
</div>
</body>
</html>
"""
    Path(output_path).write_text(html, encoding="utf-8")


def render_json_envelope(
    baseline_name: str,
    observation_name: str,
    result: ClassificationResult,
    output_path: Path | str,
) -> None:
    envelope = {
        "version": 1,
        "baseline_name": baseline_name,
        "observation_name": observation_name,
        "disposition": result.disposition,
        "exit_code": result.exit_code,
        "primary_reason": result.primary_reason,
        "reason_codes": list(result.reason_codes),
        "affected_count": result.affected_count,
        "nonempty_new_value_count": result.nonempty_new_value_count,
        "changed_fields": list(result.changed_fields),
        "affected_order_ids": list(result.affected_order_ids),
    }
    Path(output_path).write_text(json.dumps(envelope, indent=2, sort_keys=True), encoding="utf-8")
