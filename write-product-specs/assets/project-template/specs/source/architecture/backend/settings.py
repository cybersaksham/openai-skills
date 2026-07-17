"""Draft backend settings and configuration contract."""

from source.__starter import starter_page

PAGE = starter_page(
    route="architecture/backend/configuration-and-settings.html",
    nav_group="Architecture",
    nav_subgroup="Backend implementation handbook",
    nav_order=10,
    nav_label="Configuration and settings",
    title="Backend configuration, settings, environments, and startup validation",
    summary="Exact configuration ownership, required/default values, secret boundaries, mode selection, and fail-fast startup behavior.",
    sections=[("configuration-inventory", "Configuration inventory"), ("startup-validation", "Startup validation and failure behavior"), ("environment-mapping", "Environment and deployment mapping")],
    related=["architecture/backend/implementation-handbook.html", "operations/deployment-and-recovery.html"],
)
