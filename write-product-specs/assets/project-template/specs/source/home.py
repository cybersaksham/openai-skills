"""Specification home and authority map."""

PAGE = {
    "route": "index.html",
    "nav_group": "Start here",
    "nav_order": 0,
    "nav_label": "Documentation home",
    "title": "__PRODUCT_NAME__ product specifications",
    "summary": "__PRODUCT_TAGLINE__ This generated site will become the sole intended product and system-design authority.",
    "kind": "overview",
    "starter": True,
    "sections": [
        {
            "id": "authority-and-scope",
            "title": "Authority and current scope",
            "blocks": [
                {
                    "type": "callout",
                    "tone": "warning",
                    "title": "Draft specification system",
                    "text": "The documentation scaffold is active, but product-specific discovery, decisions, contracts, and acceptance evidence must be authored before SPEC_STATUS can become final.",
                },
                {
                    "type": "paragraph",
                    "text": "Generated HTML pages are the readable authority. Their source modules under .specs/source are the only editable specification source.",
                },
            ],
        },
        {
            "id": "reader-routes",
            "title": "Choose a reading route",
            "blocks": [
                {
                    "type": "cards",
                    "items": [
                        {"kicker": "New reader", "title": "Start with product and vocabulary", "text": "Use [[Start here|start-here.html]] to learn the authority boundary and reading order."},
                        {"kicker": "Developer", "title": "Follow system ownership", "text": "Use [[System map|architecture/system-map.html]] before opening focused runtime and module pages."},
                        {"kicker": "Reviewer", "title": "Inspect evidence", "text": "Use [[Requirement and contract coverage|reference/coverage.html]] to trace supplied intent to executable proof."},
                    ],
                }
            ],
        },
        {
            "id": "product-system-map",
            "title": "Product and system map",
            "blocks": [
                {
                    "type": "paragraph",
                    "text": "Replace this starter map with the product promise, actors, journeys, runtime boundaries, data owners, interfaces, asynchronous work, providers, clients, deployment topology, and operational ownership discovered for __PRODUCT_NAME__.",
                }
            ],
        },
    ],
    "related": ["start-here.html", "architecture/system-map.html", "reference/coverage.html"],
    "contracts": [],
    "requirements": [],
    "decisions": [],
}
