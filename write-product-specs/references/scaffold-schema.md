# Scaffold source schema

The bundled generator loads every Python file below `.specs/source/` that does not start with `__`. Each file exports exactly one `PAGE` dictionary. Split files by independently understandable page; do not combine the complete product into one source module. The starter tree deliberately renders the full Stride documentation hierarchy in draft mode. Replace or remove every `starter=True` page before finalization.

## Contents

- [Page object](#page-object)
- [Source-backed inventory](#source-backed-inventory)
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
    "nav_group": "Architecture",
    "nav_subgroup": "Platform system designs",
    "nav_parent": "Uploads and storage",       # optional deeper owner
    "nav_category": "Runtime flows",           # optional leaf caption
    "nav_order": 120,
    "nav_label": "Upload intent through scanning",
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

Use a route made of lowercase kebab-case segments ending in `.html`. Use a concrete title that predicts the page content. `nav_group` must be one of `Start here`, `Product journeys`, `Product guides`, `Architecture`, or `Project reference`. Use `nav_subgroup`, `nav_parent`, and `nav_category` to reproduce the Stride sidebar hierarchy; do not create another navigation system. `nav_label` is the concise sidebar title and must remain as specific as the `h1`.

## Source-backed inventory

Populate `.specs/_inventory.py` before replacing draft status. Each entry is source-owned coverage evidence, not a navigation convenience.

```python
RUNTIME_DISCOVERY_ROOTS = [
    {
        "path": "backend/apps",
        "mode": "child-directories",
        "include_extensions": [".py"],
    },
    {
        "path": "backend/config",
        "mode": "root",
        "include_extensions": [".py"],
    },
]

RUNTIME_DISCOVERY_EXCLUSIONS = [
    {
        "path": "backend/apps/test_support",
        "reason": "Test-only factories contain no deployed runtime boundary.",
    },
]

RUNTIME_MODULE_INVENTORY = [
    {
        "id": "MOD-UPLOADS",
        "title": "Uploads and storage",
        "route": "architecture/backend/modules/uploads.html",
        "role": "implementation",
        "source_unit": "backend/apps/uploads",
        "owned_paths": ["backend/apps/uploads"],
        "public_boundary": "uploads.services and uploads.selectors",
        "entry_flows": ["code-flow-create-upload", "code-flow-complete-upload", "code-flow-scan-upload"],
        "scenario_ids": ["SCN-UPLOAD-001", "SCN-UPLOAD-002"],
    },
]
```

Supported discovery modes are `child-directories`, `child-files`, and `root`. Extensions identify deployed source instead of documentation, generated caches, or empty directories. `root` covers direct source files only. When that same directory has source-bearing child directories, add a `child-directories` entry for the same path or use narrower roots; an unpaired broad root fails validation. Configure multiple roots when natural units live at different depths. Every discovered unit that is not explicitly excluded must appear exactly once as a runtime module `source_unit`, that path must also appear in `owned_paths`, and its inventory entry must use a page route that no other inventory entry uses. Exclusion reasons must explain why the path is not a deployed runtime boundary; page-count reduction is never valid.

Runtime entries use role `settings`, `common`, or `implementation`. In final mode the validator requires exactly one settings owner and one common owner in that order unless `RUNTIME_SETTINGS_NOT_APPLICABLE_REASON` or `RUNTIME_COMMON_NOT_APPLICABLE_REASON` identifies where the responsibility lives in a concrete explanation of at least twenty characters. The validator also requires reciprocal coverage for product journeys, features, architecture flows, runtime modules, and client surfaces.

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
    "owner": "uploads domain and UploadRecord repository",
    "lifecycle": "created -> uploaded -> scanning -> clean|rejected|scan_failed; retained 30 days after deletion request",
    "concurrency": "expected version and row lock by id; upload lock precedes scan-attempt lock",
    "code": "UploadRecord(\n    id: UUID primary_key,\n    ...\n)",
}
```

Use `data-schema`, `input-schema`, `output-schema`, `event-schema`, `job-schema`, or `provider-schema`. Set `sealed: True` for every public payload schema. Replace the illustrative ellipsis above with exact fields in real sources; final validation rejects ellipses and placeholders.

Every code schema requires an exact `owner`. Data schemas additionally require `lifecycle` and `concurrency`. Sealed public schemas additionally require `version`, `unknown_fields`, and `unknown_values`; set unknown behavior explicitly rather than relying on framework defaults.

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
        "initiator": "Current workspace member holding upload.complete",
        "authority": "UploadPolicy.complete from current workspace membership",
        "entry_point": "uploads.api.complete_upload -> CompleteUploadInput",
        "steps": [
            {"title": "Validate transport", "symbols": ["uploads.api.complete_upload", "CompleteUploadInput.validate"], "reads": ["request.path.id", "request.body"], "writes": ["none: validation only"], "behavior": "Reject unknown keys and invalid checksum/size with stable field errors."},
            {"title": "Load and lock", "symbols": ["uploads.commands.complete_upload"], "reads": ["UploadRecord FOR UPDATE", "WorkspaceGrant"], "writes": ["none before all guards pass"], "behavior": "Recheck scope, legal state, object metadata, version, and idempotency identity."},
            {"title": "Commit intent", "symbols": ["uploads.commands.complete_upload"], "reads": ["UploadRecord"], "writes": ["UploadRecord.status", "AuditEntry", "OutboxEvent"], "behavior": "Persist uploaded state, audit, and UploadCompleted.v1 atomically, then commit."},
            {"title": "Run consumer", "symbols": ["uploads.workers.scan_upload", "MalwareScanner.scan"], "reads": ["UploadRecord", "blob metadata"], "writes": ["ScanAttempt", "UploadRecord.scan_status"], "behavior": "Dispatch after commit, perform provider I/O without a row lock, and record a normalized terminal scan state."},
        ],
        "data_effects": "Reads and locks UploadRecord; updates status/checksum; creates AuditEntry and OutboxEvent.",
        "transaction": "One transaction; UploadRecord lock precedes audit/outbox writes; provider I/O occurs after commit.",
        "handoff": "UploadCompleted.v1 -> uploads.workers.scan_upload -> MalwareScanner adapter.",
        "duplicates_concurrency": "Completion idempotency is upload id plus version; duplicate requests return the committed response and concurrent scan claims use one lease.",
        "terminal": "202 with uploaded state; later clean, rejected, or scan_failed terminal processing state.",
        "failures": "Authority, state, version, checksum, and blob mismatches write no domain/audit/outbox state; poison scan results terminalize scan_failed.",
        "observability": "Trace upload id, event id, scan attempt, duration, retry class, and terminal code; never log filename, content, checksum secret, or blob bytes.",
        "recovery": "Duplicate completion returns the existing outcome; retries deduplicate by upload id/version; operator reconciliation handles exhausted scans.",
    },
}
```

Add exactly one matching contract entry whose `kind` is `developer-flow`, `id` equals the flow id, and `anchor` equals the flow id.

## Contract registry

Each page registers the stable contracts it owns:

```python
"contracts": [
    {"kind": "developer-flow", "id": "code-flow-upload-completion", "anchor": "code-flow-upload-completion", "module_id": "MOD-UPLOADS", "scenario_ids": ["SCN-UPLOAD-001"], "refs": ["EVENT-UPLOAD-COMPLETED-V1"]},
    {"kind": "api-operation", "id": "API-COMPLETE-UPLOAD-V1", "anchor": "operation-complete-upload", "protocol": "HTTP/JSON", "address": "POST /uploads/{id}/complete", "authentication": "session bearer", "scope": "current workspace upload.complete", "success": "202 UploadIntentDTO", "errors": ["401 unauthenticated", "404 absent", "409 invalid_state", "422 invalid_checksum"], "idempotency": "Idempotency-Key bound to actor, route, upload id, version, and normalized body", "compatibility": "versioned JSON; unknown response fields forbidden", "client_mapping": "UploadsClient.completeUpload -> UploadIntentDTO", "refs": ["INPUT-COMPLETE-UPLOAD-V1", "DTO-UPLOAD-INTENT-V1"]},
]
```

Contract kinds are listed in `.specs/_validate.py::CONTRACT_KINDS`. Ids are globally unique. Every kind has mandatory exact fields in `.specs/_validate.py::CONTRACT_REQUIRED_FIELDS`. `api-operation`, `event`, `job`, and `provider` entries must reference their sealed schema contracts; every reference must resolve. Scenario contracts must name actor, authority, deterministic fixture, invocation, response, durable effects, forbidden effects, controls, cleanup, and executable evidence. The generator renders these source records in canonical expandable contract cards, so registries cannot pass while remaining invisible to readers.

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

Keep `.specs/_config.py::SPEC_STATUS` as `draft` and `SCAFFOLD_CONTENT_REPLACED` as `False` during discovery. Set them to `final` and `True` only after every `starter=True` page is removed or fully replaced, all five source-backed inventories are complete, repository-backed discovery maps every included runtime source unit to exactly one focused handbook, settings/common ownership is explicit, every implementation-unit inventory entry exactly matches its developer code-flow directory, requirements/decisions/contracts are traceable, focused page requirements pass, canonical asset hashes and shell landmarks pass, and the semantic evaluation has no hidden assumption.
