# Scaffold source schema

The bundled generator loads every Python file below `.specs/source/` that does not start with `__`. Each file exports exactly one `PAGE` dictionary. Split files by independently understandable page; do not combine the complete product into one source module.

## Contents

- [Page object](#page-object)
- [Sections](#sections)
- [Inline links](#inline-links)
- [Blocks](#blocks)
- [Contract registry](#contract-registry)
- [Requirement and decision registers](#requirement-and-decision-registers)
- [Finalization](#finalization)

## Page object

```python
PAGE = {
    "route": "architecture/uploads/direct-upload.html",
    "nav_group": "Architecture flows",
    "nav_order": 120,
    "title": "Upload intent, direct transfer, completion, and scanning",
    "summary": "One sentence defining authority, scope, and terminal outcome.",
    "kind": "architecture-flow",
    "sections": [...],
    "related": ["product/journeys/content-authoring.html"],
    "contracts": [...],
    "requirements": [...],
    "decisions": [...],
}
```

Allowed page kinds:

- `overview`
- `product-journey`
- `feature`
- `architecture-flow`
- `runtime-module`
- `client-runtime`
- `reference`
- `decision-register`
- `coverage`

Use a route made of lowercase kebab-case segments ending in `.html`. Use a concrete title that predicts the page content. `nav_group` must appear in `.specs/_config.py::NAV_GROUP_ORDER`.

## Sections

```python
{
    "id": "chronological-sequence",
    "title": "Chronological sequence",
    "blocks": [...],
}
```

Use stable lowercase kebab-case ids. Once plans or implementation cite an anchor, preserve it unless its meaning is intentionally retired and compatibility is handled.

The validator enforces required section ids for focused page kinds. Read `.specs/_validate.py::REQUIRED_SECTIONS` before authoring each page.

## Inline links

Use root-relative specification routes inside this source syntax:

```text
[[Readable label|architecture/uploads/direct-upload.html#failure-reconciliation]]
```

The renderer computes the correct relative URL for nested generated pages and escapes all other text. Do not insert raw HTML.

## Blocks

### Paragraph and callout

```python
{"type": "paragraph", "text": "Normative text with a [[contract link|reference/api.html#op-create]]."}

{
    "type": "callout",
    "tone": "note",  # note | warning | danger | success
    "title": "Transaction boundary",
    "text": "External I/O starts only after the durable commit.",
}
```

### Lists and chronological sequences

```python
{"type": "list", "items": ["One exact rule", "Another exact rule"]}
{"type": "ordered", "items": ["First action", "Second action"]}
{
    "type": "sequence",
    "items": [
        {"title": "Validate authority", "text": "Name the exact policy owner and denial."},
        {"title": "Commit state", "text": "Name records, constraints, audit/outbox, and commit."},
    ],
}
```

### Tables

```python
{
    "type": "table",
    "id": "operation-create-upload",
    "caption": "Exact public operation contract",
    "headers": ["Operation", "Input", "Success", "Failures"],
    "rows": [["CreateUpload", "CreateUploadInput", "UploadIntentDTO", "AUTH_DENIED; INVALID_FILE"]],
}
```

Each row must match the header width and be independently interpretable.

### Code-format schemas

```python
{
    "type": "code",
    "id": "schema-upload-record",
    "label": "UploadRecord persistence contract",
    "language": "python",
    "contract_kind": "data-schema",
    "contract_id": "DATA-UPLOAD-RECORD-V1",
    "code": "UploadRecord(\n    id: UUID primary_key,\n    ...\n)",
}
```

Use `data-schema`, `input-schema`, `output-schema`, `event-schema`, `job-schema`, or `provider-schema`. Set `sealed: True` for every public payload schema. Replace the illustrative ellipsis above with exact fields in real sources; final validation rejects ellipses and placeholders.

### Cards

Use cards only for compact maps, not for every paragraph:

```python
{
    "type": "cards",
    "items": [{"kicker": "Actor", "title": "Workspace admin", "text": "Exact responsibility."}],
}
```

### Developer code flows

```python
{
    "type": "developer-flow",
    "flow": {
        "id": "code-flow-upload-completion",
        "title": "Complete an upload and schedule malware scanning",
        "trigger": "POST /uploads/{id}/complete by an authorized uploader",
        "authority": "UploadPolicy.complete from current workspace membership",
        "entry_point": "uploads.api.complete_upload -> CompleteUploadInput",
        "steps": [
            {"title": "Load and lock", "text": "uploads.commands.complete loads UploadRecord and locks id in one transaction."},
            {"title": "Commit intent", "text": "It verifies checksum/size, sets status=uploaded, writes AuditEntry and OutboxEvent, then commits."},
            {"title": "Run consumer", "text": "After commit UploadCompleted.v1 dispatches scan_upload; the worker records the terminal scan state."},
        ],
        "data_effects": "Reads and locks UploadRecord; updates status/checksum; creates AuditEntry and OutboxEvent.",
        "transaction": "One transaction; UploadRecord lock precedes audit/outbox writes; provider I/O occurs after commit.",
        "handoff": "UploadCompleted.v1 -> uploads.workers.scan_upload -> MalwareScanner adapter.",
        "terminal": "202 with uploaded state; later clean, rejected, or scan_failed terminal processing state.",
        "recovery": "Duplicate completion returns the existing outcome; retries deduplicate by upload id/version; operator reconciliation handles exhausted scans.",
    },
}
```

Add exactly one matching contract entry whose `kind` is `developer-flow`, `id` equals the flow id, and `anchor` equals the flow id.

## Contract registry

Each page registers the stable contracts it owns:

```python
"contracts": [
    {"kind": "developer-flow", "id": "code-flow-upload-completion", "anchor": "code-flow-upload-completion", "refs": ["EVENT-UPLOAD-COMPLETED-V1"]},
    {"kind": "api-operation", "id": "API-COMPLETE-UPLOAD-V1", "anchor": "operation-complete-upload", "refs": ["INPUT-COMPLETE-UPLOAD-V1", "DTO-UPLOAD-INTENT-V1"]},
]
```

Contract kinds are listed in `.specs/_validate.py::CONTRACT_KINDS`. Ids are globally unique. `api-operation`, `event`, `job`, and `provider` entries must reference their sealed schema contracts; every reference must resolve.

## Requirement and decision registers

Keep all requirement entries on the single `coverage` page and all decision entries on the single `decision-register` page. Their destinations point to focused normative owners; do not copy register entries into those focused pages.

```python
"requirements": [
    {
        "id": "REQ-UPLOAD-001",
        "source": "Owner PRD section 4.2",
        "text": "Authorized uploaders can complete a verified direct upload.",
        "status": "confirmed",  # confirmed | pending | superseded | excluded
        "destinations": ["architecture/uploads/direct-upload.html#chronological-sequence"],
    },
],
"decisions": [
    {
        "id": "DEC-UPLOAD-001",
        "question": "What is the terminal response before scanning completes?",
        "status": "confirmed",
        "choice": "Return 202 with uploaded state and process scanning asynchronously.",
        "rationale": "Scanning latency must not hold the request open.",
        "confirmation": "Owner architecture review",
        "consequences": "Consumers must handle later clean, rejected, or scan_failed states.",
        "destinations": ["architecture/uploads/direct-upload.html#failure-reconciliation"],
    },
],
```

Render the full question, choice, rationale, confirmation context, consequences, and affected contracts on the decision-register page. Final mode rejects pending entries.

## Finalization

Keep `.specs/_config.py::SPEC_STATUS` as `draft` and `SCAFFOLD_CONTENT_REPLACED` as `False` during discovery. Set them to `final` and `True` only after all source pages are project-specific, requirements/decisions/contracts are traceable, focused page requirements pass, and the semantic evaluation has no hidden assumption.
