"""Load structured specification sources and render the static documentation shell."""

from __future__ import annotations

import html
import importlib.util
import posixpath
import re
from pathlib import Path
from typing import Any, Iterable

from _config import ASSET_VERSION, NAV_GROUP_ORDER, PRODUCT_NAME, PRODUCT_TAGLINE


ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = ROOT / "source"
ROUTE_RE = re.compile(r"(?:[a-z0-9]+(?:-[a-z0-9]+)*/)*[a-z0-9]+(?:-[a-z0-9]+)*\.html$")
ID_RE = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[\[([^\]|]+)\|([^\]]+)\]\]")


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
    for match in LINK_RE.finditer(value):
        parts.append(esc(value[position : match.start()]))
        label, target = match.groups()
        href = href_for(current_route, target.strip())
        external = target.startswith(("https://", "http://"))
        rel = ' rel="noreferrer"' if external else ""
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
        page = {**page, "_source": source_name}
        pages.append(page)
    return pages


def page_order(page: dict[str, Any]) -> tuple[int, int, str]:
    group = str(page.get("nav_group", "Reference"))
    try:
        group_order = NAV_GROUP_ORDER.index(group)
    except ValueError:
        group_order = len(NAV_GROUP_ORDER)
    return group_order, int(page.get("nav_order", 999)), str(page.get("title", ""))


def render_table(block: dict[str, Any], route: str) -> str:
    headers = block.get("headers", [])
    rows = block.get("rows", [])
    head = "".join(f"<th scope=\"col\">{inline(item, route)}</th>" for item in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{inline(cell, route)}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    caption = f'<caption>{inline(block["caption"], route)}</caption>' if block.get("caption") else ""
    block_id = f' id="{esc(block["id"])}"' if block.get("id") else ""
    return f'<div class="table-wrap"{block_id}><table>{caption}<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def render_sequence(items: Iterable[Any], route: str) -> str:
    rendered = []
    for index, item in enumerate(items, 1):
        if isinstance(item, dict):
            title = item.get("title", f"Step {index}")
            text = item.get("text", "")
        else:
            title = f"Step {index}"
            text = item
        rendered.append(
            f'<li><span class="step-number">{index}</span><div><strong>{inline(title, route)}</strong>'
            f'<p>{inline(text, route)}</p></div></li>'
        )
    return '<ol class="sequence">' + "".join(rendered) + "</ol>"


def render_developer_flow(block: dict[str, Any], route: str) -> str:
    flow = block.get("flow", {})
    flow_id = str(flow.get("id", "developer-flow"))
    facts = (
        ("Trigger", flow.get("trigger", "")),
        ("Authority", flow.get("authority", "")),
        ("Entry point", flow.get("entry_point", "")),
        ("Data effects", flow.get("data_effects", "")),
        ("Consistency", flow.get("transaction", "")),
        ("Handoff", flow.get("handoff", "")),
        ("Terminal outcome", flow.get("terminal", "")),
        ("Failure and recovery", flow.get("recovery", "")),
    )
    fact_html = "".join(
        f'<div><dt>{esc(label)}</dt><dd>{inline(value, route)}</dd></div>' for label, value in facts
    )
    return (
        f'<section class="flow-card" id="{esc(flow_id)}"><div class="flow-card-head"><span>Developer flow</span>'
        f'<h3>{inline(flow.get("title", flow_id), route)}</h3></div><dl class="flow-facts">{fact_html}</dl>'
        f'<h4>Chronological code path</h4>{render_sequence(flow.get("steps", []), route)}</section>'
    )


def render_block(block: dict[str, Any], route: str) -> str:
    kind = block.get("type")
    if kind == "paragraph":
        return f'<p>{inline(block.get("text", ""), route)}</p>'
    if kind == "callout":
        tone = block.get("tone", "note")
        title = block.get("title", "Note")
        return f'<aside class="callout {esc(tone)}"><strong>{inline(title, route)}</strong><p>{inline(block.get("text", ""), route)}</p></aside>'
    if kind in {"list", "ordered"}:
        tag = "ol" if kind == "ordered" else "ul"
        items = "".join(f"<li>{inline(item, route)}</li>" for item in block.get("items", []))
        return f"<{tag} class=\"contract-list\">{items}</{tag}>"
    if kind == "code":
        language = str(block.get("language", "text"))
        label = f'<div class="code-label">{inline(block["label"], route)}</div>' if block.get("label") else ""
        block_id = f' id="{esc(block["id"])}"' if block.get("id") else ""
        return f'<div class="code-block"{block_id}>{label}<pre><code class="language-{esc(language)}">{esc(block.get("code", ""))}</code></pre></div>'
    if kind == "table":
        return render_table(block, route)
    if kind == "sequence":
        return render_sequence(block.get("items", []), route)
    if kind == "cards":
        cards = "".join(
            f'<article class="card"><span class="card-kicker">{inline(item.get("kicker", ""), route)}</span>'
            f'<h3>{inline(item.get("title", ""), route)}</h3><p>{inline(item.get("text", ""), route)}</p></article>'
            for item in block.get("items", [])
        )
        return f'<div class="card-grid">{cards}</div>'
    if kind == "developer-flow":
        return render_developer_flow(block, route)
    raise ValueError(f"Unsupported specification block type: {kind}")


def render_sections(page: dict[str, Any]) -> str:
    route = str(page["route"])
    output = []
    for section in page.get("sections", []):
        blocks = "".join(render_block(block, route) for block in section.get("blocks", []))
        output.append(f'<section class="doc-section"><h2 id="{esc(section["id"])}">{inline(section["title"], route)}</h2>{blocks}</section>')
    return "".join(output)


def render_sidebar(pages: list[dict[str, Any]], current: dict[str, Any]) -> str:
    groups: dict[str, list[dict[str, Any]]] = {}
    for page in sorted(pages, key=page_order):
        groups.setdefault(str(page["nav_group"]), []).append(page)
    rendered = []
    current_route = str(current["route"])
    ordered_groups = sorted(groups, key=lambda group: NAV_GROUP_ORDER.index(group) if group in NAV_GROUP_ORDER else 999)
    for group in ordered_groups:
        items = groups[group]
        open_attr = " open" if current in items else ""
        links = []
        for page in items:
            active = ' aria-current="page"' if page is current else ""
            links.append(
                f'<li><a href="{esc(href_for(current_route, str(page["route"])))}"{active}>'
                f'<span class="nav-dot"></span>{esc(page["title"])}</a></li>'
            )
        rendered.append(f'<details class="nav-group"{open_attr}><summary>{esc(group)}</summary><ul>{"".join(links)}</ul></details>')
    return "".join(rendered)


def render_page(page: dict[str, Any], pages: list[dict[str, Any]]) -> str:
    ordered = sorted(pages, key=page_order)
    index = ordered.index(page)
    previous_page = ordered[index - 1] if index else None
    next_page = ordered[index + 1] if index + 1 < len(ordered) else None
    route = str(page["route"])
    current_dir = posixpath.dirname(route) or "."
    asset_css = posixpath.relpath("assets/styles.css", current_dir)
    asset_js = posixpath.relpath("assets/specs.js", current_dir)
    favicon = posixpath.relpath("assets/favicon.svg", current_dir)
    home = href_for(route, "index.html")
    toc = "".join(f'<li><a href="#{esc(section["id"])}">{esc(section["title"])}</a></li>' for section in page.get("sections", []))
    related = "".join(
        f'<li><a href="{esc(href_for(route, target))}">{esc(next(item["title"] for item in pages if item["route"] == target))}</a></li>'
        for target in page.get("related", [])
        if any(item["route"] == target for item in pages)
    )
    previous_html = (
        f'<a class="page-turn previous" href="{esc(href_for(route, str(previous_page["route"])))}"><span>Previous</span><strong>{esc(previous_page["title"])}</strong></a>'
        if previous_page else '<span class="page-turn empty"></span>'
    )
    next_html = (
        f'<a class="page-turn next" href="{esc(href_for(route, str(next_page["route"])))}"><span>Next</span><strong>{esc(next_page["title"])}</strong></a>'
        if next_page else '<span class="page-turn empty"></span>'
    )
    related_html = f'<section class="related"><h2>Related documentation</h2><ul>{related}</ul></section>' if related else ""
    initial = PRODUCT_NAME[:1].upper() or "P"
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{esc(page["summary"])}"><title>{esc(page["title"])} · {esc(PRODUCT_NAME)} specifications</title>
<link rel="icon" href="{esc(favicon)}" type="image/svg+xml"><link rel="stylesheet" href="{esc(asset_css)}?v={esc(ASSET_VERSION)}"></head>
<body data-page-kind="{esc(page["kind"])}"><div class="site-shell"><aside class="sidebar" data-sidebar>
<a class="brand" href="{esc(home)}"><span class="brand-mark">{esc(initial)}</span><span><strong>{esc(PRODUCT_NAME)}</strong><small>Product specifications</small></span></a>
<nav aria-label="Documentation">{render_sidebar(pages, page)}</nav></aside><main class="main"><header class="topbar">
<button class="icon-button menu-button" type="button" data-menu aria-label="Open documentation navigation">☰</button>
<div class="topbar-title">{esc(page["nav_group"])} / {esc(page["title"])}</div><button class="icon-button" type="button" data-theme aria-label="Toggle color theme">◐</button></header>
<div class="document-layout"><article class="article"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="{esc(home)}">Home</a><span>/</span><span>{esc(page["nav_group"])}</span><span>/</span><span aria-current="page">{esc(page["title"])}</span></nav>
<header class="document-header"><span class="eyebrow">{esc(page["kind"].replace("-", " "))}</span><h1>{esc(page["title"])}</h1><p>{inline(page["summary"], route)}</p></header>
{render_sections(page)}{related_html}<nav class="page-turns" aria-label="Page navigation">{previous_html}{next_html}</nav>
<footer class="footer">{esc(PRODUCT_NAME)} product and architecture authority · Generated from version-controlled sources.</footer></article>
<aside class="toc" aria-label="On this page"><strong>On this page</strong><ol>{toc}</ol></aside></div></main></div>
<div class="sidebar-scrim" data-scrim></div><script src="{esc(asset_js)}?v={esc(ASSET_VERSION)}"></script></body></html>'''
