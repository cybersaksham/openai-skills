"""Draft bootstrap, migration, deployment, and recovery flow."""

from source.__starter import starter_page

PAGE = starter_page(
    route="operations/deployment-and-recovery.html",
    nav_group="Project reference",
    nav_subgroup="Operations and assurance",
    nav_order=10,
    title="Bootstrap, migrations, deployment rollout, rollback, backup, and recovery",
    summary="Executable fresh-install, upgrade, compatibility, rollout, rollback, readiness, RPO/RTO, restore, and operator-recovery contracts.",
    kind="architecture-flow",
    sections=[
        ("purpose-scope", "Purpose, scope, and non-goals"),
        ("components-ownership", "Components and ownership"),
        ("trigger-inputs", "Release trigger and exact inputs"),
        ("chronological-sequence", "Bootstrap and rollout sequence"),
        ("transactions-consistency", "Migration transactions and compatibility"),
        ("durable-writes", "Schema, data, and artifact effects"),
        ("contracts", "Build, health, readiness, and deployment contracts"),
        ("idempotency-concurrency", "Resume, duplicate, and concurrent rollout behavior"),
        ("timeouts-retries", "Observation windows and retry limits"),
        ("failure-reconciliation", "Rollback and operator recovery"),
        ("security-audit", "Secret handling and release audit"),
        ("observability-operations", "Metrics, thresholds, RPO/RTO, and restore proof"),
        ("acceptance", "Migration and recovery scenarios"),
        ("dependent-journeys", "Product availability dependencies"),
    ],
    related=["architecture/backend/configuration-and-settings.html", "reference/executable-scenarios.html"],
)
