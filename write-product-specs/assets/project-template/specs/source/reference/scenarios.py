"""Draft executable acceptance scenario register."""

from source.__starter import starter_page

PAGE = starter_page(
    route="reference/executable-scenarios.html",
    nav_group="Project reference",
    nav_subgroup="Operations and assurance",
    nav_order=20,
    title="Executable acceptance, failure-injection, and conformance scenarios",
    summary="Stable scenarios with exact authority, fixtures, invocation cases, responses, durable and forbidden effects, controls, cleanup, and evidence.",
    kind="reference",
    sections=[("scenario-format", "Scenario fixture and assertion format"), ("scenario-catalog", "Stable executable scenario catalog"), ("conformance-map", "Implementation and evidence mapping")],
    related=["reference/coverage.html", "operations/deployment-and-recovery.html"],
)
