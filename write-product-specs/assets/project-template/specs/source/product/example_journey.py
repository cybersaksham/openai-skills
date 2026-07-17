"""Draft example showing the required product-journey anatomy."""

from source.__starter import starter_page

PAGE = starter_page(
    route="journeys/replace-with-real-journey.html",
    nav_group="Product journeys",
    nav_order=10,
    title="Replace with one concrete product journey",
    summary="Delete or fully replace this draft page after discovering the product's actual actors and outcomes.",
    kind="product-journey",
    sections=[
        ("outcome-scope", "Outcome, scope, and non-goals"),
        ("actors-authority", "Actors and authority"),
        ("preconditions", "Preconditions and entry points"),
        ("happy-path", "Ordered happy path"),
        ("alternatives-denials", "Alternatives, denials, stale, and offline paths"),
        ("states-effects", "State model and durable effects"),
        ("handoffs", "Cross-feature and external handoffs"),
        ("notifications-audit", "Notifications, privacy, and audit"),
        ("failure-recovery", "Failure, retry, cancellation, and recovery"),
        ("client-behavior", "Client nonvisual behavior and accessibility"),
        ("acceptance", "Stable acceptance scenarios"),
        ("related-contracts", "Related system designs and exact contracts"),
    ],
    related=["product-journeys.html", "architecture/system-map.html"],
)
