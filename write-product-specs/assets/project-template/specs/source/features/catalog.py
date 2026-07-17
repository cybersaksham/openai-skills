"""Draft feature guide directory."""

from source.__starter import starter_page

PAGE = starter_page(
    route="features.html",
    nav_group="Product guides",
    nav_order=0,
    nav_label="Product guide overview",
    title="Product guides grouped by user outcome",
    summary="Feature overviews route to concrete user flows, system designs, contracts, recovery, and source evidence.",
    sections=[("feature-map", "Feature guide directory"), ("feature-ownership", "Feature ownership and boundaries")],
    related=["product-journeys.html", "architecture/guide.html"],
)
