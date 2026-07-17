"""Draft client nonvisual runtime contract."""

from source.__starter import starter_page

PAGE = starter_page(
    route="architecture/client/nonvisual-runtime.html",
    nav_group="Architecture",
    nav_subgroup="Frontend implementation",
    nav_order=10,
    title="Client routes, state ownership, interaction behavior, and accessibility",
    summary="The exact nonvisual contract for screens or client surfaces independent of pending page-level visual design.",
    kind="client-runtime",
    sections=[
        ("scope-ownership", "Scope and ownership"),
        ("routes-surfaces", "Routes and surfaces"),
        ("state-owners", "Server, URL, draft, controller, and visual state owners"),
        ("interface-authority", "Generated interface and action authority"),
        ("interaction-states", "Loading, empty, denial, stale, offline, and error states"),
        ("accessibility", "Semantics, keyboard, focus, and announcements"),
        ("failure-recovery", "Reconnect, schema mismatch, and recovery"),
        ("evidence", "Client and accessibility evidence")
    ],
    related=["reference/api-and-payload-contracts.html", "reference/executable-scenarios.html"],
)
