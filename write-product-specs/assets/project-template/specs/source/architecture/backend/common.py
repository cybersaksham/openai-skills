"""Draft shared backend foundation contract."""

from source.__starter import starter_page

PAGE = starter_page(
    route="architecture/backend/common-platform-foundations.html",
    nav_group="Architecture",
    nav_subgroup="Backend implementation handbook",
    nav_order=20,
    nav_label="Common platform foundations",
    title="Common platform foundations used by backend implementation units",
    summary="Shared transport, persistence, transactions, authentication, audit, storage, messaging, and provider primitives without feature-policy ownership.",
    sections=[("common-package-map", "Shared package ownership map"), ("common-data-contracts", "Shared data contracts"), ("common-runtime-flows", "Shared runtime flows"), ("common-invariants", "Security, concurrency, and failure invariants")],
    related=["architecture/backend/implementation-handbook.html", "architecture/backend/modules/replace-with-real-module.html"],
)
