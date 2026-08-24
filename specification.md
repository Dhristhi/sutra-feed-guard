---
title: "Sutra External Feed Change Guard — Product and Technical Specification"
version: "0.1.0"
date: "2026-08-24"
status: "VALIDATION SPECIFICATION — four-week paid experiment; not a commitment to the full Sutra platform"
parent_product: "Sutra Studio"
positioning: "Dependabot for external data feeds, with a reproducible incident packet"
implements: "Evidence-generating bridge experiment adjacent to the accepted wedge in CONCEPT_REFINEMENT.md; market gates in MARKET_ASSESSMENT.md"
scope: "Local-first CLI and GitHub Action for CSV/JSON feeds. Baseline, observe, classify, review, accept, and report. No production writes, connector runtime, or hosted control plane in the committed build."
---

# Sutra External Feed Change Guard

## 1. Decision and product contract

**External Feed Change Guard detects consequential changes in third-party CSV and JSON feeds before those changes silently corrupt or break downstream systems.** It compares a new observation with an explicitly accepted baseline, evaluates deterministic policy, proposes bounded explanations or mapping candidates where useful, and produces a reproducible decision envelope for internal review or partner escalation.

Its customer-facing job is:

> Before an upstream vendor, customer, public source, or partner changes a feed we do not control, show us exactly what changed, which assumptions are exposed, whether policy permits continuation, and the evidence needed to review or escalate it.

Its operating loop is:

```text
Observe external feed
→ parse and fingerprint locally
→ compare with accepted baseline and accepted variants
→ evaluate deterministic rules
→ optionally suggest bounded semantic correspondences
→ classify the observation
→ emit a decision envelope
→ human accepts, rejects, or records a known variant
```

The first release is **observational and fail-safe**. It does not transform data, publish records, update a warehouse, or repair a source. It may block a CI job or return a non-zero exit code, but it never writes to a production destination.

### 1.1 Relationship to Sutra

External Feed Change Guard is the first narrow utility within **Sutra Studio**, not a separate platform:

```text
Sutra
└── Sutra Studio
    └── External Feed Change Guard
```

It tests reusable Sutra concepts:

- deterministic processes with named bounded-uncertainty tasks;
- typed contracts and explicit invariants;
- local/private execution;
- immutable approval binding;
- source-specific resolution history;
- state reconstruction and run comparison;
- independently checkable outcomes;
- evidence rather than autonomous remediation.

It does **not** validate the full accepted Sutra proof: it does not execute a
deterministic transform, publish or quarantine records, exercise the AHE
Kernel/Runtime seam, demonstrate local/hosted transition equality, compensate
for an external effect, or enumerate the blast radius of a transformation
already used downstream. It is an evidence-generating bridge: success earns a
vertical shadow-mode workflow; it does not by itself validate Sutra.

It does **not** require the full AHE Kernel, AHE Runtime, Sutra Runtime, or Sutra Control Plane. The validation implementation should remain replaceable. Product learning is the objective; architectural extraction follows demonstrated pressure.

### 1.2 Success condition

The experiment succeeds only if real operators repeatedly use and pay for the acceptance/evidence workflow—not merely for schema inference or a prettier file diff.

The principal hypothesis is:

> Teams responsible for unowned external feeds will pay to preserve source-specific accepted-variant history and produce a reproducible record of what changed, why it was allowed or blocked, and what downstream assumptions were affected.

---

## 2. Users, jobs, and operating context

### 2.1 Initial ideal customer profile

- 10–200-person B2B SaaS or integration-heavy technology company;
- lean data, platform, implementation, or integration team;
- 5–50 recurring third-party CSV or JSON feeds;
- upstream formats are not under the team's version control;
- current checks are fixtures, scripts, JSON Schema, Pandera, Frictionless, GX, Soda, connector settings, or manual inspection;
- a feed incident costs at least two engineer-hours or creates a material customer delay.

### 2.2 Personas

| Persona | Responsibility | Product need |
|---|---|---|
| Integration/data engineer | Maintains ingestion and responds to failures | Fast, precise classification and reproduction |
| Engineering lead | Owns reliability and tool spend | Low-noise controls, installation and retention value |
| Implementation/migration engineer | Handles customer-specific files | Reusable variants and partner-facing evidence |
| QA engineer | Validates pipeline and migration outputs | Deterministic fixtures and machine-readable results |
| Security reviewer | Controls data egress | Local processing, redaction, explicit upload posture |
| Source/partner owner | Must remediate an upstream change | Sanitized report with exact examples and contract impact |

### 2.3 Primary jobs to be done

1. **Baseline a feed:** capture the accepted structural and behavioural envelope from representative historical observations.
2. **Detect drift:** identify structural, type, constraint, cardinality, distribution, and freshness changes.
3. **Classify risk:** distinguish harmless additive change, accepted variation, review-worthy ambiguity, and deterministic breakage.
4. **Explain impact:** name the exact fields, rules, assumptions, and bounded records involved.
5. **Review safely:** let a human accept, reject, or record a narrowly scoped variant without silently replacing history.
6. **Escalate upstream:** generate a redacted, reproducible packet suitable for a vendor, customer, or incident channel.
7. **Regress the adapter:** generate or update fixtures and test suggestions without modifying production code automatically.

### 2.4 Non-users in v0.1

- business users needing a general spreadsheet cleaner;
- product teams embedding a customer-facing CSV importer;
- warehouse teams seeking full lineage and observability;
- organizations seeking managed ETL, SFTP, or data movement;
- teams wanting automatic mapping and publication without review.

---

## 3. Scope and release boundary

### 3.1 Week-one/two committed validation build

| Surface | Included |
|---|---|
| Execution | Local CLI on macOS/Linux; CI-compatible exit codes |
| Sources | Local CSV and local JSON; HTTPS only when required by a supplied incident |
| Baseline | Candidate inference from 1–5 observations; one sample is visibly weak; explicit human acceptance |
| Detection | Structural, type, nullability, key, enum, volume, and configured control checks required by supplied incidents |
| Classification | `unchanged`, `safe_additive`, `known_variant`, `review_required`, `breaking`, `invalid_observation` |
| Review | CLI acceptance/rejection plus attributed digest-bound decision record |
| History | Append-only local journal and immutable content-addressed artefacts |
| Outputs | Canonical JSON and one self-contained HTML incident packet; exit code; redacted examples |
| Automation | GitHub Action for trusted-branch pull requests/manual runs; no durable schedule before hosted state exists |
| Interop | JSON Schema import for constraints needed by the incident corpus |
| AI | Deferred unless a paid incident cannot be resolved without testing alias suggestions |

### 3.2 Conditional build after collected paid evidence

Only after at least three customers have made collected, non-refundable pilot
payments (or signed paid purchase orders with a defined start date):

- lightweight result endpoint receiving fingerprints and redacted summaries;
- GitHub login and repository/feed registration;
- schedule management;
- email/Slack notification;
- 30-day decision history;
- sanitized share link;
- Stripe plan enforcement.

The broader profiling surface, distribution drift, ODCS export, Markdown
projection, remote model providers, export/delete UI, performance hardening,
and signed multi-user approval are also conditional backlog. Their requirements
below define intended semantics if promoted; they are not week-one/two build
commitments.

### 3.3 Explicitly excluded

- production transformation or publication;
- arbitrary Python/SQL execution inside policy;
- S3, SFTP, Kafka, database, or warehouse connectors;
- raw-file cloud retention by default;
- embedded import UI;
- broad data observability or lineage crawling;
- automatic contract mutation;
- automatic acceptance of breaking or ambiguous changes;
- automatic remediation;
- workflow designer or general agent builder;
- Jira/Slack bidirectional incident workflow;
- SSO, SCIM, enterprise RBAC, tenancy, billing metering;
- Sutra Control Plane and fleet scheduling.

A request for an excluded feature is evidence to record, not permission to expand the four-week build.

---

## 4. Core concepts and invariants

### 4.1 Feed

A **Feed** is a stable logical external source whose individual deliveries are observations. Its identity is chosen by the user and is independent of filenames or URLs.

```yaml
feed_id: acme_daily_orders
owner: integrations
format: csv
source:
  kind: https
  uri: https://partner.example/orders.csv
```

### 4.2 Observation

An **Observation** is the immutable result of acquiring and parsing one source delivery. It contains:

- `observation_id`;
- `feed_id`;
- acquisition time and source metadata;
- raw content digest;
- parser and canonicalizer versions;
- schema fingerprint;
- metric fingerprint;
- bounded or redacted evidence samples;
- acquisition and parsing outcome.

The raw digest is calculated over the exact acquired bytes. Canonical fingerprints are calculated over documented canonical forms; neither substitutes for the other.

### 4.3 Baseline

A **Baseline** is an explicitly accepted contract state used for comparison. It contains:

- baseline ID and version;
- one or more accepted schema variants;
- rules and severity policy;
- accepted statistical bands;
- key and identity declarations;
- provenance to observations used to propose it;
- approval record and immutable digest.

A baseline is never silently learned or re-centred. `init` produces a **candidate**; only `accept` promotes it.

### 4.4 Accepted variant

An **Accepted Variant** is a narrow exception or normalization attached to a baseline, such as:

- an approved field alias;
- a known date representation;
- a tolerated enum extension;
- an expected seasonal row-count band;
- an explicitly ignored additive field.

Every variant must define scope and expiry/review posture. A variant is not permission to weaken unrelated rules.

### 4.5 Rule set

A **Rule Set** is a versioned deterministic policy. Rules evaluate observations and diffs; they do not call a model. Each rule declares:

- stable rule ID;
- target path/field;
- predicate;
- severity;
- evidence requirements;
- disposition contribution;
- optional variant scope.

### 4.6 Change Set

A **Change Set** is the deterministic comparison between an observation and a baseline. It contains typed findings with before/after evidence and affected-rule references.

### 4.7 Decision envelope

The **Feed Decision Envelope** is the durable product artefact:

```text
feed identity
+ observation digest and source metadata
+ baseline/rule/variant digests
+ deterministic findings and classification
+ bounded suggestion records
+ redacted evidence
+ downstream assumption references
+ human decision and actor
+ exact reproduction command
+ tool/parser/model versions
```

The envelope digest binds the review decision to one exact execution context.

### 4.8 Hard invariants

1. No accepted baseline or variant is created without an attributed human action.
2. No model output directly determines pass, fail, or acceptance.
3. No baseline is modified in place; changes create new immutable versions.
4. Every classification can be reproduced from retained inputs or declared fingerprints, policy versions, and tool versions.
5. Every finding references a stable rule or a declared heuristic category.
6. Every redaction is explicit in the envelope; absence of raw evidence is not represented as full evidence.
7. A failed or partial parse cannot be classified as safe.
8. An unknown policy state fails to `review_required` or `breaking`, never to safe.
9. The committed product performs no writes to customer feed-processing or
   business-data production destinations. Allowed operational side effects are
   local journal/object/report writes and, when explicitly enabled, GitHub job
   summaries/artefacts and conditional hosted result/notification/billing
   records. Every non-local side effect is declared in the envelope.
10. Hosted v0.1 receives no raw bytes or literal samples. A future encrypted
    sample mode requires a separate specification for encryption, retention,
    deletion, access audit, and consent; it is not authorized here.
11. An editable configuration, policy, baseline, or variant file is a proposal,
    not accepted state. `check` may return a safe exit only when every
    decision-affecting digest matches the accepted content-addressed state.

### 4.9 Accepted-state authority

SQLite journal records plus content-addressed accepted objects are authoritative.
Editable `feedguard.yaml`, baseline exports, and variant YAML files are authoring
surfaces. `feedguard check` computes their digests and compares them with the
current accepted-state record:

- exact match: authoritative evaluation may proceed;
- no accepted state: evaluation is preview-only and returns `review_required`;
- changed policy/baseline/variant digest: evaluation records a proposal and
  returns `review_required`, even if the proposed policy would otherwise pass;
- promotion: `accept` binds the proposed object set, parent accepted-state
  digest, actor/signature posture, and envelope digest in one journal append.

No file committed by an untrusted pull request can become authoritative merely
because it exists in the checkout.

---

## 5. Functional requirements

Requirement identifiers are stable within this specification.

### 5.1 Feed registration and configuration

**FG-CONF-001 — Feed identity.** The user shall create a feed with a unique `feed_id`, format, source declaration, ownership metadata, and policy file.

**FG-CONF-002 — Configuration validation.** Invalid or incomplete configuration shall fail before source acquisition with path-specific diagnostics.

**FG-CONF-003 — Environment separation.** Credentials and tokens shall be references to environment/keychain/CI secrets, never serialized into feed configuration, reports, or journals.

**FG-CONF-004 — Interoperability.** The product shall import JSON Schema and shall not invent a proprietary equivalent where the external standard expresses the same constraint. ODCS mappings may initially be partial but must report unsupported fields.

**FG-CONF-005 — Declarative policy.** v0.1 policy shall support a small typed YAML surface; it shall not execute arbitrary code.

**FG-CONF-006 — Accepted digest enforcement.** Authoritative `check` execution
shall reject any policy, baseline, variant, parser, or redaction digest that is
not the current accepted object set. Editable files are proposals only.

### 5.2 Acquisition

**FG-ACQ-001 — Local file.** Acquire CSV or JSON from an explicit local path.

**FG-ACQ-002 — HTTPS.** Acquire CSV or JSON over HTTPS with bounded timeout, byte ceiling, redirect ceiling, and optional bearer/header secret references.

**FG-ACQ-003 — Conditional request.** HTTPS acquisition should support ETag and Last-Modified to avoid redundant downloads while still journalling the check result.

**FG-ACQ-004 — Content identity.** Compute SHA-256 over exact source bytes before parsing.

**FG-ACQ-005 — Safety limits.** Refuse decompression bombs, unsupported content types, byte-limit violations, and malformed encodings with `invalid_observation`.

**FG-ACQ-006 — No hidden sampling.** If profiling uses a sample rather than all rows, the sampling method, seed, bounds, and coverage shall be recorded.

**FG-ACQ-007 — HTTPS boundary.** If HTTPS acquisition is promoted, resolution
shall reject loopback, link-local, metadata, and disallowed private-network
addresses before and after DNS resolution; revalidate every redirect; prevent
DNS rebinding; forward credentials only across an explicitly allowed same-origin
redirect; require verified TLS; and require an explicit allowlist for private
network sources.

### 5.3 Parsing and canonicalization

**FG-PARSE-001 — CSV dialect.** Detect delimiter, quote, escape, header, newline, and encoding; record inferred values and allow explicit overrides.

**FG-PARSE-002 — JSON shapes.** Support top-level arrays of records and a configured record path in a JSON document. Reject ambiguous multi-record paths.

**FG-PARSE-003 — Canonical types.** Infer values into a limited type lattice: `null`, `boolean`, `integer`, `number`, `date`, `datetime`, `string`, `object`, `array`, `mixed`.

**FG-PARSE-004 — Conservative widening.** Type inference shall prefer `mixed`/review over lossy coercion. Leading-zero identifiers must not be silently converted to numbers.

**FG-PARSE-005 — Canonical field paths.** Produce stable field paths independent of presentation order.

**FG-PARSE-006 — Parse evidence.** Record invalid row count, bounded examples, and byte/row offsets where available.

### 5.4 Profiling and fingerprints

**FG-PROF-001 — Structural profile.** For each field record presence, inferred type set, null count/rate, uniqueness estimate, min/max length, and bounded examples after redaction.

**FG-PROF-002 — Value profile.** For eligible fields record enum candidates, numeric/date range, quantiles, cardinality, and normalized pattern signatures.

**FG-PROF-003 — Dataset profile.** Record row count, byte count, duplicate-key count, freshness observation, and configured control totals.

**FG-PROF-004 — Deterministic fingerprint.** Given identical bytes and configuration, structural and metric fingerprints shall be byte-identical across runs on the same product version.

**FG-PROF-005 — Sensitive-field treatment.** Fields marked sensitive shall never contribute literal values to reports or hosted summaries. Hashing must use a configured keyed digest when cross-run equality is required.

### 5.5 Baseline initialization

**FG-BASE-001 — Candidate inference.** `init` shall accept 1–5 observations and
generate a candidate schema and unresolved questions. One observation produces
a weak candidate; variability bands require at least two and remain proposals.

**FG-BASE-002 — No single-sample certainty.** A baseline inferred from one observation shall be visibly labelled weak and cannot infer variability bands.

**FG-BASE-003 — Contradiction surfacing.** Incompatible historical observations shall produce questions or variant candidates, not a silently widened baseline.

**FG-BASE-004 — Explicit promotion.** Candidate baseline promotion shall require `accept`, an actor identity, and optional rationale.

**FG-BASE-005 — Approval digest.** Promotion shall bind to the complete baseline, rule set, variant set, parser policy, and redaction policy digest.

### 5.6 Change detection

**FG-DIFF-001 — Structural changes.** Detect field add/remove, nested path change, order-only change where relevant, header duplication, and record-shape change.

**FG-DIFF-002 — Type changes.** Detect narrowing, widening, mixed-type emergence, representation change, and parse-failure increase.

**FG-DIFF-003 — Constraint changes.** Detect nullability, requiredness, uniqueness, key, enum, pattern, range, and control-total violations.

**FG-DIFF-004 — Dataset changes.** Detect row/byte volume deviation, duplicate changes, freshness failure, empty delivery, and partition/date discontinuity.

**FG-DIFF-005 — Distribution changes (conditional hypothesis).** After a paid
incident requires them, evaluate explicitly configured cardinality, quantile,
category-share, null-share, or pattern-share thresholds. Algorithms, minimum
sample sizes, and fixture oracles must be specified per promoted check; no
adaptive automatic re-baselining is permitted.

**FG-DIFF-006 — Rename candidates (conditional hypothesis).** A promoted rename
detector shall declare its deterministic similarity features, threshold, and
fixture oracle. Until those are specified, the system may display a heuristic
candidate but shall classify it `review_required` and shall not claim recall or
precision.

**FG-DIFF-007 — Affected records.** Where a rule is row-evaluable, record the exact affected-row count and bounded redacted examples. Reports must distinguish exact enumeration from sampled estimates.

**FG-DIFF-008 — Downstream assumptions.** Configuration may name consumers, fields, fixtures, and invariants. Findings shall list directly referenced assumptions; v0.1 does not crawl lineage.

### 5.7 Policy and classification

**FG-POL-001 — Typed severity.** Findings shall have `info`, `warning`, `error`, or `critical` severity.

**FG-POL-002 — Dispositions.** Every observation shall end in exactly one disposition:

| Disposition | Meaning | Default exit |
|---|---|---:|
| `unchanged` | Observation matches the accepted baseline with no material finding | 0 |
| `safe_additive` | Deterministic policy permits continuation | 0 |
| `known_variant` | Matches an explicitly accepted variant | 0 |
| `review_required` | Ambiguous or policy requires human decision | 2 |
| `breaking` | Deterministic hard rule violated | 3 |
| `invalid_observation` | Acquisition/parsing/evaluation incomplete | 4 |
| `internal_error` | Product failed to evaluate safely | 5 |

**FG-POL-003 — Precedence.** `internal_error`/`invalid_observation` and critical hard-rule failures shall not be masked by lower findings. The precedence algorithm must be deterministic and documented.

**FG-POL-004 — Safe additive.** Added fields are safe only when the policy explicitly permits additions and no row shape, parser, key, size, or consumer assumption is violated.

**FG-POL-005 — Fail-safe unknowns.** Unsupported rules, missing baseline components, and unavailable required evidence shall never yield a safe result.

**FG-POL-006 — Reason codes.** Every disposition shall include machine-readable reason codes and the findings that caused it.

### 5.8 Bounded model assistance

**FG-AI-001 — Optional.** Core operation shall work without a model or network.

**FG-AI-002 — Allowed tasks.** A model may suggest likely aliases, explain a finding, summarize a change packet, or propose deterministic fixture cases.

**FG-AI-003 — Forbidden authority.** A model may not create/promote a baseline, accept a variant, lower severity, suppress a hard-rule failure, or mark an observation safe.

**FG-AI-004 — Typed output.** Suggestions shall conform to a declared schema with field references, confidence, evidence references, and uncertainty.

**FG-AI-005 — Validation.** Suggested aliases shall be evaluated against deterministic type/value compatibility and affected-record checks before presentation.

**FG-AI-006 — Provenance.** Suggestion records shall include provider, model, parameters, prompt/template digest, input digest, output digest, latency, and cost where available.

**FG-AI-007 — Data boundary.** Remote model calls shall require explicit opt-in and use only the configured redacted projection. The envelope shall state what data class left the machine.

**FG-AI-008 — Egress authorization.** Remote AI shall fail closed unless an
accepted provider-enablement record binds provider, allowed tasks, allowed data
classes, redaction-policy digest, and actor. A configuration flag alone cannot
authorize egress, especially in CI. Model-authored prose is labelled
non-authoritative in every report.

### 5.9 Review and acceptance

**FG-REV-001 — Review object.** The review surface shall display observation, baseline, findings, evidence coverage, suggestions, and proposed decision-envelope digest.

**FG-REV-002 — Decisions.** A reviewer may:

- acknowledge without changing policy;
- reject the observation;
- accept a new baseline version;
- accept a scoped variant;
- record an upstream incident/escalation;
- defer while preserving `review_required`.

**FG-REV-003 — Actor.** Every decision shall include actor, timestamp, action, envelope digest, and optional rationale. CI/non-interactive acceptance shall require an explicit configured signer; anonymous acceptance is prohibited.

**FG-REV-004 — Scoped variant.** Accepting an alias or tolerance shall require scope, applicable fields/pattern, start point, and optional expiry/review date.

**FG-REV-005 — No mutation.** Acceptance appends a decision and a new version; it does not rewrite the prior baseline, observation, findings, or envelope.

**FG-REV-006 — Stale review.** If the baseline, policy, or observation changes after review starts, the previous approval shall not apply. Digest mismatch must fail visibly.

**FG-REV-007 — Authenticity grades.** v0.1 local decisions are **attributed,
digest-bound records**, not cryptographically signed or tamper-resistant. If
signed approval is promoted, a trusted-key policy shall bind reviewer identity
to a verified signature (local key or OIDC identity), reject unknown/revoked
keys, and hash-chain journal records. Reports must state the achieved grade.

### 5.10 Evidence and reports

**FG-REP-001 — Formats.** Week one/two shall produce canonical JSON and one
self-contained HTML incident packet. Markdown is conditional on demonstrated
GitHub-review use.

**FG-REP-002 — Reproduction.** Every report shall include product version, configuration digests, observation/baseline IDs, and exact command sufficient to reproduce where source access remains available.

**FG-REP-003 — Coverage.** Reports shall state whether evaluation was full, sampled, fingerprint-only, or missing required evidence.

**FG-REP-004 — Redaction.** The redacted report shall contain no literal sensitive values, credentials, signed URLs, authorization headers, or local absolute paths unless explicitly requested.

**FG-REP-005 — Partner packet.** A partner-facing mode shall omit internal rule implementation details while retaining changed fields, examples, expected contract, timestamps, digests, and reproduction guidance.

**FG-REP-006 — Stable JSON.** Canonical JSON keys and enums shall be versioned; backward-incompatible changes require a schema-version increment.

### 5.11 History and state reconstruction

**FG-HIST-001 — Append-only journal.** Observations, baseline proposals, findings,
decisions, and report manifests shall be append-only at the application API in
SQLite for v0.1. This is not a tamper-resistant audit log; the report shall not
claim otherwise.

**FG-HIST-002 — Content-addressed artefacts.** Raw observations retained locally, reports, and large evidence blocks shall be stored by digest with explicit retention policy.

**FG-HIST-003 — Rebuild.** Derived feed status, current baseline pointer, and report index shall be reconstructible from the journal and artefact store.

**FG-HIST-004 — Exclusive writer.** A workspace shall take an OS-level lock; a second writer shall refuse to open it.

**FG-HIST-005 — Export/delete.** The user shall be able to export a feed history and delete raw retained content while preserving a tombstone and declared evidence limitation. Immutability does not mean refusing privacy deletion.

**FG-HIST-006 — Replay grades.** Every envelope declares one grade:

- `exact_local_replay`: retained exact bytes plus pinned config/tool artefacts;
- `source_dependent_rerun`: source must still return the same digest;
- `fingerprint_verification`: retained fingerprints can verify identity/summary
  only and cannot reproduce parsing, row enumeration, or all findings.

`reproduce` and reports shall not claim a stronger grade than retained evidence
supports.

### 5.12 GitHub Action and CI

**FG-CI-001 — Action inputs.** Support config path, source override, report destination, upload-artifact flag, and policy mode.

**FG-CI-002 — Pull-request summary.** Emit a concise Markdown job summary and optional PR annotation without posting raw sensitive samples.

**FG-CI-003 — Scheduled checks.** Before hosted accepted-state storage exists,
scheduled GitHub checks are excluded because runners are ephemeral. After the
paid gate, scheduling may be enabled only against an authenticated hosted state
service or another separately specified integrity-checked persistent store.

**FG-CI-004 — Exit semantics.** Preserve the disposition exit codes in local and CI execution.

**FG-CI-005 — No hidden acceptance.** The Action shall never update a baseline or accepted variant unless a separately invoked acceptance command verifies the exact envelope digest and signer.

**FG-CI-006 — Artefact retention warning.** If reports are uploaded to GitHub, display and record that repository artefact retention and access controls apply.

**FG-CI-007 — Event trust policy.** Fork pull requests and other untrusted events
shall receive no source credentials, accepted-state signing authority, hosted
write token, or raw report upload. Only protected-branch/manual/scheduled events
matching repository policy may read authoritative state; only a protected
acceptance workflow may promote it. Untrusted PR configuration is evaluated as
a proposal and cannot produce an authoritative safe decision.

---

## 6. Configuration contract

### 6.1 Illustrative `feedguard.yaml`

```yaml
api_version: feedguard.sutra.dev/v1alpha1
kind: FeedGuard

feed:
  id: acme_daily_orders
  owner: integrations
  description: Daily order export supplied by Acme

source:
  kind: https
  uri: https://partner.example/orders.csv
  format: csv
  auth:
    bearer_from: env:ACME_FEED_TOKEN
  limits:
    max_bytes: 52428800
    timeout_seconds: 30

records:
  key: [order_id]
  csv:
    header: true
    encoding: utf-8

contract:
  import_json_schema: contracts/acme-orders.schema.json
  additions: review
  fields:
    order_id:
      required: true
      type: string
      pattern: '^ORD-[0-9]+$'
    amount:
      required: true
      type: number
      minimum: 0
    currency:
      required: true
      enum: [INR, USD]

checks:
  duplicate_key:
    severity: critical
  row_count:
    min: 1
    max_change_ratio: 0.50
    severity: error
  null_rate:
    amount:
      max: 0
      severity: critical
  freshness:
    field: exported_at
    max_age: 36h
    severity: error

variants:
  file: .feedguard/variants/acme_daily_orders.yaml

redaction:
  default: mask
  allow_fields: [currency]
  hash_fields: [order_id]
  drop_fields: [customer_email]

ai:
  enabled: false
  allowed_tasks: [alias_suggestion, explanation]

outputs:
  json: .feedguard/reports/latest.json
  markdown: .feedguard/reports/latest.md
  html: .feedguard/reports/latest.html
```

### 6.2 Policy language restrictions

v0.1 expressions may include:

- comparisons;
- set membership;
- boolean composition;
- field existence/type/null checks;
- string/number/date bounds;
- ratios and control totals;
- cross-field equality or arithmetic over the current record;
- dataset aggregates provided by the profiler.

They may not include network, filesystem, shell, SQL, Python, JavaScript, model calls, or non-deterministic functions. Time-sensitive checks receive an explicit `evaluation_time` recorded in the envelope.

---

## 7. CLI contract

```text
feedguard init <source...> --config feedguard.yaml
feedguard check [source] --config feedguard.yaml
feedguard diff <observation-or-source> --against <baseline>
feedguard review <envelope-id> [--html]
feedguard accept <envelope-id> --as observation|baseline|variant --actor <id>
feedguard reject <envelope-id> --actor <id>
feedguard report <envelope-id> --format json|md|html --redacted
feedguard history <feed-id>
feedguard reproduce <envelope-id>
feedguard doctor
feedguard version
```

### 7.1 Command semantics

- `init` proposes; it never accepts.
- `check` acquires, parses, profiles, diffs, evaluates, journals, and reports.
- `diff` does not journal external state unless requested; it is useful for preview.
- `review` opens a local HTML review surface or prints a terminal summary.
- `accept` verifies envelope plus parent accepted-state digest and applies the
  explicit state transition in §8.3.
- `reproduce` reports `exact_local_replay`, `source_dependent_rerun`, or
  `fingerprint_verification`; it never implies reconstruction from fingerprints.
- `doctor` validates workspace permissions, configuration, secrets references, parser support, model boundary, and GitHub Action environment without acquiring a feed.

### 7.2 Output discipline

- Human output goes to stderr; canonical JSON may go to stdout with `--json`.
- Secrets and raw sensitive values are redacted in both streams.
- Non-interactive mode must never prompt; it returns `review_required` with instructions.
- `--quiet` suppresses human summaries but not error diagnostics.

---

## 8. Decision model

### 8.1 Finding categories

| Category | Examples |
|---|---|
| Acquisition | unavailable source, content type, freshness metadata |
| Parse | malformed rows, encoding, duplicate headers, shape ambiguity |
| Structure | field add/remove/path/order, record container change |
| Type | widening, narrowing, representation, mixed emergence |
| Constraint | null, enum, key, pattern, range, uniqueness |
| Behaviour | row count, cardinality, distribution, category share |
| Control | totals, cross-field arithmetic, temporal continuity |
| Assumption | named consumer/fixture/invariant reference affected |
| Suggestion | alias, explanation, proposed fixture—not policy evidence |

### 8.2 Classification algorithm

1. If the product cannot safely acquire, parse, or evaluate required policy, disposition is `invalid_observation` or `internal_error`.
2. Evaluate all deterministic rules whose required evidence exists.
3. If any critical hard rule fails, disposition is `breaking`.
4. If any error rule configured to block fails, disposition is `breaking`.
5. If the observation exactly matches an accepted variant and no unrelated blocking rule fails, disposition is `known_variant`.
6. If any ambiguity, rename candidate, unsupported evidence, or human-gated rule remains, disposition is `review_required`.
7. If changes are additive and explicitly allowed, disposition is `safe_additive`.
8. If no material changes exist, return `unchanged`.

Model confidence never appears in this precedence chain.

### 8.3 Review state transitions

| Action | Current envelope | Authoritative state effect | Future checks |
|---|---|---|---|
| Acknowledge | Remains unchanged | Append acknowledgement only | No policy effect |
| Defer | `review_required` | Append deferral and optional owner/due date | Still non-zero until another decision |
| Reject observation | `breaking` or `review_required` | Mark observation rejected; baseline unchanged | Same change remains blocking |
| Accept observation only | Current observation becomes accepted exception | Append observation-scoped exception, never reusable | Future observations do not inherit it |
| Accept variant | Current envelope resolves to `known_variant` | Promote scoped variant under a new accepted-state digest | Matching future scope may exit 0 |
| Accept baseline | Current envelope resolves to `unchanged` against new baseline | Promote proposed baseline/rules/variants atomically and advance current pointer | Future checks compare with new state |
| Record incident | Disposition unchanged | Append escalation metadata | No policy effect |

Every transition verifies the current envelope and parent accepted-state digest.
There is no generic “accept” that silently chooses one of these effects.

### 8.4 Default policy posture

- removed field: breaking;
- required field missing: breaking;
- key/type incompatibility: breaking;
- empty delivery after non-empty history: breaking;
- new field: review required unless additions explicitly allowed;
- likely rename: review required;
- enum extension: review required unless accepted/allowed;
- format-only representation change: review required until normalized as a variant;
- order-only change: informational unless the parser/consumer declares order significant;
- statistical drift: warning/review by configured threshold, never automatic baseline movement.

---

## 9. Data and journal model

### 9.1 Principal records

| Record | Purpose |
|---|---|
| `FeedRegistered` | Stable logical feed identity |
| `ObservationAcquired` | Exact source digest and acquisition metadata |
| `ObservationProfiled` | Parser/canonicalizer and fingerprint results |
| `BaselineProposed` | Candidate baseline with source observations |
| `BaselineAccepted` | Human-attributed immutable promotion |
| `ChangeDetected` | Typed finding set and evidence refs |
| `SuggestionProduced` | Non-authoritative bounded AI/deterministic suggestion |
| `DecisionEnvelopeCreated` | Immutable review object |
| `ObservationAccepted` | Human decision for the observation |
| `VariantAccepted` | Scoped normalization/tolerance decision |
| `ObservationRejected` | Human rejection |
| `IncidentRecorded` | Partner/internal escalation metadata |
| `RawContentDeleted` | Privacy deletion tombstone and evidence limitation |

### 9.2 Identifiers and digests

- IDs: UUIDv7 or another lexically sortable, collision-resistant scheme.
- Content digests: `sha256:<hex>`.
- Envelope digest: deterministic canonical JSON with explicit schema version.
- Causality: every derived record references its input record IDs and digests.
- Journal sequence is local ordering metadata, not a globally meaningful identity.

### 9.3 Storage layout

```text
.feedguard/
├── feedguard.db
├── workspace.lock
├── objects/sha256/<prefix>/<digest>
├── baselines/<feed-id>/
├── variants/<feed-id>.yaml
└── reports/<feed-id>/<envelope-id>/
```

SQLite is authoritative for the journal. `baselines/`, `variants/`, and report indices are projections/export surfaces and must be rebuildable. Large retained objects are content addressed.

---

## 10. Architecture and module boundaries

The validation implementation should be a small uv-managed Python project unless benchmark evidence requires another language. Python is chosen for parser/data tooling and speed of validation, not as a permanent Sutra architecture decision.

```text
CLI / GitHub Action
       │
       ▼
Application service
  acquire → parse → profile → diff → evaluate → envelope
       │          │        │        │
       │          │        │        └─ deterministic policy engine
       │          │        └─ typed change detector
       │          └─ bounded canonical profiles
       └─ local/HTTPS source adapters
       │
       ├─ optional suggestion port (local or remote model)
       ├─ append-only SQLite journal
       ├─ content-addressed local artefacts
       └─ JSON/Markdown/HTML projections
```

### 10.1 Modules

| Module | Owns | Must not |
|---|---|---|
| `domain` | Types, dispositions, findings, events, invariants | Perform I/O |
| `acquisition` | Local/HTTPS bytes and source metadata | Interpret business policy |
| `parsing` | CSV/JSON canonical records and parse evidence | Accept lossy coercion silently |
| `profiling` | Structural/value/dataset fingerprints | Decide disposition |
| `contracts` | JSON Schema/ODCS mapping and typed rules | Execute arbitrary user code |
| `diffing` | Deterministic change sets | Call a model |
| `policy` | Rule evaluation and classification | Mutate baseline/history |
| `suggestions` | Optional alias/explanation/fixture proposals | Decide or accept |
| `review` | Decision commands and digest verification | Rewrite prior records |
| `journal` | Atomic append/read and migrations | Become a second policy engine |
| `objects` | Content-addressed storage and deletion | Expose raw objects in reports by default |
| `reports` | JSON/Markdown/HTML projections | Serve facts absent from journal/objects |
| `cli` | Arguments, streams, exit codes | Contain domain logic |

### 10.2 Dependency rule

Domain types and pure decision functions sit at the centre. I/O adapters call them. No domain function reads the filesystem, network, clock, environment, database, or model. Clock and evaluation time are explicit inputs.

### 10.3 Relation to AHE

v0.1 does not force this narrow deterministic workflow through the general AHE architecture. If model suggestions and approvals later require durable multi-step orchestration, extraction shall preserve:

- the Workflow Definition IR as canonical;
- the Runtime-calls-Kernel direction;
- append-only journal semantics;
- command/outcome separation;
- immutable approval envelopes.

Until then, introducing a general agent runtime is scope failure.

---

## 11. Privacy and security

### 11.1 Threat model

Protect against:

- accidental sensitive values in reports, CI logs, prompts, or hosted telemetry;
- malicious or malformed feed content;
- decompression/size/resource exhaustion;
- CSV formula injection in exported reports;
- credential leakage through configuration or reproduction commands;
- remote model exfiltration;
- tampering with baseline, variant, or decision records;
- stale approval applied to changed content;
- unsafe HTML report rendering.

### 11.2 Requirements

**FG-SEC-001 — Local first.** All mandatory evaluation runs locally. Network is required only for an HTTPS source explicitly configured by the user.

**FG-SEC-002 — Secret references.** Reports and journals store the reference name, never resolved secret material.

**FG-SEC-003 — Redaction before egress.** Redaction occurs before model calls, hosted submission, CI annotation, or partner-report generation.

**FG-SEC-004 — Formula neutralization.** Spreadsheet-compatible outputs shall neutralize cells beginning with `=`, `+`, `-`, or `@` where they could execute as formulas.

**FG-SEC-005 — Bounded parser.** Acquisition and parsing enforce byte, row, nesting, field-count, decompression, and execution-time ceilings.

**FG-SEC-006 — HTML safety.** Reports escape all source-controlled content and carry a restrictive Content Security Policy with no remote scripts.

**FG-SEC-007 — File permissions.** Workspace and raw-object permissions default to owner-only where supported.

**FG-SEC-008 — Digest verification.** `accept`, `reject`, and report sharing verify the referenced envelope exists and matches its digest.

**FG-SEC-009 — No training.** Customer content shall not be used for model training. Remote-provider data terms remain the customer's explicit choice and must be shown before enabling the provider.

**FG-SEC-010 — Telemetry.** v0.1 telemetry is opt-in and contains product events and coarse counts only; no feed names, paths, URLs, field names, values, digests, or reports.

### 11.3 Data retention

Default local retention:

- baseline and decision metadata: retained until user deletion;
- raw acquired bytes: off unless explicitly enabled, or retained only for the current run;
- redacted evidence: retained with decision history;
- reports: user-configurable;
- hosted v0.1: no raw bytes; 30-day result retention if the conditional service is built.

Reports must declare what was retained, deleted, or unavailable.

---

## 12. Non-functional requirements

### 12.1 Performance targets

These are conditional engineering targets, not week-one/two acceptance gates.
Before enforcement, check in the benchmark corpus, record CPU architecture,
logical cores, RAM, filesystem, Python/product version, cold/warm-cache posture,
and define elapsed time from post-acquisition bytes-ready to envelope creation.
Network time and upstream failures are reported separately. Initial target
machine class: Apple Silicon M-series or x86-64 equivalent, 8 logical cores and
16 GB RAM.

- startup to help: under 500 ms warm, under 1.5 s cold;
- 100 MB CSV full structural scan: under 60 s;
- 1 million-row CSV with configured key checks: under 120 s or emit a clear resource-limit result;
- peak memory: under 512 MB for 100 MB streaming-compatible input;
- unchanged fingerprint comparison after acquisition: under 5 s excluding download;
- HTML report generation: under 5 s for 10,000 findings using bounded grouping rather than rendering every row.

These are validation targets, not published guarantees until benchmarked.

### 12.2 Reliability

- Atomic journal append for one evaluation phase.
- Crash before envelope creation leaves a reconstructible incomplete run, never a safe result.
- Re-running identical input/config creates semantically identical findings; duplicate storage may be deduplicated by digest.
- A report generation failure does not erase the canonical envelope.
- Corrupt object or journal verification returns `internal_error` and never falls back to an older silent baseline.

### 12.3 Portability

- Python 3.12.
- macOS and Linux in v0.1.
- GitHub-hosted Ubuntu runners.
- Windows support after the validation sprint unless demanded by a paying pilot.
- No Docker requirement for local use.

### 12.4 Usability

- First-check time starts when a qualified user receives installation
  instructions and ends at the first canonical envelope; founder intervention
  and failures are recorded, never excluded silently. Target: under 15 minutes.
- Candidate-baseline setup starts at successful first parse and ends at an
  accepted-state digest for a feed with the week-one rule surface. Target: under
  30 minutes.
- Every blocking result names the next safe action.
- Terminology distinguishes observed fact, heuristic candidate, model suggestion, policy verdict, and human decision.

### 12.5 Observability

Local structured logs shall include correlation IDs and phases but not sensitive fields. `--debug` may increase technical detail without disabling redaction. The report exposes phase durations and coverage.

---

## 13. Reports and review experience

### 13.1 HTML structure

1. **Decision:** disposition, reasons, evidence coverage, observation/baseline IDs.
2. **What changed:** grouped material findings.
3. **Why it matters:** violated rules and named assumptions.
4. **Affected records:** exact count or clearly labelled estimate, redacted examples.
5. **Suggested correspondences:** non-authoritative alias/explanation candidates.
6. **Review actions:** commands for accept/reject/variant; no mutation from a static HTML file in v0.1.
7. **Reproduce:** exact sanitized command and pinned versions.
8. **Evidence manifest:** digests, parser/config/model versions, retention/redaction posture.

### 13.2 Noise controls

- group repeated row findings by rule and field;
- show bounded examples and downloadable machine-readable details;
- separate informational from blocking findings;
- suppress a known variant only by matching its explicit scope;
- never hide a new critical finding because the same field had an older accepted warning.

---

## 14. Test and enforcement specification

A subsystem is not complete until an executable test enforces it.

1. **Golden determinism:** define a canonical deterministic payload containing
   accepted input/config/object digests, canonical profile, findings,
   disposition, and evidence refs. Identical bytes, accepted state, explicit
   evaluation time, sampling seed, and product version produce byte-identical
   canonical payloads. Acquisition timestamps, phase durations, local paths,
   actor timestamps, model latency/cost, and transport metadata live outside it.
2. **Baseline immutability:** accepting a new baseline leaves prior bytes and digest unchanged.
3. **Stale approval rejection:** alter observation or policy after review; `accept` must refuse the old digest.
4. **Model non-authority:** replace the suggestion provider with malicious `safe` output; disposition remains determined by policy.
5. **Parse fail-safe:** truncated CSV/JSON cannot return `safe_additive` or `known_variant`.
6. **Semantic trap fixtures:** renamed field with incompatible units/meaning remains review/breaking despite name similarity.
7. **Known-variant scope:** accepted alias applies only to its feed/field/type scope and does not suppress an unrelated violation.
8. **Affected-record correctness:** seeded fixtures assert exact row enumeration and bounded report examples.
9. **Redaction conformance:** planted secrets/PII do not appear in stdout, stderr, DB text columns, reports, CI summary, suggestion prompt, or hosted payload.
10. **Formula injection:** malicious CSV cells render as inert text in every export/report.
11. **Resource ceilings:** oversized/deep/malformed payloads terminate safely under declared limits.
12. **Empty-projection rebuild:** delete baseline/report projections and rebuild them from journal and content-addressed artefacts with equality.
13. **Workspace lock:** a second writer refuses the same workspace.
14. **Exit-code contract:** each disposition maps to the documented code in local and GitHub Action runs.
15. **No production-write dependency:** dependency/static analysis rejects database/warehouse/SFTP/Kafka publishing adapters in the v0.1 core package.
16. **Offline conformance:** local-file evaluation with AI disabled completes with network unavailable.
17. **Schema interoperability:** JSON Schema round-trip preserves supported constraints and reports unsupported ones.
18. **Crash recovery:** crash after profile and before envelope; restart records incomplete state and produces one final envelope without duplicate acceptance.
19. **Report truthfulness:** sampled evaluation is labelled sampled; deleted raw data is labelled unavailable.
20. **Historical incident replay:** at least ten incident fixtures, with eight detected and zero silent critical misses before paid pilot release.

### 14.1 Test fixture matrix

| Fixture | Expected result |
|---|---|
| Identical reordered CSV rows | unchanged/safe if row order not significant |
| Added optional field | safe or review according to additions policy |
| Removed required field | breaking |
| Numeric ID gains leading zeros | review/breaking, never silent numeric coercion |
| Amount changes from rupees to paise | semantic trap; review/breaking |
| Date changes ISO to locale-ambiguous | review required |
| New enum value | review unless explicitly allowed |
| Empty file with headers | breaking by default |
| Duplicate primary key | breaking |
| Row-count seasonal spike within accepted band | known variant |
| Same alias accepted for another feed only | no match; review required |
| Malformed final row | invalid observation or breaking by configured parse policy |

---

## 15. Packaging and repository shape

If implementation begins, create a separate build repository rather than mixing validation code into this specification repository:

```text
pyproject.toml
uv.lock
.python-version
README.md
DEMO.md
src/feedguard/
  domain/
  acquisition/
  parsing/
  profiling/
  contracts/
  diffing/
  policy/
  suggestions/
  review/
  journal/
  reports/
  cli.py
tests/
fixtures/
evals/
scripts/
  scenario_safe_additive.py
  scenario_breaking_change.py
  scenario_known_variant.py
  scenario_semantic_trap.py
  scenario_redacted_incident_packet.py
action.yml
```

The README and demo must show what the artifact proves and does not prove. Every scenario shall print `PASS`/`FAIL` and exit non-zero on failure.

---

## 16. Four-week delivery and validation plan

### Week 1 — incident corpus and deterministic slice

Research:

- build 100-account/prospect list;
- obtain five old/new artifact bundles;
- conduct eight last-incident interviews;
- verify six of eight saw repeated incidents and median remediation exceeded two engineer-hours.

Build only enough to replay one incident end to end:

- local CSV/JSON acquisition;
- parser/canonical profile;
- baseline proposal/acceptance;
- structural/type/key/null/enum checks;
- canonical JSON and HTML envelope;
- append-only SQLite journal.

Gate: five representative bundles. Otherwise stop product development and repair recruitment/access.

### Week 2 — historical replay and payment

- replay ten historical changes from at least five teams;
- add variants, affected-record enumeration, redaction, and partner packet;
- measure detection, false blocks, setup time, and operator actionability;
- collect payment for a $99 shadow pilot beginning immediately; the full 30-day
  retention window may extend beyond the four-week build sprint.

Gate:

- at least 8/10 known incidents detected;
- zero silent critical misses;
- median setup under 30 minutes;
- no more than one false blocking alert per 20 runs;
- at least three collected, non-refundable pilot payments (or signed paid
  purchase orders with a defined start date).

No collected payment or defined paid equivalent means no hosted build.

### Week 3 — installable shadow product

- package CLI;
- add GitHub Action;
- optional suggestion port;
- install for paid teams without production writes;
- add only the minimal result endpoint if paid evidence requires scheduling/history.

Gate:

- three teams install without founder code changes;
- time to first use under 15 minutes;
- at least two real or seeded changes correctly triaged;
- no customer-specific engine fork.

### Week 4 — retention and decision

- compare against each team's existing script/library on the same incidents;
- ask pilots to convert to $39 or $149 recurring plans;
- require a second reviewer where available;
- measure repeat checks, decisions, evidence sharing, and configuration reuse.

Build gate at day 28:

- three paying teams;
- at least two customers prepay or sign an explicitly priced continuation after
  the pilot; this is a forward commitment, not yet evidence of retained use;
- at least 70% successful eligible checks, where the denominator excludes only
  independently verified upstream unavailability and includes product/config
  failures;
- at least two multi-user decision events;
- at least two customers name evidence/acceptance history—not AI—as a purchase reason;
- at least one credible Sutra vertical design-partner conversation.

Retention gate at day 60:

- at least two pilots remain paid after the 30-day period;
- each retained team has completed a second real or seeded decision cycle;
- accepted-state history, rather than one-off incident forensics alone, is used
  in at least one renewal.

Pivot gate:

- incidents are real but users pay only for contract generation: release scaffolding as free acquisition and retest monitoring;
- demand clusters around NBFC co-lending files: preserve the engine and implement a separate validated vertical policy pack;
- users value one-off forensic reports but not monitoring: test a service product before more software.

Kill gate:

- fewer than five artifacts after 30 qualified outreaches and ten calls;
- zero paid pilots;
- setup remains above 60 minutes;
- existing GX/Soda/Airbyte/scripts win without meaningful coordination/evidence pain;
- every third feed requires bespoke engine code;
- no repeat usage after the incident replay.

---

## 17. Product analytics for the experiment

Collect only consented, non-sensitive operational metrics:

- time to first baseline;
- observations per feed/week;
- change incidence and disposition mix;
- rules and variants per feed;
- setup/configuration minutes;
- false blocking alerts;
- critical misses discovered by operator;
- review latency;
- reviewer count;
- evidence packet generated/shared;
- repeat use and feed retention;
- custom implementation hours;
- paid conversion and plan;
- stated incumbent/workaround;
- raw-data posture: local only, redacted egress, or explicit sample upload.

The decisive questions are:

1. Is the retained job detection, or proof and coordination?
2. Will teams install before an incident, or only immediately after one?
3. Does accepted-variant history recur enough to retain customers?
4. Can at least 80% of feed configuration use the standard rule surface?
5. Is local-first operation a purchase enabler or merely expected?
6. Does the utility create access to the regulated partner-data market Sutra ultimately targets?

---

## 18. Commercial hypothesis

These prices are experiments, not commitments:

| Plan | Hypothesis | Scope |
|---|---:|---|
| Local | Free | Unlimited local checks, JSON/HTML, public repositories |
| Shadow pilot | $99/30 days | Assisted setup, up to five feeds, explicit feedback agreement |
| Solo | $39/month | Five hosted schedules, 30-day result history, email/GitHub |
| Team | $149/month | 25 feeds, 180-day evidence, Slack, five reviewers |
| Scale | $399/month | 100 feeds, one-year evidence, private runner, support |

The value metric is monitored feeds, schedule frequency, retention, and review collaboration—not row count. Raw compute volume may later require abuse ceilings, but it should not obscure the recurring operational job during validation.

---

## 19. Risks and responses

| Risk | Consequence | Response / evidence gate |
|---|---|---|
| Existing validators are sufficient | No willingness to pay | Historical bake-off must show workflow/evidence advantage |
| Airbyte/dbt/observability vendor bundles it | Weak independent category | Stay at unowned pre-ingestion boundary; validate cross-tool demand |
| Tool is installed only after incidents | Weak recurring retention | Measure scheduled checks and second incident/use |
| Every source needs code | Services trap | Standard policy coverage ≥80%; kill on repeated engine forks |
| Noise causes disablement | Product loses trust | False blocking alert ≤1/20 runs |
| Statistical checks imply false certainty | Silent semantic corruption | Thresholds explicit; no adaptive re-baselining; semantic traps |
| AI suggestion perceived as authority | Unsafe acceptance | Hard separation and executable non-authority tests |
| Sensitive data leaks through reports | Adoption blocker/liability | Local-first, redaction conformance, no raw hosted payload |
| Evidence history alone is not valuable | Weak differentiation | Customers must name it as purchase reason |
| Architecture expands before demand | Delayed learning | Four-week boundary; no full AHE/Control Plane |

---

## 20. Open questions requiring evidence

1. Does the initial ICP prefer GitHub-native monitoring, a local scheduled daemon, or CI-independent hosting?
2. Are CSV and JSON enough for the first paying cohort, or is Excel unavoidable?
3. Is source-specific variant history more valuable than incident packet generation?
4. Which distribution metrics produce signal without privacy leakage?
5. Do users permit retaining raw source bytes locally, or require fingerprint-only history?
6. What signer is sufficient for acceptance in small teams: Git identity, local key, or OIDC identity?
7. Does ODCS interoperability reduce setup or add vocabulary burden for the initial ICP?
8. Can distribution drift be useful without creating alert fatigue?
9. Which downstream assumptions can be declared manually before lineage integration is needed?
10. When does a vertical pack, especially NBFC co-lending preflight, become a separate policy package rather than product-specific code?
11. Does a hosted scheduler improve willingness to pay, or does local/private operation remain the dominant requirement?
12. What evidence packet has actually shortened partner remediation in a real incident?

Open questions remain outside committed scope until customer behaviour answers them.

---

## 21. Acceptance criteria for specification completion

This specification is complete enough to begin validation implementation when:

- every v0.1 surface has an explicit inclusion/exclusion boundary;
- dispositions and exit codes are stable;
- baseline, variant, finding, envelope, and decision semantics are unambiguous;
- model authority is explicitly bounded and executable tests enforce it;
- local data, redaction, retention, and hosted boundaries are declared;
- the first vertical slice and four-week gates are measurable;
- no requirement depends on the full Sutra/AHE platform;
- implementation can proceed through test-driven vertical slices with self-checking demos.

It is **not** evidence that the market opportunity is proven. Only paid use and repeated external behaviour can promote the product beyond this validation specification.

---

## 22. Source documents

- `../CONCEPT_REFINEMENT.md` — accepted Sutra product hierarchy, wedge, architecture direction, and validation constraints.
- `../MARKET_ASSESSMENT.md` — conditional-go market assessment and commercial gates.
- `../Common/research/sutra-adjacent-product-assessment.md` — product-option research, competitors, pricing hypotheses, and four-week experiment.
- `../AHE/design-notes/authoring-model.md` — deterministic business process with bounded uncertainty ports.
- `../AHE/adr/AHE-ADR-021-workflow-authoring-and-the-plan-lifecycle.md` — accepted authoring and approval semantics.
- `specification.md` — broader Sutra specification; this narrow validation specification supersedes it only for External Feed Change Guard scope.

When this document conflicts with an accepted ADR on shared architecture semantics, the ADR wins. When the broader Sutra specification implies capabilities explicitly deferred here, this document governs the validation build.

## 23. External research basis

- https://docs.getdbt.com/docs/mesh/govern/model-contracts
- https://cli.datacontract.com
- https://docs.datacontract.com/scheduling/github-actions
- https://docs.greatexpectations.io/docs/reference/learn/gx_in_your_data_pipeline/ingestion
- https://docs.soda.io/soda-documentation/soda-v3/data-source-reference/connect-file
- https://framework.frictionlessdata.io/docs/guides/validating-data.html
- https://docs.airbyte.com/platform/using-airbyte/schema-change-management
- https://www.datafold.com/data-diff
- https://bump.sh/pricing
- https://csvbox.io

These sources validate adjacent tooling, workflow patterns, and competition. They do not prove willingness to pay for this product; the four-week gates exist to obtain that evidence.
