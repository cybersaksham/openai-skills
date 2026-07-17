"""Product and system-design decision register."""

PAGE = {
    "route": "reference/decisions.html",
    "nav_group": "Project reference",
    "nav_subgroup": "Traceability",
    "nav_order": 10,
    "nav_label": "Product and architecture decisions",
    "title": "Confirmed and pending product decisions",
    "summary": "One register for questions, confirmed choices, rationale, consequences, confirmation context, and affected contracts.",
    "kind": "decision-register",
    "starter": True,
    "sections": [
        {
            "id": "decision-register",
            "title": "Decision register",
            "blocks": [
                {
                    "type": "table",
                    "headers": ["Decision", "Question", "Status", "Choice", "Rationale", "Affected contracts"],
                    "rows": [["No decisions registered", "Product discovery has not populated this register", "draft", "Not selected", "Owner discovery is required", "All affected focused pages"]],
                }
            ],
        }
    ],
    "related": ["start-here.html", "reference/coverage.html"],
    "contracts": [],
    "requirements": [],
    "decisions": [],
}
