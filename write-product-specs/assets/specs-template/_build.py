#!/usr/bin/env python3
"""Generate the static product and technical documentation."""

from __future__ import annotations

import html
import os
import re
from pathlib import Path

from _events import EVENTS
from _features import FEATURES
from _html_policy import css_issues, scan_html, url_issue
from _low_level_design import LOW_LEVEL_DESIGN
from _manifest import ASSET_VERSION, FEATURE_GROUPS, PAGE_GROUPS, PRODUCT_NAME, PRODUCT_TAGLINE
from _pages import PAGES
from _requirements import DECISIONS, REQUIREMENTS
from _routes import ROUTES
from _system_design import SYSTEM_DESIGN


OUT = Path(__file__).resolve().parent
SYSTEM_FALLBACK = {
    "architecture": "Pending system-design documentation.",
    "runtime_flow": [],
    "interaction_flow": [],
    "commands": [],
    "queries": [],
    "transitions": [],
    "contracts": [],
    "reconciliations": [],
    "tests": [],
}
LOW_LEVEL_FALLBACK = {
    "files": [],
    "records": [],
    "commands": [],
    "queries": [],
    "interfaces": [],
    "interaction_modules": [],
    "jobs": [],
    "migrations": [],
    "telemetry": [],
    "errors": [],
}
SAFE_PAGE_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\.html")
SAFE_FEATURE_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


class SafeHtml(str):
    """A renderer-owned fragment whose dynamic values were already escaped."""


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def cell_html(value: object) -> str:
    return str(value) if isinstance(value, SafeHtml) else esc(value)


def list_html(items: list[object], cls: str = "") -> str:
    if not items:
        return '<p class="muted">No entries documented.</p>'
    return f'<ul class="{esc(cls)}">' + "".join(f"<li>{esc(item)}</li>" for item in items) + "</ul>"


def table_html(headers: tuple[str, ...], rows: list[tuple[object, ...]]) -> str:
    if not rows:
        return '<p class="muted">No entries documented.</p>'
    header = "".join(f"<th>{esc(item)}</th>" for item in headers)
    body = "".join(
        '<tr data-searchable>' + "".join(f"<td>{cell_html(cell)}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return f"<table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>"


def card_rows(rows: list[tuple[object, object, object]]) -> str:
    if not rows:
        return '<p class="muted">No entries documented.</p>'
    return '<div class="grid">' + "".join(
        '<section class="card span-6" data-searchable>'
        f'<div class="card-kicker">{esc(kicker)}</div><h3>{esc(title)}</h3><p>{esc(body)}</p></section>'
        for title, kicker, body in rows
    ) + "</div>"


def nav_list(items: list[tuple[str, str]], current: str, prefix: str, nested: bool = False) -> str:
    cls = "nav-list nested" if nested else "nav-list"
    links = []
    for target, label in items:
        selected = ' aria-current="page"' if target == current else ""
        links.append(
            f'<li><a href="{prefix}{esc(target)}"{selected}><span class="nav-dot"></span>{esc(label)}</a></li>'
        )
    return f'<ul class="{cls}">' + "".join(links) + "</ul>"


def nav_html(current: str, prefix: str) -> str:
    groups: list[str] = []
    for label, items in PAGE_GROUPS[:2]:
        opened = " open" if current in {item[0] for item in items} else ""
        groups.append(
            f'<details class="nav-group"{opened}><summary>{esc(label)}</summary>'
            f"{nav_list(items, current, prefix)}</details>"
        )

    feature_subgroups = []
    for group in FEATURE_GROUPS:
        items = [
            (f"features/{feature['slug']}.html", feature["name"])
            for feature in FEATURES
            if feature["group"] == group
        ]
        opened = " open" if current in {item[0] for item in items} else ""
        feature_subgroups.append(
            f'<details class="nav-subgroup"{opened}><summary>{esc(group)}</summary>'
            f"{nav_list(items, current, prefix, nested=True)}</details>"
        )
    feature_open = " open" if current.startswith("features/") else ""
    groups.append(
        f'<details class="nav-group"{feature_open}><summary>Features</summary>'
        f'<div class="nav-subgroups">{"".join(feature_subgroups)}</div></details>'
    )

    for label, items in PAGE_GROUPS[2:]:
        opened = " open" if current in {item[0] for item in items} else ""
        groups.append(
            f'<details class="nav-group"{opened}><summary>{esc(label)}</summary>'
            f"{nav_list(items, current, prefix)}</details>"
        )
    return "".join(groups)


def shell(title: str, current: str, content: str, feature_page: bool = False) -> str:
    prefix = "../" if feature_page else ""
    initial = PRODUCT_NAME[:1].upper() or "P"
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{esc(PRODUCT_NAME)} — {esc(PRODUCT_TAGLINE)}">
<title>{esc(title)} · {esc(PRODUCT_NAME)} Documentation</title>
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{prefix}assets/styles.css?v={esc(ASSET_VERSION)}"></head>
<body><div class="site-shell"><aside class="sidebar">
<a class="brand" href="{prefix}index.html"><span class="brand-mark">{esc(initial)}</span>
<span class="brand-copy"><strong>{esc(PRODUCT_NAME)}</strong><span>{esc(PRODUCT_TAGLINE)}</span></span></a>
<nav class="documentation-nav" aria-label="Documentation">{nav_html(current, prefix)}</nav></aside>
<main class="main"><header class="topbar"><button class="menu-button" data-menu aria-label="Open navigation">☰</button>
<div class="topbar-title"><strong>{esc(PRODUCT_NAME)}</strong> / {esc(title)}</div>
<label class="search"><input data-spec-search type="search" placeholder="Filter this page…" aria-label="Filter this page"></label>
</header><article class="content">{content}
<footer class="footer">{esc(PRODUCT_NAME)} product and technical documentation · Generated from version-controlled sources.</footer>
</article></main></div><script src="{prefix}assets/specs.js?v={esc(ASSET_VERSION)}"></script></body></html>'''


def feature_cards() -> str:
    if not FEATURES:
        return '<p class="muted">Feature definitions have not been added yet.</p>'
    return '<div class="grid">' + "".join(
        '<section class="card feature-card" data-searchable>'
        f'<div class="card-kicker">{esc(feature["group"])}</div><h3>{esc(feature["name"])}</h3>'
        f'<p>{esc(feature["summary"])}</p><div class="meta-row"><span class="badge">{esc(feature["status"])}</span></div>'
        f'<a class="feature-link" href="features/{esc(feature["slug"])}.html">Explore feature →</a></section>'
        for feature in FEATURES
    ) + "</div>"


def decision_register() -> str:
    rows = [
        (
            decision["id"],
            decision["question"],
            decision["choice"],
            decision["rationale"],
            decision["consequences"],
            ", ".join(decision["affected"]),
            decision["confirmation"],
            decision["status"],
        )
        for decision in DECISIONS
    ]
    return '<h2 id="decision-register">Decision register</h2>' + table_html(
        (
            "Id",
            "Question",
            "Confirmed choice",
            "Rationale",
            "Consequences",
            "Affected contracts",
            "Confirmation",
            "Status",
        ),
        rows,
    )


def requirement_coverage() -> str:
    def links(destinations: list[str]) -> SafeHtml:
        return SafeHtml(
            " · ".join(f'<a href="{esc(destination)}">{esc(destination)}</a>' for destination in destinations)
        )

    rows = [
        (
            requirement["id"],
            requirement["source"],
            requirement["kind"],
            requirement["area"],
            requirement["text"],
            links(requirement["destinations"]),
            requirement["status"],
            requirement.get("notes", ""),
        )
        for requirement in REQUIREMENTS
    ]
    return '<h2 id="requirement-register">Requirement register</h2>' + table_html(
        ("Id", "Source", "Kind", "Area", "Requirement", "Rendered destinations", "Status", "Notes"), rows
    )


def aggregate_catalogs(filename: str) -> str:
    if filename == "data-dictionary.html":
        rows = []
        for feature in FEATURES:
            for record in LOW_LEVEL_DESIGN.get(feature["slug"], {}).get("records", []):
                rows.append((feature["name"], *record))
        return '<h2 id="record-catalog">Feature record catalog</h2>' + table_html(
            ("Feature", "Storage identity", "Code identity", "Fields", "Invariants/indexes"), rows
        )
    if filename == "permissions.html":
        rows = []
        for feature in FEATURES:
            for permission in feature.get("permissions", []):
                rows.append((feature["name"], *permission))
        return '<h2 id="permission-catalog">Feature permission catalog</h2>' + table_html(
            ("Feature", "Action/read", "Actor", "Scope and rule"), rows
        )
    if filename == "transport-contracts.html":
        rows = []
        for feature in FEATURES:
            for interface in LOW_LEVEL_DESIGN.get(feature["slug"], {}).get("interfaces", []):
                rows.append((feature["name"], *interface))
        return '<h2 id="interface-catalog">Feature interface catalog</h2>' + table_html(
            ("Feature", "Operation", "Input", "Success", "Failures/authority"), rows
        )
    if filename == "events-jobs.html":
        event_rows = []
        job_rows = []
        for feature in FEATURES:
            for event in EVENTS.get(feature["slug"], []):
                event_rows.append((feature["name"], *event))
            for job in LOW_LEVEL_DESIGN.get(feature["slug"], {}).get("jobs", []):
                job_rows.append((feature["name"], *job))
        return (
            '<h2 id="event-catalog">Event catalog</h2>'
            + table_html(("Feature", "Event/version", "Producer", "Payload", "Consumers/effect"), event_rows)
            + '<h2 id="job-catalog">Job and consumer catalog</h2>'
            + table_html(("Feature", "Signature", "Trigger", "Idempotency/terminal behavior"), job_rows)
        )
    if filename == "audit.html":
        rows = [
            (
                feature["name"],
                "documented" if feature["slug"] in SYSTEM_DESIGN else "missing",
                "documented" if feature["slug"] in LOW_LEVEL_DESIGN else "missing",
                len(ROUTES.get(feature["slug"], [])),
                len(EVENTS.get(feature["slug"], [])),
            )
            for feature in FEATURES
        ]
        return '<h2 id="feature-coverage">Feature architecture coverage</h2>' + table_html(
            ("Feature", "System design", "Low-level design", "Surfaces", "Events"), rows
        )
    return ""


def feature_page(feature: dict[str, object]) -> str:
    slug = str(feature["slug"])
    system = {**SYSTEM_FALLBACK, **SYSTEM_DESIGN.get(slug, {})}
    low = {**LOW_LEVEL_FALLBACK, **LOW_LEVEL_DESIGN.get(slug, {})}
    routes = ROUTES.get(slug, [])
    events = EVENTS.get(slug, [])
    missing_layers = [
        label
        for label, source in (
            ("high-level system design", SYSTEM_DESIGN),
            ("low-level code architecture", LOW_LEVEL_DESIGN),
            ("route or surface manifest", ROUTES),
            ("event or message manifest", EVENTS),
        )
        if slug not in source
    ]
    draft_notice = ""
    if missing_layers:
        draft_notice = (
            '<div class="callout danger" data-searchable><strong>Incomplete rough cut</strong>'
            f'Missing {esc(", ".join(missing_layers))}. The validator will reject this draft until those '
            "source manifests are authored.</div>"
        )
    content = f'''
<section class="hero" data-searchable><div class="eyebrow">{esc(feature["group"])} · {esc(feature["status"])}</div>
<h1>{esc(feature["name"])}</h1><p>{esc(feature["summary"])}</p></section>
{draft_notice}
<h2 id="why">Why this feature exists</h2><p>{esc(feature["why"])}</p>
<div class="grid"><section class="card span-6"><h3 id="goals">Goals</h3>{list_html(feature["goals"])}</section>
<section class="card span-6"><h3 id="non-goals">Non-goals</h3>{list_html(feature["non_goals"])}</section></div>
<h2 id="people">People and responsibilities</h2>{table_html(("Actor", "Need, authority, and responsibility"), feature["personas"])}
<h2 id="success">Success signals and guardrails</h2>{table_html(("Signal", "Meaning or target"), feature["success_metrics"])}
<h3 id="dependencies">Dependencies</h3>{list_html(feature["dependencies"])}
<h2 id="flows">End-to-end product flows</h2>{card_rows(feature["flows"])}
<h2 id="screens">Screens and experience</h2>{table_html(("Screen/surface", "Actor", "Content, actions, and states"), feature["screens"])}
<h2 id="states">State vocabulary</h2>{list_html(feature["states"], "state-list")}
<h2 id="models">Conceptual feature model</h2>{table_html(("Model/aggregate", "Product fields", "Ownership and constraints"), feature["models"])}
<h2 id="permissions">Feature permissions</h2>{table_html(("Action/read", "Actor", "Scope and rule"), feature["permissions"])}
<h2 id="rules">Product rules and invariants</h2>{list_html(feature["rules"], "checklist")}
<h2 id="edge-cases">Edge-case checklist</h2>{list_html(feature["edge_cases"])}
<h2 id="acceptance">Acceptance behavior</h2>{list_html(feature["acceptance"], "checklist")}
<h2 id="future">Future evolution and boundaries</h2><p>{esc(feature["future"])}</p>
<h2 id="system-design">High-level system design</h2><p>{esc(system["architecture"])}</p>
<h3 id="runtime-flow">Authoritative runtime execution</h3>{card_rows(system["runtime_flow"])}
<h3 id="interaction-flow">Interaction and presentation execution</h3>{card_rows(system["interaction_flow"])}
<h3 id="commands">Command catalog</h3>{table_html(("Command", "Actor", "Guards", "Writes and effects"), system["commands"])}
<h3 id="queries">Query catalog</h3>{table_html(("Query", "Scope", "Projection and behavior"), system["queries"])}
<h3 id="transitions">Authoritative state transitions</h3>{table_html(("Aggregate", "From", "Trigger/guard", "To", "Effects/invariants"), system["transitions"])}
<h3 id="contracts">Cross-feature and external contracts</h3>{table_html(("Contract", "Shape/input", "Consumer", "Boundary rule"), system["contracts"])}
<h3 id="reconciliations">Reconciliation register</h3>{table_html(("Statement or ambiguity", "Status", "Current meaning"), system["reconciliations"])}
<h3 id="tests">Feature-specific verification obligations</h3>{list_html(system["tests"], "checklist")}
<h2 id="implementation-manifest">Low-level code architecture</h2><p>These manifests fix ownership and contracts without reproducing implementation bodies.</p>
<h3 id="runtime-files">File and module ownership</h3>{table_html(("Path/module", "Owned responsibility"), low["files"])}
<h3 id="storage-schema">Exact persisted records</h3>{table_html(("Storage identity", "Code identity", "Fields/relationships", "Invariants/indexes"), low["records"])}
<h3 id="command-contracts">Command-service contracts</h3>{table_html(("Signature", "Transaction and behavior", "Stable failures"), low["commands"])}
<h3 id="query-contracts">Read/query contracts</h3>{table_html(("Signature", "Scope, projection, and performance"), low["queries"])}
<h3 id="interface-contracts">Transport and interface contracts</h3>{table_html(("Operation", "Input", "Success", "Failures/authority"), low["interfaces"])}
<h3 id="interaction-manifest">Interaction and presentation manifest</h3>{table_html(("Path/module", "Owned responsibility and states"), low["interaction_modules"])}
<h3 id="job-contracts">Job and consumer contracts</h3>{table_html(("Signature", "Trigger", "Idempotency and terminal behavior"), low["jobs"])}
<h3 id="migration-contracts">Migration and compatibility contracts</h3>{table_html(("Change or sequence", "Backfill, compatibility, rollback, and proof"), low["migrations"])}
<h3 id="telemetry-contracts">Telemetry and operational contracts</h3>{table_html(("Signal", "Attributes and privacy", "Operational use or response"), low["telemetry"])}
<h3 id="error-codes">Stable error vocabulary</h3>{list_html(low["errors"], "state-list")}
<h2 id="routes">Routes and surfaces</h2>{table_html(("Route/surface", "Owning file/module", "Screen contract", "Required states"), routes)}
<h2 id="events">Feature events</h2>{table_html(("Event/version", "Producer", "Payload", "Consumers/effect"), events)}
'''
    return shell(str(feature["name"]), f"features/{slug}.html", content, feature_page=True)


def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "features").mkdir(parents=True, exist_ok=True)
    expected_cross_pages = set(PAGES)
    expected_feature_pages = {f"{feature['slug']}.html" for feature in FEATURES}
    for stale_page in OUT.glob("*.html"):
        if stale_page.name not in expected_cross_pages:
            stale_page.unlink()
    for stale_page in (OUT / "features").glob("*.html"):
        if stale_page.name not in expected_feature_pages:
            stale_page.unlink()
    for filename, (title, base_content) in PAGES.items():
        content = base_content
        if filename == "index.html":
            content += f'<h2 id="feature-catalog">Product features</h2>{feature_cards()}'
        elif filename == "decisions.html":
            content += decision_register()
        elif filename == "coverage.html":
            content += requirement_coverage()
        content += aggregate_catalogs(filename)
        (OUT / filename).write_text(shell(title, filename, content))
    for feature in FEATURES:
        (OUT / "features" / f"{feature['slug']}.html").write_text(feature_page(feature))


if __name__ == "__main__":
    build()
