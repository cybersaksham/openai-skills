"""Draft example showing the required architecture-flow anatomy."""

from source.__starter import starter_page

PAGE = starter_page(
    route="architecture/flows/replace-with-real-runtime-flow.html",
    nav_group="Architecture",
    nav_subgroup="Platform system designs",
    nav_order=10,
    title="Replace with one concrete end-to-end runtime flow",
    summary="Delete or fully replace this draft with an actual upload, email, webhook, authentication, event, provider, migration, or other independent sequence.",
    kind="architecture-flow",
    sections=[
        ("purpose-scope", "Purpose, scope, and non-goals"),
        ("components-ownership", "Components and ownership"),
        ("trigger-inputs", "Trigger and exact inputs"),
        ("chronological-sequence", "Chronological sequence"),
        ("transactions-consistency", "Transactions, consistency, and lock boundaries"),
        ("durable-writes", "Data read and written at each durable point"),
        ("contracts", "Interface, event, job, and provider contracts"),
        ("idempotency-concurrency", "Idempotency, ordering, duplicates, and concurrency"),
        ("timeouts-retries", "Timeouts, retries, dead letter, and reconciliation"),
        ("failure-reconciliation", "Failure classification and operator recovery"),
        ("security-audit", "Permissions, secrets, sensitive data, and audit"),
        ("observability-operations", "Observability and operations"),
        ("acceptance", "Acceptance and failure-injection scenarios"),
        ("dependent-journeys", "Dependent product journeys"),
    ],
    related=["architecture/guide.html", "product-journeys.html"],
)
