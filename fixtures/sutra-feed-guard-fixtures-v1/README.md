# Sutra External Feed Change Guard Fixture Corpus (v1)

This is a deterministic, synthetic test fixture corpus for the **Sutra External Feed Change Guard**. 
The product compares a newly delivered external CSV or JSON feed against an accepted baseline, detects changes, and generates an evidence packet.

## Business Context
Fictional partner **Acme Commerce Services** delivers a daily order feed to a B2B SaaS customer.
All data in this corpus is synthetic and generated deterministically. No real personal data or active business entities are represented.

## Baseline Schema
| Field | Type | Required | Rules |
|---|---|---:|---|
| `order_id` | string | yes | Unique; pattern `ORD-[0-9]{6}` |
| `customer_id` | string | yes | Pattern `CUS-[0-9]{4}`; preserve leading zeros |
| `order_date` | string/date | yes | ISO `YYYY-MM-DD` |
| `exported_at` | string/datetime | yes | ISO-8601 UTC with `Z` |
| `amount` | decimal number | yes | Amount in major currency units; two decimal places; `>= 0` |
| `currency` | string | yes | `INR` or `USD` |
| `status` | string | yes | `PENDING`, `PAID`, `CANCELLED`, or `REFUNDED` |
| `country_code` | string | yes | `IN` or `US` |
| `source_system` | string | yes | Always `ACME_COMMERCE` in accepted historical files |

Field order in baseline CSV files is exactly as listed. JSON numeric amounts use decimal representations but might omit trailing zeros during parsing (semantic equivalence is required).

## Baseline Files
- `historical/orders_2026-07-01` (100 rows, IDs `ORD-000001` - `ORD-000100`)
- `historical/orders_2026-07-02` (100 rows, IDs `ORD-000101` - `ORD-000200`)
- `historical/orders_2026-07-03` (100 rows, IDs `ORD-000201` - `ORD-000300`)

All three daily deliveries differ only in legitimate daily business values (e.g. unique sequential order IDs, varying amounts, dates, and statuses).

## Accepted Policy & Schema Choice
The JSON Schema `contracts/partner_orders.schema.json` sets `additionalProperties: false` to represent the strict, original baseline schema structure. However, the policy defined in `contracts/accepted_policy.yaml` explicitly allows additive fields if they do not modify existing values or violate general rules. Thus, while a strict schema parser would flag the addition of `partner_note`, the policy engine classifies it as `safe_additive`.

## Scenarios Table
| ID | Scenario | Expected Disposition | Exit Code | Description / Rationale |
|---|---|---|---|---|
| 01 | `unchanged` | `unchanged` | 0 | Shuffled row order with varying CSV quoting. Row order is insignificant under the policy. |
| 02 | `safe_additive_column` | `safe_additive` | 0 | Adds optional field `partner_note` (20 rows populated, 80 null). Allowed by policy. |
| 03 | `removed_required_column` | `breaking` | 3 | Removes `currency` field. Violates required fields. |
| 04 | `duplicate_primary_key` | `breaking` | 3 | Replaces the last row's ID with the first row's ID, causing duplicate keys. |
| 05 | `identifier_leading_zero` | `breaking` | 3 | Changes 12 `customer_id` values to lossy formats (e.g., `CUS-7`). Prohibited pattern violation. |
| 06 | `rupees-to-paise_semantic_trap` | `breaking` | 3 | Renames `amount` to `amount_in_paise` and multiplies values by 100. Semantic trap; not a simple alias. |
| 07 | `accepted_field_alias` | `known_variant` | 0 | Renames `amount` to `total_amount`. Mapped successfully by the accepted policy's alias rule. |
| 08 | `malformed_partial_delivery` | `invalid_observation` | 4 | Mid-record file truncation. Exact count is unknown; parsing is incomplete. |

## Rationale for Scenario 06 & 08
- **Scenario 06 (Rupees-to-Paise Trap)**: Changing currency units from major (Rupees/Dollars) to minor (Paise/Cents) is extremely hazardous for downstream systems. Treating it as a harmless rename would cause severe financial logic errors (e.g. interpreting paise as rupees). Hence, it is flagged as `breaking` with multiple critical reasons.
- **Scenario 08 (Malformed Delivery)**: Because the file is truncated mid-record, the parser cannot know how many records were actually in the source file or if the rest of the delivery contained breaking changes. It must report `unknown` affected records and prevent safe classification.

*Note: These fixtures are development and evaluation assets and do not replace real customer incident bundles.*
