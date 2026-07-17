"""Reading order and authority boundaries."""

PAGE = {
    "route": "start-here.html",
    "nav_group": "Start here",
    "nav_order": 10,
    "nav_label": "How to read these specifications",
    "title": "Read and implement from the specifications",
    "summary": "How humans and implementation agents navigate authority, focused flows, exact contracts, and acceptance evidence.",
    "kind": "overview",
    "starter": True,
    "sections": [
        {
            "id": "reading-order",
            "title": "Reading order",
            "blocks": [
                {
                    "type": "sequence",
                    "items": [
                        {"title": "Understand the outcome", "text": "Read the complete product journey and its alternatives before technical contracts."},
                        {"title": "Follow ownership", "text": "Trace every step through focused architecture flows and runtime module developer handbooks."},
                        {"title": "Close exact contracts", "text": "Read code-format data schemas, sealed interface payloads, states, events/jobs/providers, security, and operations."},
                        {"title": "Prove behavior", "text": "Map stable acceptance scenarios and clauses to implementation and executable evidence."},
                    ],
                }
            ],
        },
        {
            "id": "authority-boundary",
            "title": "Authority boundary",
            "blocks": [
                {"type": "paragraph", "text": "The specifications define intended outcomes and system design. Code, tests, schemas, and infrastructure show implementation state and must be reconciled without silently overriding confirmed decisions."},
                {"type": "callout", "tone": "note", "title": "Missing decisions stop dependent work", "text": "When a material decision is absent or contradictory, ask the focused owner question, update the specification first, regenerate, validate, rate, and only then plan or implement."},
            ],
        },
        {
            "id": "implementation-order",
            "title": "Specification-first implementation order",
            "blocks": [
                {"type": "paragraph", "text": "The repository skill pipeline is maintain specifications, create a specification-backed plan, implement vertical slices with tests, and perform final clause-by-clause conformance."}
            ],
        },
    ],
    "related": ["index.html", "architecture/system-map.html", "reference/decisions.html"],
    "contracts": [],
    "requirements": [],
    "decisions": [],
}
