"""Requirement, contract, and conformance coverage map."""

PAGE = {
    "route": "reference/coverage.html",
    "nav_group": "Reference",
    "nav_order": 20,
    "title": "Requirement, contract, and evidence coverage",
    "summary": "Trace every supplied requirement and stable contract to its normative page, implementation target, and executable evidence.",
    "kind": "coverage",
    "sections": [
        {
            "id": "requirement-coverage",
            "title": "Requirement coverage",
            "blocks": [
                {"type": "table", "headers": ["Requirement", "Source", "Status", "Normative destinations"], "rows": [["No requirements registered", "Initial scaffold", "draft", "Product discovery must populate source-owned destinations"]]}
            ],
        },
        {
            "id": "contract-coverage",
            "title": "Contract and evidence coverage",
            "blocks": [
                {"type": "table", "headers": ["Contract", "Owner", "Consumers", "Scenario and evidence"], "rows": [["No contracts registered", "Initial scaffold", "No consumers mapped", "No conformance evidence mapped"]]}
            ],
        },
    ],
    "related": ["index.html", "architecture/system-map.html", "reference/decisions.html"],
    "contracts": [],
    "requirements": [],
    "decisions": [],
}
