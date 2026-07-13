"""Curated cross-cutting documentation pages."""


def scaffold_page(eyebrow: str, title: str, intro: str, sections: list[tuple[str, str]]) -> str:
    body = [
        f'<section class="hero" data-searchable><div class="eyebrow">{eyebrow}</div>',
        f"<h1>{title}</h1><p>{intro}</p></section>",
    ]
    for section_id, heading in sections:
        body.append(
            f'<section data-searchable><h2 id="{section_id}">{heading}</h2>'
            f'<div class="callout warn"><strong>TODO</strong>Replace this scaffold with complete, '
            "decision-resolved product documentation.</div></section>"
        )
    return "".join(body)


PAGES = {
    "index.html": (
        "Overview",
        scaffold_page(
            "Product documentation",
            "Understand the complete product",
            "TODO: explain the product promise and why it matters.",
            [
                ("product-promise", "Product promise"),
                ("audiences", "People and outcomes"),
                ("feature-map", "Feature map"),
                ("current-scope", "Current scope and boundaries"),
            ],
        ),
    ),
    "product-flows.html": (
        "Experience and flows",
        scaffold_page(
            "Product experience",
            "How people move through the product",
            "TODO: document the global information architecture and end-to-end journeys.",
            [
                ("information-architecture", "Information architecture"),
                ("actor-journeys", "Actor journeys"),
                ("cross-feature-flows", "Cross-feature flows"),
                ("global-experience-rules", "Global experience rules"),
            ],
        ),
    ),
    "decisions.html": (
        "Decisions",
        scaffold_page(
            "Product authority",
            "Confirmed decisions and their consequences",
            "TODO: explain how decisions become current product and system truth.",
            [("decision-policy", "Decision policy")],
        ),
    ),
    "roadmap.html": (
        "Roadmap and boundaries",
        scaffold_page(
            "Scope boundaries",
            "What is current, designed for later, and excluded",
            "TODO: separate current scope from future compatibility and unapproved ideas.",
            [
                ("current-release", "Current product scope"),
                ("extension-seams", "Designed extension seams"),
                ("future-capabilities", "Future capabilities"),
                ("explicit-non-goals", "Explicit non-goals"),
            ],
        ),
    ),
    "system-architecture.html": (
        "System overview",
        scaffold_page(
            "System design",
            "How the product is divided and how work flows",
            "TODO: define contexts, runtimes, ownership, dependencies, and execution paths.",
            [
                ("system-context", "System context"),
                ("runtime-boundaries", "Runtime boundaries"),
                ("ownership", "Domain and data ownership"),
                ("execution-paths", "Synchronous and asynchronous execution"),
                ("dependency-direction", "Dependency direction"),
            ],
        ),
    ),
    "repository-blueprint.html": (
        "Repository blueprint",
        scaffold_page(
            "Code architecture",
            "Exact repository and module structure",
            "TODO: document the intended roots, files, dependency rules, generated artifacts, and commands.",
            [
                ("runtime-baseline", "Runtime and toolchain baseline"),
                ("root-layout", "Repository root layout"),
                ("module-layouts", "Runtime and module layouts"),
                ("dependency-rules", "Dependency and ownership rules"),
                ("verification-commands", "Canonical verification commands"),
            ],
        ),
    ),
    "runtime-architecture.html": (
        "Runtime architecture",
        scaffold_page(
            "Authoritative runtime",
            "Execution, ownership, storage, and asynchronous work",
            "TODO: document the product's real execution boundaries; combine or split them without inventing a layer.",
            [
                ("execution-lifecycle", "Request, command, or execution lifecycle"),
                ("domain-boundaries", "Domain, policy, command, query, and interface boundaries"),
                ("storage-transactions", "Storage, consistency, transactions, and concurrency"),
                ("asynchronous-work", "Asynchronous work"),
                ("runtime-configuration", "Runtime configuration and startup contract"),
            ],
        ),
    ),
    "interaction-surfaces.html": (
        "Interaction surfaces",
        scaffold_page(
            "Interaction architecture",
            "Surfaces, transitions, state, input, and feedback",
            "TODO: document every human, operator, device, conversational, or programmatic surface without assuming a separate client.",
            [
                ("surface-inventory", "Surface inventory, actors, and purpose"),
                ("entry-navigation", "Entry, navigation, transitions, and deep links"),
                ("interaction-boundaries", "Interaction module and presentation boundaries"),
                ("state-session", "Remote, local, session, and interrupted state"),
                ("input-feedback", "Input, validation, errors, feedback, and recovery"),
                ("accessibility-adaptation", "Accessibility, modality, device, and responsive adaptation"),
                ("interaction-verification", "Interaction, accessibility, and state verification"),
            ],
        ),
    ),
    "domain-model.html": (
        "Domain model",
        scaffold_page(
            "Domain language",
            "Aggregates, relationships, lifecycle, and ownership",
            "TODO: explain the conceptual model before its storage representation.",
            [
                ("vocabulary", "Canonical vocabulary"),
                ("aggregates", "Aggregates and ownership"),
                ("relationships", "Relationships and cross-domain contracts"),
                ("history-lifecycle", "Lifecycle, versioning, and history"),
            ],
        ),
    ),
    "data-dictionary.html": (
        "Data dictionary",
        scaffold_page(
            "Persisted data",
            "Exact records, fields, constraints, and indexes",
            "TODO: explain shared data conventions; generated feature record catalogs appear below.",
            [
                ("data-conventions", "Identifiers, time, nullability, and deletion"),
                ("shared-records", "Shared records and indexes"),
            ],
        ),
    ),
    "permissions.html": (
        "Permissions",
        scaffold_page(
            "Authorization",
            "Actors, scope, capabilities, and audit",
            "TODO: define authentication, authority derivation, denial behavior, and shared permission rules.",
            [
                ("actors-capabilities", "Actors and capabilities"),
                ("scope-resolution", "Scope and object checks"),
                ("denial-audit", "Denial and audit behavior"),
            ],
        ),
    ),
    "transport-contracts.html": (
        "Transport and interfaces",
        scaffold_page(
            "Interface contracts",
            "Stable operations and schemas across boundaries",
            "TODO: define protocol-wide conventions; generated feature operations appear below.",
            [
                ("interface-conventions", "Interface conventions"),
                ("authentication-errors", "Authentication, concurrency, and errors"),
            ],
        ),
    ),
    "events-jobs.html": (
        "Events and jobs",
        scaffold_page(
            "Asynchronous contracts",
            "Events, consumers, schedules, retries, and replay",
            "TODO: define shared envelopes and reliability rules; generated catalogs appear below.",
            [
                ("event-envelope", "Event or message envelope"),
                ("job-reliability", "Job reliability and terminal behavior"),
            ],
        ),
    ),
    "integrations.html": (
        "Integrations",
        scaffold_page(
            "External boundaries",
            "Systems, adapters, credentials, resilience, and reconciliation",
            "TODO: document every external dependency, or record the owner's explicit exclusion when none is in scope.",
            [
                ("integration-landscape", "Integration inventory, purpose, and data classification"),
                ("ownership-boundaries", "Authority, ownership, and lifecycle boundaries"),
                ("capability-contracts", "Adapter operations, schemas, protocols, and versions"),
                ("credentials-configuration", "Credential scope, configuration, rotation, and revocation"),
                ("inbound-callbacks", "Inbound callbacks, verification, replay defense, and acknowledgement"),
                ("resilience-rate-limits", "Timeouts, retries, idempotency, rate limits, and degradation"),
                ("failure-reconciliation", "Partial failure, duplicate handling, reconciliation, and recovery"),
                ("integration-testing", "Sandboxes, test doubles, provider contracts, and compatibility"),
                ("integration-observability", "Safe telemetry, outage signals, runbooks, and ownership"),
            ],
        ),
    ),
    "operations.html": (
        "Operations",
        scaffold_page(
            "Operational lifecycle",
            "Environments, release, recovery, capacity, and ownership",
            "TODO: document the complete operational lifecycle, or record the owner's explicit scope exclusion.",
            [
                ("environments", "Environments, topology differences, and promotion boundaries"),
                ("configuration", "Configuration inventory, defaults, validation, and startup failure"),
                ("secrets", "Secret ownership, storage, access, rotation, and revocation"),
                ("migrations-data-change", "Schema, data, compatibility, and migration operations"),
                ("release-rollout", "Release prerequisites, rollout strategy, gates, and verification"),
                ("rollback-forward-fix", "Rollback, forward-fix, and compatibility policy"),
                ("backup-restore", "Backup scope, restore procedure, evidence, and drills"),
                ("disaster-recovery", "Failure scenarios, recovery objectives, authority, and communication"),
                ("scaling-capacity", "Capacity assumptions, scaling boundaries, quotas, and cost controls"),
                ("service-levels-alerting", "Service levels, signals, alerts, escalation, and incident criteria"),
                ("runbooks-ownership", "Runbooks, replay/repair tools, maintenance, and operational ownership"),
            ],
        ),
    ),
    "quality.html": (
        "Quality and security",
        scaffold_page(
            "Production-grade baseline",
            "Testing, privacy, security, reliability, and observability",
            "TODO: define complete quality and operational standards for this product.",
            [
                ("test-matrix", "Test matrix"),
                ("security", "Security controls"),
                ("privacy-retention", "Privacy and retention"),
                ("observability", "Observability and operations"),
                ("performance", "Performance and scale"),
                ("migration-quality", "Migration and compatibility quality"),
            ],
        ),
    ),
    "implementation-sequence.html": (
        "Implementation sequence",
        scaffold_page(
            "Dependency-aware sequence",
            "Build vertical outcomes in a safe order",
            "TODO: document prerequisite foundations, vertical slices, integration order, and proof gates without estimates.",
            [
                ("dependency-graph", "Dependency graph"),
                ("vertical-sequence", "Vertical implementation sequence"),
                ("integration-gates", "Integration and proof gates"),
            ],
        ),
    ),
    "audit.html": (
        "Documentation audit",
        scaffold_page(
            "Specification health",
            "Coverage, consistency, and implementation readiness",
            "TODO: explain audit authority and product-specific regression checks; generated coverage appears below.",
            [
                ("authority-order", "Authority order"),
                ("audit-method", "Audit method"),
                ("known-boundaries", "Known boundaries"),
            ],
        ),
    ),
    "coverage.html": (
        "Requirement coverage",
        scaffold_page(
            "Traceability",
            "Every supplied requirement has a rendered home",
            "TODO: explain requirement classification and supersession; generated coverage appears below.",
            [("coverage-policy", "Coverage policy")],
        ),
    ),
}
