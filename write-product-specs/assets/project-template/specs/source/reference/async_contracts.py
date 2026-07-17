"""Draft asynchronous and provider contract catalogs."""

from source.__starter import starter_page

PAGE = starter_page(
    route="reference/async-provider-contracts.html",
    nav_group="Project reference",
    nav_subgroup="Data and interfaces",
    nav_order=30,
    title="Events, jobs, schedules, providers, callbacks, and reconciliation contracts",
    summary="Typed asynchronous and external-system boundaries from durable dispatch through retry, dead letter, replay, callback verification, and terminal reconciliation.",
    kind="reference",
    sections=[("event-catalog", "Domain event catalog"), ("job-catalog", "Background job and schedule catalog"), ("provider-catalog", "Provider adapter and callback catalog"), ("reliability", "Ordering, retries, dead letter, replay, and reconciliation")],
    related=["reference/api-and-payload-contracts.html", "architecture/flows/replace-with-real-runtime-flow.html"],
)
