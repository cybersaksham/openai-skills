"""Helpers for draft-only pages that establish the canonical documentation architecture."""

from __future__ import annotations


def starter_page(
    *,
    route: str,
    nav_group: str,
    nav_order: int,
    title: str,
    summary: str,
    kind: str = "overview",
    nav_subgroup: str = "",
    nav_parent: str = "",
    nav_category: str = "",
    nav_label: str = "",
    sections: list[tuple[str, str]] | None = None,
    related: list[str] | None = None,
) -> dict[str, object]:
    prompts = sections or [("scope", "Replace this starter with the complete project-specific owner and contract.")]
    return {
        "route": route,
        "nav_group": nav_group,
        "nav_subgroup": nav_subgroup,
        "nav_parent": nav_parent,
        "nav_category": nav_category,
        "nav_order": nav_order,
        "nav_label": nav_label or title,
        "title": title,
        "summary": summary,
        "kind": kind,
        "starter": True,
        "sections": [
            {
                "id": section_id,
                "title": section_title,
                "blocks": [
                    {
                        "type": "paragraph",
                        "text": "Draft scaffold owner. Replace this section with exact product and system-design decisions discovered for the target project.",
                    }
                ],
            }
            for section_id, section_title in prompts
        ],
        "related": related or [],
        "contracts": [],
        "requirements": [],
        "decisions": [],
    }
