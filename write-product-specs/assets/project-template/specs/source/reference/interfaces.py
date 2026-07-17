"""Draft API and payload contract catalog."""

from source.__starter import starter_page

PAGE = starter_page(
    route="reference/api-and-payload-contracts.html",
    nav_group="Project reference",
    nav_subgroup="Data and interfaces",
    nav_order=20,
    title="Closed API, interface, request, response, and generated-client contracts",
    summary="Every operation and public payload with exact authentication, scope, schemas, outcomes, errors, metadata, idempotency, and compatibility.",
    kind="reference",
    sections=[("transport-rules", "Transport and compatibility rules"), ("input-schemas", "Sealed reusable input schemas"), ("output-schemas", "Sealed response schemas"), ("operation-catalog", "Closed operation catalog")],
    related=["reference/data-dictionary.html", "reference/async-provider-contracts.html"],
)
