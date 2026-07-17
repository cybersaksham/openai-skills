"""Load specification sources and render the canonical Stride documentation shell."""

from __future__ import annotations

import html
import importlib.util
import json
import posixpath
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from _config import (
    ASSET_VERSION,
    GENERATED_LABEL,
    NAV_GROUP_ORDER,
    NAV_SUBGROUP_ORDER,
    PRODUCT_NAME,
    PRODUCT_TAGLINE,
    SPEC_STATUS,
    SPEC_VERSION,
)


ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT / "source"
ROUTE_RE = re.compile(r"(?:[a-z0-9]+(?:-[a-z0-9]+)*/)*[a-z0-9]+(?:-[a-z0-9]+)*\.html$")
ID_RE = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
INLINE_RE = re.compile(r"\[\[([^\]|]+)\|([^\]]+)\]\]|`([^`]+)`")
LINK_RE = re.compile(r"\[\[([^\]|]+)\|([^\]]+)\]\]")

PAGE_KIND_LABELS = {
    "overview": "Orientation guide",
    "product-journey": "Product journey",
    "feature": "Feature guide",
    "architecture-flow": "System design",
    "runtime-module": "Backend application architecture",
    "client-runtime": "Frontend implementation contract",
    "reference": "Project reference",
    "decision-register": "Decision register",
    "coverage": "Coverage and conformance",
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def href_for(current_route: str, target: str) -> str:
    if target.startswith(("https://", "http://", "mailto:")):
        return target
    path, marker, anchor = target.partition("#")
    if not path:
        return f"#{anchor}" if marker else "#"
    current_dir = posixpath.dirname(current_route) or "."
    relative = posixpath.relpath(path, current_dir)
    return relative + (f"#{anchor}" if marker else "")


def inline(text: object, current_route: str) -> str:
    value = str(text)
    parts: list[str] = []
    position = 0
    for match in INLINE_RE.finditer(value):
        parts.append(esc(value[position : match.start()]))
        label, target, code = match.groups()
        if code is not None:
            parts.append(f"<code>{esc(code)}</code>")
        else:
            href = href_for(current_route, target.strip())
            rel = ' rel="noreferrer"' if target.startswith(("https://", "http://")) else ""
            parts.append(f'<a href="{esc(href)}"{rel}>{esc(label.strip())}</a>')
        position = match.end()
    parts.append(esc(value[position:]))
    return "".join(parts)


def load_pages(source_root: Path = SOURCE_ROOT) -> list[dict[str, Any]]:
    pages: list[dict[str, Any]] = []
    if not source_root.is_dir():
        return pages
    for index, path in enumerate(sorted(source_root.rglob("*.py"))):
        if path.name.startswith("__"):
            continue
        module_name = f"_spec_page_{index}_{path.stem.replace('-', '_')}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Cannot load specification source: {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not hasattr(module, "PAGE"):
            raise ValueError(f"Specification source has no PAGE object: {path}")
        page = module.PAGE
        if not isinstance(page, dict):
            raise TypeError(f"PAGE must be a dictionary: {path}")
        try:
            source_name = path.relative_to(ROOT).as_posix()
        except ValueError:
            source_name = path.as_posix()
        pages.append({**page, "_source": source_name})
    return pages


def _configured_order(value: str, configured: list[str]) -> int:
    try:
        return configured.index(value)
    except ValueError:
        return len(configured)


def page_order(page: dict[str, Any]) -> tuple[int, int, str, str, str, int, str]:
    group = str(page.get("nav_group", "Project reference"))
    subgroup = str(page.get("nav_subgroup", ""))
    subgroup_order = _configured_order(subgroup, NAV_SUBGROUP_ORDER.get(group, []))
    return (
        _configured_order(group, NAV_GROUP_ORDER),
        subgroup_order,
        subgroup,
        str(page.get("nav_parent", "")),
        str(page.get("nav_category", "")),
        int(page.get("nav_order", 999)),
        str(page.get("title", "")),
    )


def page_label(page: dict[str, Any]) -> str:
    return str(page.get("nav_label") or page.get("title") or "Untitled page")


def render_table(block: dict[str, Any], route: str) -> str:
    headers = block.get("headers", [])
    rows = block.get("rows", [])
    head = "".join(f'<th scope="col">{inline(item, route)}</th>' for item in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{inline(cell, route)}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    caption = f'<caption>{inline(block["caption"], route)}</caption>' if block.get("caption") else ""
    block_id = f' id="{esc(block["id"])}"' if block.get("id") else ""
    return f'<div class="table-wrap"{block_id}><table>{caption}<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def render_sequence(items: Iterable[Any], route: str, title: str = "Chronological sequence") -> str:
    rendered = []
    for index, item in enumerate(items, 1):
        if isinstance(item, dict):
            step_title = item.get("title", f"Step {index}")
            text = item.get("text") or item.get("behavior", "")
        else:
            step_title = f"Step {index}"
            text = item
        rendered.append(f'<li><p><strong>{inline(step_title, route)}.</strong> {inline(text, route)}</p></li>')
    return (
        '<div class="flow-journeys"><section class="flow-journey">'
        f'<div class="card-kicker">Ordered flow</div><h3>{inline(title, route)}</h3>'
        f'<ol>{"".join(rendered)}</ol></section></div>'
    )


def _explicit_value(value: object, route: str) -> str:
    if isinstance(value, dict):
        value = "; ".join(f"{key}: {_plain_value(child)}" for key, child in value.items())
    elif isinstance(value, (list, tuple)):
        value = "; ".join(_plain_value(item) for item in value)
    return inline(value, route)


def _plain_value(value: object) -> str:
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    if isinstance(value, (list, tuple)):
        return ", ".join(_plain_value(item) for item in value)
    return str(value)


def render_developer_flow(block: dict[str, Any], route: str) -> str:
    flow = block.get("flow", {})
    flow_id = str(flow.get("id", "developer-flow"))
    steps = []
    for index, step in enumerate(flow.get("steps", []), 1):
        if not isinstance(step, dict):
            steps.append(f'<li><p>{inline(step, route)}</p></li>')
            continue
        symbols = _plain_value(step.get("symbols", ""))
        reads = _plain_value(step.get("reads", ""))
        writes = _plain_value(step.get("writes", ""))
        steps.append(
            f'<li><p><strong>{inline(step.get("title", f"Step {index}"), route)}.</strong> '
            f'{inline(step.get("behavior", ""), route)}</p>'
            f'<p class="small"><strong>Symbols:</strong> {inline(symbols, route)} · '
            f'<strong>Reads:</strong> {inline(reads, route)} · <strong>Writes:</strong> {inline(writes, route)}</p></li>'
        )
    facts = (
        ("Trigger", flow.get("trigger", "")),
        ("Initiator", flow.get("initiator", "")),
        ("Authority", flow.get("authority", "")),
        ("Entry point", flow.get("entry_point", "")),
        ("Data effects", flow.get("data_effects", "")),
        ("Transaction and commit", flow.get("transaction", "")),
        ("After-commit handoff", flow.get("handoff", "")),
        ("Duplicate and concurrency", flow.get("duplicates_concurrency", "")),
        ("Observability", flow.get("observability", "")),
    )
    fact_rows = "".join(
        f'<tr><th scope="row">{esc(label)}</th><td>{_explicit_value(value, route)}</td></tr>'
        for label, value in facts
    )
    return (
        f'<section class="flow-journey developer-code-flow" id="{esc(flow_id)}">'
        '<div class="card-kicker">Developer code flow</div>'
        f'<h3>{inline(flow.get("title", flow_id), route)}</h3>'
        f'<div class="table-wrap"><table><tbody>{fact_rows}</tbody></table></div>'
        f'<h4>Chronological execution path</h4><ol>{"".join(steps)}</ol>'
        f'<div class="callout info"><strong>Terminal state</strong>{inline(flow.get("terminal", ""), route)}</div>'
        f'<div class="callout danger"><strong>Terminal failures</strong>{inline(flow.get("failures", ""), route)}</div>'
        f'<div class="callout warn"><strong>Retry and operator recovery</strong>{inline(flow.get("recovery", ""), route)}</div>'
        "</section>"
    )


def render_block(block: dict[str, Any], route: str) -> str:
    kind = block.get("type")
    if kind == "paragraph":
        return f'<p>{inline(block.get("text", ""), route)}</p>'
    if kind == "callout":
        tone = {"note": "", "warning": "warn", "danger": "danger", "success": "info"}.get(str(block.get("tone", "note")), "")
        return f'<div class="callout {esc(tone)}"><strong>{inline(block.get("title", "Note"), route)}</strong>{inline(block.get("text", ""), route)}</div>'
    if kind in {"list", "ordered"}:
        tag = "ol" if kind == "ordered" else "ul"
        css_class = "checklist" if block.get("style") == "checklist" else ""
        class_attr = f' class="{css_class}"' if css_class else ""
        items = "".join(f"<li>{inline(item, route)}</li>" for item in block.get("items", []))
        return f"<{tag}{class_attr}>{items}</{tag}>"
    if kind == "code":
        language = str(block.get("language", "text"))
        label = f'<div class="card-kicker">{inline(block["label"], route)}</div>' if block.get("label") else ""
        block_id = f' id="{esc(block["id"])}"' if block.get("id") else ""
        return f'<div class="schema-group"{block_id}>{label}<pre class="schema-code"><code class="language-{esc(language)}">{esc(block.get("code", ""))}</code></pre></div>'
    if kind == "table":
        return render_table(block, route)
    if kind == "sequence":
        return render_sequence(block.get("items", []), route, str(block.get("title", "Chronological sequence")))
    if kind == "cards":
        cards = "".join(
            '<article class="card span-4">'
            f'<span class="card-kicker">{inline(item.get("kicker", ""), route)}</span>'
            f'<h3>{inline(item.get("title", ""), route)}</h3><p>{inline(item.get("text", ""), route)}</p></article>'
            for item in block.get("items", [])
        )
        return f'<div class="grid">{cards}</div>'
    if kind == "developer-flow":
        return render_developer_flow(block, route)
    raise ValueError(f"Unsupported specification block type: {kind}")


def render_sections(page: dict[str, Any]) -> str:
    route = str(page["route"])
    output = []
    for section in page.get("sections", []):
        blocks = "".join(render_block(block, route) for block in section.get("blocks", []))
        output.append(
            f'<section class="doc-section"><h2 id="{esc(section["id"])}">'
            f'{inline(section["title"], route)}</h2>{blocks}</section>'
        )
    return "".join(output)


def render_contract_registry(page: dict[str, Any]) -> str:
    contracts = page.get("contracts", [])
    if not contracts:
        return ""
    route = str(page["route"])
    records = []
    for contract in contracts:
        details = []
        for key, value in contract.items():
            if key in {"kind", "id", "anchor"}:
                continue
            details.append(
                f'<div><dt>{esc(key.replace("_", " "))}</dt><dd>{_explicit_value(value, route)}</dd></div>'
            )
        records.append(
            '<details class="contract-record">'
            f'<summary><code>{esc(contract.get("kind", "contract"))}</code><span>{esc(contract.get("id", ""))}</span></summary>'
            f'<dl>{"".join(details)}</dl></details>'
        )
    return '<section class="doc-section"><h2 id="owned-contracts">Owned contract records</h2>' + "".join(records) + "</section>"


def _sidebar_links(pages: list[dict[str, Any]], current: dict[str, Any], route: str) -> str:
    items = ['<ul class="nav-list">']
    current_route = str(current["route"])
    for page in sorted(pages, key=page_order):
        active = ' aria-current="page"' if str(page["route"]) == current_route else ""
        items.append(
            f'<li><a href="{esc(href_for(route, str(page["route"])))}"{active}>{esc(page_label(page))}</a></li>'
        )
    items.append("</ul>")
    return "".join(items)


def _subgroup_order(group: str, subgroup: str) -> tuple[int, str]:
    return _configured_order(subgroup, NAV_SUBGROUP_ORDER.get(group, [])), subgroup


def _render_parent(parent: str, pages: list[dict[str, Any]], current: dict[str, Any], route: str) -> str:
    is_open = any(str(page["route"]) == str(current["route"]) for page in pages)
    direct = [page for page in pages if not page.get("nav_category")]
    categories: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for page in pages:
        if page.get("nav_category"):
            categories[str(page["nav_category"])].append(page)
    content = [_sidebar_links(direct, current, route) if direct else ""]
    for category, items in sorted(categories.items(), key=lambda item: min(int(page.get("nav_order", 999)) for page in item[1])):
        content.append(f'<div class="nav-caption">{esc(category)}</div>{_sidebar_links(items, current, route)}')
    return (
        f'<details class="nav-subgroup nav-feature"{" open" if is_open else ""}>'
        f'<summary>{esc(parent)}</summary><div class="nav-feature-pages">{"".join(content)}</div></details>'
    )


def _render_subgroup(group: str, subgroup: str, pages: list[dict[str, Any]], current: dict[str, Any], route: str) -> str:
    is_open = any(str(page["route"]) == str(current["route"]) for page in pages)
    direct = [page for page in pages if not page.get("nav_parent")]
    parents: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for page in pages:
        if page.get("nav_parent"):
            parents[str(page["nav_parent"])].append(page)
    content = [_sidebar_links(direct, current, route) if direct else ""]
    if parents:
        content.append('<div class="nav-feature-list">')
        for parent, items in sorted(parents.items(), key=lambda item: min(int(page.get("nav_order", 999)) for page in item[1])):
            content.append(_render_parent(parent, items, current, route))
        content.append("</div>")
    return (
        f'<details class="nav-subgroup"{" open" if is_open else ""}><summary>{esc(subgroup)}</summary>'
        f'{"".join(content)}</details>'
    )


def render_sidebar(pages: list[dict[str, Any]], current: dict[str, Any]) -> str:
    route = str(current["route"])
    sections = ['<nav class="documentation-nav" aria-label="Documentation">']
    by_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for page in pages:
        by_group[str(page.get("nav_group", "Project reference"))].append(page)
    for group in NAV_GROUP_ORDER:
        group_pages = by_group.get(group, [])
        if not group_pages:
            continue
        is_open = any(str(page["route"]) == route for page in group_pages)
        sections.append(f'<details class="nav-group"{" open" if is_open else ""}><summary>{esc(group)}</summary>')
        direct = [page for page in group_pages if not page.get("nav_subgroup")]
        if direct:
            sections.append(_sidebar_links(direct, current, route))
        subgroups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for page in group_pages:
            if page.get("nav_subgroup"):
                subgroups[str(page["nav_subgroup"])].append(page)
        if subgroups:
            sections.append('<div class="nav-subgroups">')
            for subgroup, items in sorted(subgroups.items(), key=lambda item: _subgroup_order(group, item[0])):
                sections.append(_render_subgroup(group, subgroup, items, current, route))
            sections.append("</div>")
        sections.append("</details>")
    sections.append("</nav>")
    return "".join(sections)


def page_kind(page: dict[str, Any]) -> str:
    if page.get("route") == "index.html":
        return "Documentation home"
    return PAGE_KIND_LABELS.get(str(page.get("kind")), "Project reference")


def breadcrumbs_html(page: dict[str, Any], pages: list[dict[str, Any]]) -> str:
    route = str(page["route"])
    if route == "index.html":
        crumbs = [("Documentation", None)]
    else:
        crumbs: list[tuple[str, str | None]] = [("Documentation", href_for(route, "index.html"))]
        labels = [str(page.get("nav_group", "")), str(page.get("nav_subgroup", "")), str(page.get("nav_parent", ""))]
        for label in (item for item in labels if item):
            owner = next(
                (
                    candidate
                    for candidate in sorted(pages, key=page_order)
                    if label in {
                        str(candidate.get("nav_group", "")),
                        str(candidate.get("nav_subgroup", "")),
                        str(candidate.get("nav_parent", "")),
                    }
                    and str(candidate["route"]) != route
                ),
                None,
            )
            crumbs.append((label, href_for(route, str(owner["route"])) if owner else None))
        crumbs.append((str(page["title"]), None))
    items = []
    for label, target in crumbs:
        if target:
            items.append(f'<li><a href="{esc(target)}">{esc(label)}</a></li>')
        else:
            items.append(f'<li><span>{esc(label)}</span></li>')
    return '<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>' + "".join(items) + "</ol></nav>"


def page_navigation_html(page: dict[str, Any], pages: list[dict[str, Any]]) -> str:
    ordered = sorted(pages, key=page_order)
    index = ordered.index(page)
    previous = ordered[index - 1] if index else None
    following = ordered[index + 1] if index + 1 < len(ordered) else None
    route = str(page["route"])
    links = []
    if previous:
        links.append(
            f'<a class="page-turn previous" rel="prev" href="{esc(href_for(route, str(previous["route"])))}">'
            f'<span>Previous</span><strong>{esc(page_label(previous))}</strong></a>'
        )
    else:
        links.append('<span class="page-turn placeholder"></span>')
    if following:
        links.append(
            f'<a class="page-turn next" rel="next" href="{esc(href_for(route, str(following["route"])))}">'
            f'<span>Next</span><strong>{esc(page_label(following))}</strong></a>'
        )
    return '<nav class="page-navigation" aria-label="Previous and next pages">' + "".join(links) + "</nav>"


def page_rail_html(page: dict[str, Any], content: str, pages: list[dict[str, Any]]) -> str:
    route = str(page["route"])
    headings = []
    for level, anchor, body in re.findall(r'<h([23])[^>]*\bid="([^"]+)"[^>]*>(.*?)</h\1>', content, flags=re.DOTALL):
        label = " ".join(re.sub(r"<[^>]+>", " ", html.unescape(body)).split())
        if label and len(headings) < 14:
            headings.append((level, anchor, label))
    output = ['<aside class="page-rail" aria-label="Page navigation">']
    if headings:
        output.append('<div class="rail-section"><div class="rail-title">On this page</div><ol class="page-toc">')
        output.extend(
            f'<li class="toc-level-{level}"><a href="#{esc(anchor)}">{esc(label)}</a></li>'
            for level, anchor, label in headings
        )
        output.append("</ol></div>")
    related_pages = [candidate for target in page.get("related", []) for candidate in pages if candidate.get("route") == target]
    if related_pages:
        output.append('<div class="rail-section"><div class="rail-title">Related pages</div><ul class="rail-links">')
        output.extend(
            f'<li><a href="{esc(href_for(route, str(candidate["route"])))}">{esc(page_label(candidate))}</a></li>'
            for candidate in related_pages[:5]
        )
        output.append("</ul></div>")
    status = "Authoritative" if SPEC_STATUS == "final" else "Draft"
    output.append(
        f'<div class="rail-status"><span>Specification</span><strong>{esc(SPEC_VERSION)} · {status}</strong>'
        f'<small>{esc(GENERATED_LABEL)}</small></div></aside>'
    )
    return "".join(output)


def render_page(page: dict[str, Any], pages: list[dict[str, Any]]) -> str:
    route = str(page["route"])
    current_dir = posixpath.dirname(route) or "."
    asset_css = posixpath.relpath("assets/styles.css", current_dir)
    asset_js = posixpath.relpath("assets/specs.js", current_dir)
    favicon = posixpath.relpath("assets/favicon.svg", current_dir)
    home = href_for(route, "index.html")
    coverage_page = next((candidate for candidate in pages if candidate.get("kind") == "coverage"), None)
    coverage_href = href_for(route, str(coverage_page["route"])) if coverage_page else home
    initial = PRODUCT_NAME[:1].upper() or "P"
    kind = page_kind(page)
    hero_class = "documentation-hero" if route == "index.html" else "doc-hero compact" if page.get("kind") == "overview" else "doc-hero"
    hero = (
        f'<header class="{hero_class}"><div class="eyebrow">{esc(kind)}</div><h1>{esc(page["title"])}</h1>'
        f'<p>{inline(page["summary"], route)}</p><div class="meta-row"><span class="badge">{esc(SPEC_VERSION)}</span>'
        f'<span class="badge info">{"Authoritative" if SPEC_STATUS == "final" else "Draft"}</span></div></header>'
    )
    content = hero + render_sections(page) + render_contract_registry(page)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{esc(page["summary"])}"><title>{esc(page["title"])} · {esc(PRODUCT_NAME)} Documentation</title>
<link rel="icon" href="{esc(favicon)}" type="image/svg+xml"><link rel="stylesheet" href="{esc(asset_css)}?v={esc(ASSET_VERSION)}"></head>
<body data-page-kind="{esc(page["kind"])}"><div class="site-shell"><div class="navigation-scrim" data-nav-close></div><aside class="sidebar"><div class="sidebar-header"><a class="brand" href="{esc(home)}"><span class="brand-mark">{esc(initial)}</span><span class="brand-copy"><strong>{esc(PRODUCT_NAME)}</strong><span>Product &amp; engineering</span></span></a><span class="version-pill">Specification {esc(SPEC_VERSION)}</span></div>{render_sidebar(pages, page)}<div class="sidebar-footer"><span>Authoritative product contract</span></div></aside>
<main class="main"><header class="topbar"><button class="menu-button" data-menu aria-label="Open navigation"><span></span><span></span><span></span></button><div class="topbar-title"><span>{esc(kind)}</span><strong>{esc(page["title"])}</strong></div><div class="topbar-actions"><a class="topbar-link" href="{esc(coverage_href)}">Coverage</a><button class="theme-toggle topbar-theme-toggle" type="button" data-theme-toggle aria-label="Toggle color theme">Theme</button></div></header>
<div class="documentation-layout"><article class="content">{breadcrumbs_html(page, pages)}{content}{page_navigation_html(page, pages)}<footer class="footer"><strong>{esc(PRODUCT_NAME)} product and architecture documentation</strong><span>Generated from version-controlled specification sources</span></footer></article>{page_rail_html(page, content, pages)}</div></main></div>
<script src="{esc(asset_js)}?v={esc(ASSET_VERSION)}"></script></body></html>'''
