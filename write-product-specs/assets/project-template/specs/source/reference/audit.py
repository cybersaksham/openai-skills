"""Draft audit and implementation-readiness report."""

from source.__starter import starter_page

PAGE = starter_page(
    route="reference/audit.html",
    nav_group="Project reference",
    nav_subgroup="Traceability",
    nav_order=30,
    title="Specification correctness, completeness, and implementation-readiness audit",
    summary="Mechanical evidence, semantic category scores, deductions, assumptions, and the smallest remaining actions.",
    kind="reference",
    sections=[("mechanical-evidence", "Mechanical quality evidence"), ("semantic-rating", "Semantic implementation-readiness rating"), ("remaining-gaps", "Remaining decisions, contradictions, and completeness gaps")],
    related=["reference/coverage.html", "reference/executable-scenarios.html"],
)
