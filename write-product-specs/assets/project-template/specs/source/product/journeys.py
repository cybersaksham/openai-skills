"""Draft product journey directory."""

from source.__starter import starter_page

PAGE = starter_page(
    route="product-journeys.html",
    nav_group="Product journeys",
    nav_order=0,
    nav_label="Product journey overview",
    title="Product journeys from actor intent to terminal outcome",
    summary="A routing map for every independently understandable user or system journey.",
    sections=[("journey-map", "Product journey directory"), ("cross-journey-rules", "Cross-journey rules")],
    related=["start-here.html", "architecture/system-map.html"],
)
