#!/usr/bin/env python3
"""Generate all static HTML pages from structured source modules."""

from __future__ import annotations

from pathlib import Path

from _spec_core import ROOT, ROUTE_RE, load_pages, render_page


def build() -> None:
    pages = load_pages()
    routes = [str(page.get("route", "")) for page in pages]
    if not pages:
        raise ValueError("No specification source pages exist")
    if len(routes) != len(set(routes)):
        raise ValueError("Duplicate specification routes exist")
    for route in routes:
        if not ROUTE_RE.fullmatch(route):
            raise ValueError(f"Unsafe specification route: {route}")

    expected = set(routes)
    for output in sorted(ROOT.rglob("*.html")):
        relative = output.relative_to(ROOT).as_posix()
        if relative not in expected:
            output.unlink()

    for page in pages:
        output = ROOT / str(page["route"])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_page(page, pages), encoding="utf-8")


if __name__ == "__main__":
    build()
