"""Draft example showing the required backend/runtime module handbook anatomy."""

from source.__starter import starter_page

PAGE = starter_page(
    route="architecture/backend/modules/replace-with-real-module.html",
    nav_group="Architecture",
    nav_subgroup="Backend implementation handbook",
    nav_order=30,
    title="Replace with one natural backend implementation-unit handbook",
    summary="Delete or fully replace this draft with one application, service, package, bounded context, worker, or equivalent natural code owner.",
    kind="runtime-module",
    sections=[
        ("responsibility-boundary", "Implementation-unit responsibility and public boundary"),
        ("developer-code-flow-directory", "Developer code-flow directory"),
        ("model-schema", "Complete owned model and data schema"),
        ("product-runtime-handoffs", "Product journeys and cross-module runtime handoffs"),
        ("commands-queries", "Commands, transactions, and scoped queries"),
        ("api-security", "Operations, authorization, and stable failures"),
        ("events-jobs-recovery", "Events, jobs, providers, and recovery"),
        ("transitions-acceptance", "Legal transitions and executable proof"),
        ("related-designs", "Canonical owners and related system designs"),
    ],
    related=["architecture/backend/implementation-handbook.html", "architecture/backend/common-platform-foundations.html"],
)
