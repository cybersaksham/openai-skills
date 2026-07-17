"""Draft backend implementation handbook directory."""

from source.__starter import starter_page

PAGE = starter_page(
    route="architecture/backend/implementation-handbook.html",
    nav_group="Architecture",
    nav_subgroup="Backend implementation handbook",
    nav_order=0,
    nav_label="Backend implementation handbook",
    title="Backend implementation handbook and module directory",
    summary="Configuration, shared foundations, and one developer handbook per natural backend implementation unit.",
    sections=[("backend-reading-order", "Backend reading order"), ("module-directory", "Complete implementation-unit directory")],
    related=["architecture/backend/configuration-and-settings.html", "architecture/backend/common-platform-foundations.html"],
)
