#!/usr/bin/env python3
"""Validate the generated specification system without third-party packages."""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from _events import EVENTS
from _features import FEATURES
from _low_level_design import LOW_LEVEL_DESIGN
from _manifest import FEATURE_GROUPS, PAGE_GROUPS, PRODUCT_NAME, PRODUCT_TAGLINE
from _pages import PAGES
from _requirements import DECISIONS, REQUIREMENTS
from _routes import ROUTES
from _system_design import SYSTEM_DESIGN


OUT = Path(__file__).resolve().parent
SOURCE_FILES = [
    "_manifest.py",
    "_requirements.py",
    "_pages.py",
    "_features.py",
    "_system_design.py",
    "_low_level_design.py",
    "_routes.py",
    "_events.py",
]

REQUIRED_FEATURE_KEYS = {
    "slug",
    "name",
    "group",
    "status",
    "summary",
    "why",
    "goals",
    "non_goals",
    "personas",
    "success_metrics",
    "dependencies",
    "flows",
    "screens",
    "states",
    "models",
    "permissions",
    "rules",
    "edge_cases",
    "acceptance",
    "future",
}
REQUIRED_SYSTEM_KEYS = {
    "architecture",
    "runtime_flow",
    "client_flow",
    "commands",
    "queries",
    "transitions",
    "contracts",
    "reconciliations",
    "tests",
}
REQUIRED_LOW_LEVEL_KEYS = {
    "files",
    "records",
    "commands",
    "queries",
    "interfaces",
    "clients",
    "jobs",
    "migrations",
    "telemetry",
    "errors",
}
REQUIRED_FEATURE_SECTIONS = {
    "why",
    "goals",
    "non-goals",
    "people",
    "success",
    "dependencies",
    "flows",
    "screens",
    "system-design",
    "backend-flow",
    "frontend-flow",
    "commands",
    "queries",
    "transitions",
    "contracts",
    "reconciliations",
    "tests",
    "implementation-manifest",
    "backend-files",
    "relational-schema",
    "service-contracts",
    "selector-contracts",
    "transport-contracts",
    "frontend-manifest",
    "job-contracts",
    "migration-contracts",
    "telemetry-contracts",
    "error-codes",
    "routes",
    "states",
    "models",
    "permissions",
    "rules",
    "events",
    "edge-cases",
    "acceptance",
    "future",
}
REQUIRED_CROSS_PAGE_IDS = {
    "index.html": {"product-promise", "audiences", "feature-map", "current-scope", "feature-catalog"},
    "product-flows.html": {"information-architecture", "actor-journeys", "cross-feature-flows", "global-experience-rules"},
    "decisions.html": {"decision-policy", "decision-register"},
    "roadmap.html": {"current-release", "extension-seams", "future-capabilities", "explicit-non-goals"},
    "system-architecture.html": {"system-context", "runtime-boundaries", "ownership", "execution-paths", "dependency-direction"},
    "repository-blueprint.html": {"runtime-baseline", "root-layout", "module-layouts", "dependency-rules", "verification-commands"},
    "backend.html": {"request-lifecycle", "domain-boundaries", "persistence", "asynchronous-work", "integrations", "configuration"},
    "frontend.html": {"route-ownership", "component-boundaries", "state-ownership", "forms-errors", "accessibility-responsive", "client-testing"},
    "domain-model.html": {"vocabulary", "aggregates", "relationships", "history-lifecycle"},
    "data-dictionary.html": {"data-conventions", "shared-records", "record-catalog"},
    "permissions.html": {"actors-capabilities", "scope-resolution", "denial-audit", "permission-catalog"},
    "transport-contracts.html": {"interface-conventions", "authentication-errors", "interface-catalog"},
    "events-jobs.html": {"event-envelope", "job-reliability", "event-catalog", "job-catalog"},
    "quality.html": {"test-matrix", "security", "privacy-retention", "observability", "performance", "migration-quality"},
    "implementation-sequence.html": {"dependency-graph", "vertical-sequence", "integration-gates"},
    "audit.html": {"authority-order", "audit-method", "known-boundaries", "feature-coverage"},
    "coverage.html": {"coverage-policy", "requirement-register"},
}
REQUIREMENT_KINDS = {"behavior", "architecture", "constraint", "quality", "exclusion", "decision"}
SAFE_LINK_SCHEMES = {"http", "https", "mailto", "tel"}


class DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.resources: list[str] = []
        self.unanchored_sections: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"] or "")
        if tag == "h2" and not values.get("id"):
            self.unanchored_sections.append(tag)
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"] or "")
        if tag == "link" and values.get("href"):
            self.resources.append(values["href"] or "")
        if tag in {"img", "script", "source"} and values.get("src"):
            self.resources.append(values["src"] or "")


def add(errors: list[str], message: str) -> None:
    errors.append(message)


def require_rows(
    errors: list[str],
    slug: str,
    label: str,
    rows: list[tuple[object, ...]],
    width: int,
    identity_columns: tuple[int, ...] = (0,),
) -> None:
    identities: list[tuple[str, ...]] = []
    for row in rows:
        if len(row) != width or not all(str(cell).strip() for cell in row):
            add(errors, f"{slug} has an incomplete {label} row: {row}")
        if len(row) == width:
            identities.append(tuple(str(row[index]) for index in identity_columns))
    if len(identities) != len(set(identities)):
        add(errors, f"{slug} has duplicate {label} identities")


def validate() -> list[str]:
    errors: list[str] = []
    if not PRODUCT_NAME.strip():
        add(errors, "Product name is empty")
    if not PRODUCT_TAGLINE.strip():
        add(errors, "Product tagline is empty")
    if not FEATURE_GROUPS or any(not str(group).strip() for group in FEATURE_GROUPS):
        add(errors, "Feature groups must contain at least one nonempty group")
    if len(FEATURE_GROUPS) != len(set(FEATURE_GROUPS)):
        add(errors, "Feature groups are not unique")

    page_group_files = {filename for _, items in PAGE_GROUPS for filename, _ in items}
    if page_group_files != set(PAGES):
        add(
            errors,
            f"Navigation/page sources differ: missing={sorted(page_group_files-set(PAGES))}, "
            f"extra={sorted(set(PAGES)-page_group_files)}",
        )

    for source_name in SOURCE_FILES:
        source = (OUT / source_name).read_text()
        if "TODO" in source:
            add(errors, f"{source_name} retains scaffold placeholders")

    slugs = [str(feature.get("slug", "")) for feature in FEATURES]
    if not slugs:
        add(errors, "At least one holistic feature must be documented")
    if len(slugs) != len(set(slugs)):
        add(errors, "Feature slugs are not unique")
    slug_set = set(slugs)
    if slug_set != set(SYSTEM_DESIGN) or slug_set != set(LOW_LEVEL_DESIGN) or slug_set != set(ROUTES) or slug_set != set(EVENTS):
        add(errors, "Feature slugs differ across product, system, low-level, route, and event manifests")

    for feature in FEATURES:
        slug = str(feature.get("slug", ""))
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            add(errors, f"Invalid feature slug: {slug}")
        missing_keys = REQUIRED_FEATURE_KEYS - set(feature)
        if missing_keys:
            add(errors, f"{slug} is missing product keys: {', '.join(sorted(missing_keys))}")
            continue
        if feature["group"] not in FEATURE_GROUPS:
            add(errors, f"{slug} uses unknown feature group: {feature['group']}")
        for key in REQUIRED_FEATURE_KEYS - {"slug"}:
            if not feature[key]:
                add(errors, f"{slug} has empty product content: {key}")
        require_rows(errors, slug, "persona", feature["personas"], 2)
        require_rows(errors, slug, "success metric", feature["success_metrics"], 2)
        require_rows(errors, slug, "flow", feature["flows"], 3)
        require_rows(errors, slug, "screen", feature["screens"], 3, (0, 1))
        require_rows(errors, slug, "conceptual model", feature["models"], 3)
        require_rows(errors, slug, "permission", feature["permissions"], 3, (0, 1))

        system = SYSTEM_DESIGN.get(slug, {})
        missing_system = REQUIRED_SYSTEM_KEYS - set(system)
        if missing_system:
            add(errors, f"{slug} is missing system-design keys: {', '.join(sorted(missing_system))}")
        else:
            for key in REQUIRED_SYSTEM_KEYS:
                if not system[key]:
                    add(errors, f"{slug} has empty system-design content: {key}")
            require_rows(errors, slug, "runtime flow", system["runtime_flow"], 3)
            require_rows(errors, slug, "client flow", system["client_flow"], 3, (0, 1))
            require_rows(errors, slug, "system command", system["commands"], 4)
            require_rows(errors, slug, "system query", system["queries"], 3)
            require_rows(errors, slug, "transition", system["transitions"], 5, (0, 1, 2))
            require_rows(errors, slug, "contract", system["contracts"], 4)
            require_rows(errors, slug, "reconciliation", system["reconciliations"], 3)

        low = LOW_LEVEL_DESIGN.get(slug, {})
        missing_low = REQUIRED_LOW_LEVEL_KEYS - set(low)
        if missing_low:
            add(errors, f"{slug} is missing low-level keys: {', '.join(sorted(missing_low))}")
        else:
            for key in REQUIRED_LOW_LEVEL_KEYS:
                if key not in {"clients", "jobs"} and not low[key]:
                    add(errors, f"{slug} has empty low-level content: {key}")
            require_rows(errors, slug, "file/module", low["files"], 2)
            require_rows(errors, slug, "record", low["records"], 4)
            require_rows(errors, slug, "low-level command", low["commands"], 3)
            require_rows(errors, slug, "low-level query", low["queries"], 2)
            require_rows(errors, slug, "interface", low["interfaces"], 4)
            require_rows(errors, slug, "client file", low["clients"], 2)
            require_rows(errors, slug, "job", low["jobs"], 3)
            require_rows(errors, slug, "migration", low["migrations"], 2)
            require_rows(errors, slug, "telemetry", low["telemetry"], 3)

        require_rows(errors, slug, "route/surface", ROUTES.get(slug, []), 4)
        require_rows(errors, slug, "event", EVENTS.get(slug, []), 4)

    if not REQUIREMENTS:
        add(errors, "Requirement coverage register is empty")
    requirement_ids: list[str] = []
    for requirement in REQUIREMENTS:
        required = {"id", "source", "text", "kind", "area", "destinations", "status", "notes"}
        if required - set(requirement):
            add(errors, f"Incomplete requirement row: {requirement}")
            continue
        requirement_ids.append(requirement["id"])
        if not re.fullmatch(r"REQ-[0-9]{3,}", str(requirement["id"])):
            add(errors, f"Invalid requirement id: {requirement['id']}")
        if any(not requirement.get(key) for key in {"id", "source", "text", "kind", "area", "status"}):
            add(errors, f"Requirement has empty required content: {requirement.get('id', requirement)}")
        if requirement["kind"] not in REQUIREMENT_KINDS:
            add(errors, f"Invalid requirement kind: {requirement['id']}={requirement['kind']}")
        if requirement["status"] == "pending":
            add(errors, f"Unresolved requirement: {requirement['id']}")
        if requirement["status"] not in {"covered", "superseded"}:
            add(errors, f"Invalid requirement status: {requirement['id']}={requirement['status']}")
        if not requirement["destinations"]:
            add(errors, f"Requirement has no rendered destination: {requirement['id']}")
    if len(requirement_ids) != len(set(requirement_ids)):
        add(errors, "Requirement ids are not unique")

    decision_ids: list[str] = []
    for decision in DECISIONS:
        required = {
            "id",
            "question",
            "choice",
            "rationale",
            "consequences",
            "affected",
            "confirmation",
            "status",
        }
        if required - set(decision) or not all(decision.get(key) for key in required):
            add(errors, f"Incomplete decision row: {decision}")
            continue
        decision_ids.append(decision["id"])
        if not re.fullmatch(r"DEC-[0-9]{3,}", str(decision["id"])):
            add(errors, f"Invalid decision id: {decision['id']}")
        if decision["status"] != "confirmed":
            add(errors, f"Unresolved decision: {decision['id']}")
    if len(decision_ids) != len(set(decision_ids)):
        add(errors, "Decision ids are not unique")

    cross_html = sorted(OUT.glob("*.html"))
    feature_html = sorted((OUT / "features").glob("*.html"))
    actual_cross = {path.name for path in cross_html}
    if actual_cross != set(PAGES):
        add(errors, f"Generated cross-page set differs: expected={sorted(PAGES)}, actual={sorted(actual_cross)}")
    actual_features = {path.stem for path in feature_html}
    if actual_features != slug_set:
        add(errors, f"Generated feature-page set differs: expected={sorted(slug_set)}, actual={sorted(actual_features)}")

    parsed: dict[Path, DocumentParser] = {}
    for path in cross_html + feature_html:
        source = path.read_text()
        if "TODO" in source:
            add(errors, f"{path.relative_to(OUT)} retains scaffold placeholders")
        parser = DocumentParser()
        parser.feed(source)
        parsed[path.resolve()] = parser
        duplicates = sorted({item for item in parser.ids if parser.ids.count(item) > 1})
        if duplicates:
            add(errors, f"{path.relative_to(OUT)} has duplicate ids: {', '.join(duplicates)}")
        if parser.unanchored_sections:
            add(errors, f"{path.relative_to(OUT)} has an h2 section without a stable id")

    for path in cross_html + feature_html:
        parser = parsed[path.resolve()]
        for href in parser.hrefs:
            parts = urlsplit(href)
            if parts.scheme:
                if parts.scheme not in SAFE_LINK_SCHEMES:
                    add(errors, f"{path.relative_to(OUT)} has unsafe link scheme: {href}")
                continue
            if parts.netloc:
                continue
            target = path.resolve() if not parts.path else (path.parent / parts.path).resolve()
            if not target.exists():
                add(errors, f"{path.relative_to(OUT)} has broken link: {href}")
            elif parts.fragment and target in parsed and parts.fragment not in parsed[target].ids:
                add(errors, f"{path.relative_to(OUT)} has broken anchor: {href}")
        for resource in parser.resources:
            parts = urlsplit(resource)
            if parts.scheme == "data":
                continue
            if parts.scheme or parts.netloc:
                add(errors, f"{path.relative_to(OUT)} depends on an external resource: {resource}")
                continue
            target = (path.parent / parts.path).resolve()
            if not target.exists():
                add(errors, f"{path.relative_to(OUT)} has missing local resource: {resource}")

    for filename, required_ids in REQUIRED_CROSS_PAGE_IDS.items():
        path = (OUT / filename).resolve()
        if path not in parsed:
            continue
        missing = required_ids - set(parsed[path].ids)
        if missing:
            add(errors, f"{filename} is missing sections: {', '.join(sorted(missing))}")
    for slug in slug_set:
        path = (OUT / "features" / f"{slug}.html").resolve()
        if path not in parsed:
            continue
        missing = REQUIRED_FEATURE_SECTIONS - set(parsed[path].ids)
        if missing:
            add(errors, f"{slug}.html is missing sections: {', '.join(sorted(missing))}")

    for requirement in REQUIREMENTS:
        if not requirement.get("destinations"):
            continue
        for destination in requirement["destinations"]:
            filename, separator, anchor = destination.partition("#")
            path = (OUT / filename).resolve()
            if path not in parsed:
                add(errors, f"{requirement['id']} points to missing page: {destination}")
            elif not separator or not anchor or anchor not in parsed[path].ids:
                add(errors, f"{requirement['id']} points to missing section: {destination}")
    return errors


if __name__ == "__main__":
    problems = validate()
    if problems:
        print("Specification validation failed:")
        for problem in problems:
            print(f"- {problem}")
        raise SystemExit(1)
    print(
        f"Specification validation passed: {len(FEATURES)} features, "
        f"{len(REQUIREMENTS)} requirements, and {len(list(OUT.rglob('*.html')))} HTML pages."
    )
