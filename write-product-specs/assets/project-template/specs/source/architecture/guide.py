"""Draft architecture guide."""

from source.__starter import starter_page

PAGE = starter_page(
    route="architecture/guide.html",
    nav_group="Architecture",
    nav_subgroup="System foundations",
    nav_order=5,
    nav_label="Architecture guide",
    title="Architecture guide from runtime boundaries to operational proof",
    summary="Reader map for system foundations, backend handbooks, focused flows, clients, interfaces, and assurance.",
    sections=[("architecture-map", "Architecture documentation map"), ("reading-order", "Architecture reading order")],
    related=["architecture/system-map.html", "architecture/backend/implementation-handbook.html"],
)
