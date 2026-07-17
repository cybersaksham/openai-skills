"""Draft canonical data dictionary."""

from source.__starter import starter_page

PAGE = starter_page(
    route="reference/data-dictionary.html",
    nav_group="Project reference",
    nav_subgroup="Data and interfaces",
    nav_order=10,
    title="Code-format domain and persistence data dictionary",
    summary="One canonical code-formatted schema owner for entities, fields, relationships, constraints, indexes, lifecycle, migration, and concurrency.",
    kind="reference",
    sections=[("schema-language", "Schema language and type resolution"), ("data-schemas", "Complete code-format schemas"), ("lifecycle", "Lifecycle, retention, deletion, and restore")],
    related=["reference/api-and-payload-contracts.html", "architecture/backend/implementation-handbook.html"],
)
