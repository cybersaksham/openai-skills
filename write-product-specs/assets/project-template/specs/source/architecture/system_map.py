"""Top-level product runtime map."""

PAGE = {
    "route": "architecture/system-map.html",
    "nav_group": "Architecture flows",
    "nav_order": 0,
    "title": "Product runtime boundaries and ownership map",
    "summary": "The discoverable map from actors and clients through trusted runtime boundaries, data stores, asynchronous work, providers, and operations.",
    "kind": "overview",
    "sections": [
        {
            "id": "system-boundaries",
            "title": "System boundaries",
            "blocks": [
                {"type": "paragraph", "text": "Replace this starter section with the actual deployable units, clients, gateways, backend/runtime modules, workers, stores, queues, providers, and operator surfaces."}
            ],
        },
        {
            "id": "dependency-direction",
            "title": "Dependency direction and public seams",
            "blocks": [
                {"type": "paragraph", "text": "Name which boundary owns each domain truth and which typed interfaces, events, or adapters permit cross-boundary access. Keep transport and presentation layers from becoming domain owners."}
            ],
        },
        {
            "id": "flow-directory",
            "title": "Focused runtime flow directory",
            "blocks": [
                {"type": "paragraph", "text": "Create one architecture page for every independently triggered sequence with persistence, ordering, provider, failure, or recovery behavior. Link each product journey and runtime module handbook to those pages."}
            ],
        },
    ],
    "related": ["index.html", "start-here.html", "reference/coverage.html"],
    "contracts": [],
    "requirements": [],
    "decisions": [],
}
