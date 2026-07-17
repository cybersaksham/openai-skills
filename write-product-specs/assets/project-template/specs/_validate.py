#!/usr/bin/env python3
"""Validate source completeness, generated structure, links, identities, and shell policy."""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable

from _config import NAV_GROUP_ORDER, SCAFFOLD_CONTENT_REPLACED, SPEC_STATUS
from _spec_core import ID_RE, LINK_RE, ROOT, ROUTE_RE, load_pages


ALLOWED_KINDS = {
    "overview",
    "product-journey",
    "feature",
    "architecture-flow",
    "runtime-module",
    "client-runtime",
    "reference",
    "decision-register",
    "coverage",
}
ALLOWED_BLOCKS = {"paragraph", "callout", "list", "ordered", "code", "table", "sequence", "cards", "developer-flow"}
REQUIRED_SECTIONS = {
    "product-journey": {"outcome-scope", "actors-authority", "preconditions", "happy-path", "alternatives-denials", "durable-effects", "failure-recovery", "acceptance", "related-contracts"},
    "feature": {"outcome-scope", "actors-authority", "product-flows", "states-effects", "permissions", "failure-recovery", "acceptance", "related-contracts"},
    "architecture-flow": {"purpose-scope", "components-ownership", "trigger-inputs", "chronological-sequence", "transactions-consistency", "durable-writes", "contracts", "idempotency-concurrency", "failure-reconciliation", "security-audit", "observability-operations", "acceptance"},
    "runtime-module": {"responsibility-boundary", "developer-code-flows", "data-schemas", "runtime-handoffs", "exact-catalogs", "related-designs"},
    "client-runtime": {"scope-ownership", "routes-surfaces", "state-owners", "interface-authority", "interaction-states", "accessibility", "failure-recovery", "evidence"},
    "decision-register": {"decision-register"},
    "coverage": {"requirement-coverage", "contract-coverage"},
}
DEVELOPER_FLOW_FIELDS = {"id", "title", "trigger", "authority", "entry_point", "steps", "data_effects", "transaction", "handoff", "terminal", "recovery"}
CONTRACT_KINDS = {
    "requirement",
    "decision",
    "product-flow",
    "architecture-flow",
    "runtime-module",
    "developer-flow",
    "data-schema",
    "input-schema",
    "output-schema",
    "api-operation",
    "route",
    "state-transition",
    "event",
    "event-schema",
    "job",
    "job-schema",
    "provider",
    "provider-schema",
    "permission",
    "scenario",
    "migration",
    "client-surface",
}
SEALED_SCHEMA_KINDS = {"input-schema", "output-schema", "event-schema", "job-schema", "provider-schema"}
REF_REQUIRED_KINDS = {"api-operation", "event", "job", "provider"}
PAGE_OWNER_CONTRACT = {
    "product-journey": "product-flow",
    "feature": "product-flow",
    "architecture-flow": "architecture-flow",
    "runtime-module": "runtime-module",
    "client-runtime": "client-surface",
}
REQUIRED_REF_KINDS = {
    "api-operation": {"input-schema", "output-schema"},
    "event": {"event-schema"},
    "job": {"job-schema"},
    "provider": {"provider-schema"},
}
FORBIDDEN_SOURCE = re.compile(r"\b(?:TODO|TBD|FIXME)\b|\.{3}|standard behavior|as above|normal errors|etc\.", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate generated product specifications")
    parser.add_argument("--json", action="store_true", help="Emit a JSON result")
    parser.add_argument("--allow-draft", action="store_true", help="Permit SPEC_STATUS=draft and pending decisions")
    return parser.parse_args()


def all_values(value: Any) -> Iterable[Any]:
    if isinstance(value, dict):
        for child in value.values():
            yield from all_values(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from all_values(child)
    else:
        yield value


def all_blocks(page: dict[str, Any]) -> Iterable[dict[str, Any]]:
    for section in page.get("sections", []):
        for block in section.get("blocks", []):
            if isinstance(block, dict):
                yield block


class DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.duplicate_ids: set[str] = set()
        self.hrefs: list[str] = []
        self.inputs = 0
        self.h1 = 0
        self.aria_current = 0
        self.external_assets: list[str] = []
        self.forbidden_classes: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        element_id = values.get("id")
        if element_id:
            if element_id in self.ids:
                self.duplicate_ids.add(element_id)
            self.ids.add(element_id)
        href = values.get("href")
        if href:
            self.hrefs.append(href)
        if tag == "input":
            self.inputs += 1
        if tag == "h1":
            self.h1 += 1
        if tag == "a" and values.get("aria-current") == "page":
            self.aria_current += 1
        class_names = set((values.get("class") or "").split())
        self.forbidden_classes.update(class_names & {"feature-tabs", "subtabs", "search", "filter-bar"})
        asset = values.get("src") if tag == "script" else href if tag == "link" else None
        if asset and asset.startswith(("https://", "http://", "//")):
            self.external_assets.append(asset)


def validate_block(block: dict[str, Any], location: str, errors: list[str], metrics: Counter[str]) -> None:
    kind = block.get("type")
    if kind not in ALLOWED_BLOCKS:
        errors.append(f"{location}: unsupported block type {kind!r}")
        return
    metrics[f"block_{kind}"] += 1
    if kind in {"list", "ordered", "sequence"} and not block.get("items"):
        errors.append(f"{location}: {kind} block must contain items")
    if kind == "table":
        headers = block.get("headers")
        rows = block.get("rows")
        if not isinstance(headers, list) or not headers:
            errors.append(f"{location}: table requires headers")
        if not isinstance(rows, list) or not rows:
            errors.append(f"{location}: table requires rows")
        elif isinstance(headers, list):
            for row_index, row in enumerate(rows):
                if not isinstance(row, (list, tuple)) or len(row) != len(headers):
                    errors.append(f"{location}: table row {row_index + 1} does not match header width")
    if kind == "code":
        if not str(block.get("code", "")).strip():
            errors.append(f"{location}: code block must not be empty")
        contract_kind = block.get("contract_kind")
        if contract_kind:
            metrics[f"schema_{contract_kind}"] += 1
            if contract_kind not in {"data-schema", *SEALED_SCHEMA_KINDS}:
                errors.append(f"{location}: unsupported schema contract_kind {contract_kind!r}")
            if not block.get("contract_id"):
                errors.append(f"{location}: contract code block requires contract_id")
            if contract_kind in SEALED_SCHEMA_KINDS and block.get("sealed") is not True:
                errors.append(f"{location}: public payload schema {block.get('contract_id')} must set sealed=True")
    if kind == "cards" and not block.get("items"):
        errors.append(f"{location}: cards block must contain items")
    if kind == "developer-flow":
        metrics["developer_code_flows"] += 1
        flow = block.get("flow")
        if not isinstance(flow, dict):
            errors.append(f"{location}: developer-flow requires a flow dictionary")
            return
        missing = sorted(DEVELOPER_FLOW_FIELDS - set(flow))
        if missing:
            errors.append(f"{location}: developer flow is missing {', '.join(missing)}")
        if not isinstance(flow.get("steps"), list) or len(flow.get("steps", [])) < 2:
            errors.append(f"{location}: developer flow must contain at least two chronological steps")
        if flow.get("id") and not ID_RE.fullmatch(str(flow["id"])):
            errors.append(f"{location}: unsafe developer flow id {flow['id']!r}")


def validate_sources(pages: list[dict[str, Any]], allow_draft: bool) -> tuple[list[str], Counter[str]]:
    errors: list[str] = []
    metrics: Counter[str] = Counter()
    routes: set[str] = set()
    global_contracts: dict[str, tuple[str, dict[str, Any]]] = {}
    pending_decisions = 0
    pending_requirements = 0

    if SPEC_STATUS not in {"draft", "final"}:
        errors.append(f"SPEC_STATUS must be 'draft' or 'final', found {SPEC_STATUS!r}")
    if SPEC_STATUS != "final" and not allow_draft:
        errors.append("SPEC_STATUS is not final")
    if not SCAFFOLD_CONTENT_REPLACED and not allow_draft:
        errors.append("SCAFFOLD_CONTENT_REPLACED is false")

    for page in pages:
        source = str(page.get("_source", "unknown source"))
        required = {"route", "nav_group", "nav_order", "title", "summary", "kind", "sections", "related", "contracts", "requirements", "decisions"}
        missing = sorted(required - set(page))
        if missing:
            errors.append(f"{source}: PAGE is missing {', '.join(missing)}")
            continue
        route = str(page["route"])
        if not ROUTE_RE.fullmatch(route):
            errors.append(f"{source}: unsafe route {route!r}")
        if route in routes:
            errors.append(f"{source}: duplicate route {route}")
        routes.add(route)
        kind = str(page["kind"])
        metrics["html_pages"] += 1
        metrics[f"page_kind_{kind}"] += 1
        if kind not in ALLOWED_KINDS:
            errors.append(f"{source}: unsupported page kind {kind!r}")
        if page["nav_group"] not in NAV_GROUP_ORDER:
            errors.append(f"{source}: nav_group {page['nav_group']!r} is absent from NAV_GROUP_ORDER")
        if not str(page["title"]).strip() or not str(page["summary"]).strip():
            errors.append(f"{source}: title and summary must be non-empty")

        section_ids: set[str] = set()
        block_ids: set[str] = set()
        flow_ids: set[str] = set()
        schema_contracts: list[tuple[str, str, str]] = []
        sections = page.get("sections")
        if not isinstance(sections, list) or not sections:
            errors.append(f"{source}: sections must be a non-empty list")
            sections = []
        for section_index, section in enumerate(sections):
            location = f"{source}: section {section_index + 1}"
            if not isinstance(section, dict) or not {"id", "title", "blocks"}.issubset(section):
                errors.append(f"{location}: section requires id, title, and blocks")
                continue
            section_id = str(section["id"])
            if not ID_RE.fullmatch(section_id):
                errors.append(f"{location}: unsafe section id {section_id!r}")
            if section_id in section_ids | block_ids | flow_ids:
                errors.append(f"{location}: duplicate page anchor {section_id}")
            section_ids.add(section_id)
            if not isinstance(section["blocks"], list) or not section["blocks"]:
                errors.append(f"{location}: blocks must be a non-empty list")
                continue
            for block_index, block in enumerate(section["blocks"]):
                if not isinstance(block, dict):
                    errors.append(f"{location}: block {block_index + 1} must be a dictionary")
                    continue
                validate_block(block, f"{location}, block {block_index + 1}", errors, metrics)
                if block.get("id"):
                    block_id = str(block["id"])
                    if block.get("type") not in {"code", "table"}:
                        errors.append(f"{location}: only code and table blocks may define an id")
                    if not ID_RE.fullmatch(block_id):
                        errors.append(f"{location}: unsafe block id {block_id!r}")
                    if block_id in section_ids | block_ids | flow_ids:
                        errors.append(f"{location}: duplicate page anchor {block_id}")
                    block_ids.add(block_id)
                if block.get("type") == "developer-flow" and isinstance(block.get("flow"), dict):
                    flow_id = str(block["flow"].get("id", ""))
                    if flow_id in section_ids | block_ids | flow_ids:
                        errors.append(f"{location}: duplicate page anchor {flow_id}")
                    flow_ids.add(flow_id)
                if block.get("type") == "code" and block.get("contract_kind"):
                    schema_contracts.append((str(block["contract_kind"]), str(block.get("contract_id", "")), str(block.get("id", ""))))

        missing_sections = REQUIRED_SECTIONS.get(kind, set()) - section_ids
        if missing_sections:
            errors.append(f"{source}: {kind} page is missing sections {', '.join(sorted(missing_sections))}")
        if kind == "runtime-module" and not flow_ids:
            errors.append(f"{source}: runtime-module page has no developer code flows")

        for related in page.get("related", []):
            if not isinstance(related, str):
                errors.append(f"{source}: related routes must be strings")

        page_contract_ids: set[str] = set()
        for contract in page.get("contracts", []):
            if not isinstance(contract, dict) or not {"kind", "id", "anchor"}.issubset(contract):
                errors.append(f"{source}: each contract requires kind, id, and anchor")
                continue
            contract_kind = str(contract["kind"])
            contract_id = str(contract["id"])
            anchor = str(contract["anchor"])
            if contract_kind not in CONTRACT_KINDS:
                errors.append(f"{source}: unsupported contract kind {contract_kind!r}")
            if not contract_id.strip():
                errors.append(f"{source}: contract id must not be empty")
            if contract_id in global_contracts:
                errors.append(f"{source}: duplicate global contract id {contract_id}")
            global_contracts[contract_id] = (source, contract)
            page_contract_ids.add(contract_id)
            if anchor not in section_ids | block_ids | flow_ids:
                errors.append(f"{source}: contract {contract_id} points to missing anchor #{anchor}")
            refs = contract.get("refs", [])
            if contract_kind in REF_REQUIRED_KINDS and not refs:
                errors.append(f"{source}: {contract_kind} {contract_id} must reference its sealed schema contract(s)")
            if refs and not isinstance(refs, list):
                errors.append(f"{source}: contract refs for {contract_id} must be a list")
            metrics[f"contract_{contract_kind}"] += 1

        for flow_id in flow_ids:
            matching = [item for item in page.get("contracts", []) if item.get("kind") == "developer-flow" and item.get("id") == flow_id]
            if len(matching) != 1:
                errors.append(f"{source}: developer flow {flow_id} requires exactly one matching developer-flow contract entry")

        for schema_kind, schema_id, block_id in schema_contracts:
            matching = [item for item in page.get("contracts", []) if item.get("kind") == schema_kind and item.get("id") == schema_id]
            if len(matching) != 1:
                errors.append(f"{source}: schema {schema_id} requires exactly one matching {schema_kind} contract entry")
            elif not block_id or matching[0].get("anchor") != block_id:
                errors.append(f"{source}: schema {schema_id} contract must point to its exact code-block id")

        owner_contract = PAGE_OWNER_CONTRACT.get(kind)
        if owner_contract and not any(item.get("kind") == owner_contract for item in page.get("contracts", [])):
            errors.append(f"{source}: {kind} page requires an owning {owner_contract} contract")
        if kind in {"product-journey", "feature", "architecture-flow", "runtime-module", "client-runtime"} and not any(
            item.get("kind") == "scenario" for item in page.get("contracts", [])
        ):
            errors.append(f"{source}: {kind} page requires at least one stable scenario contract")

        for decision in page.get("decisions", []):
            decision_fields = {"id", "question", "status", "choice", "rationale", "confirmation", "consequences", "destinations"}
            if not isinstance(decision, dict) or not decision_fields.issubset(decision):
                errors.append(f"{source}: each decision requires {', '.join(sorted(decision_fields))}")
                continue
            metrics["decisions"] += 1
            if decision["status"] == "pending":
                pending_decisions += 1
            elif decision["status"] not in {"confirmed", "superseded", "excluded"}:
                errors.append(f"{source}: unsupported decision status {decision['status']!r}")
        if page.get("decisions") and kind != "decision-register":
            errors.append(f"{source}: decisions must be owned by the decision-register page")

        for requirement in page.get("requirements", []):
            requirement_fields = {"id", "text", "status", "destinations", "source"}
            if not isinstance(requirement, dict) or not requirement_fields.issubset(requirement):
                errors.append(f"{source}: each requirement requires {', '.join(sorted(requirement_fields))}")
                continue
            metrics["requirements"] += 1
            if requirement["status"] == "pending":
                pending_requirements += 1
            elif requirement["status"] not in {"confirmed", "superseded", "excluded"}:
                errors.append(f"{source}: unsupported requirement status {requirement['status']!r}")
        if page.get("requirements") and kind != "coverage":
            errors.append(f"{source}: requirements must be owned by the coverage page")

        source_text = "\n".join(str(value) for value in all_values(page) if isinstance(value, str))
        matches = FORBIDDEN_SOURCE.findall(source_text)
        metrics["forbidden_contract_phrases"] += len(matches)
        if matches:
            errors.append(f"{source}: forbidden placeholder or ambiguous contract phrase found: {matches[0]!r}")

    anchor_map: dict[str, set[str]] = {}
    for page in pages:
        anchors = {str(section.get("id")) for section in page.get("sections", []) if isinstance(section, dict)}
        anchors.update(str(block.get("id")) for block in all_blocks(page) if block.get("id"))
        anchors.update(str(block.get("flow", {}).get("id")) for block in all_blocks(page) if block.get("type") == "developer-flow")
        anchor_map[str(page["route"])] = anchors

    for page in pages:
        source = str(page.get("_source", "unknown source"))
        for related in page.get("related", []):
            if related not in routes:
                errors.append(f"{source}: related route does not exist: {related}")
        for value in all_values(page):
            if not isinstance(value, str):
                continue
            for match in LINK_RE.finditer(value):
                target = match.group(2).strip()
                if target.startswith(("https://", "http://", "mailto:", "#")):
                    continue
                target_route = target.partition("#")[0]
                if target_route and target_route not in routes:
                    errors.append(f"{source}: inline link target does not exist: {target}")
        for register_kind in ("requirements", "decisions"):
            for item in page.get(register_kind, []):
                for destination in item.get("destinations", []):
                    target_route, marker, anchor = str(destination).partition("#")
                    if target_route not in routes:
                        errors.append(f"{source}: {register_kind[:-1]} {item.get('id')} destination route is missing: {destination}")
                    elif not marker or anchor not in anchor_map.get(target_route, set()):
                        errors.append(f"{source}: {register_kind[:-1]} {item.get('id')} destination anchor is missing: {destination}")

    for contract_id, (source, contract) in global_contracts.items():
        for reference in contract.get("refs", []):
            if reference not in global_contracts:
                errors.append(f"{source}: contract {contract_id} references missing contract {reference}")
        required_ref_kinds = REQUIRED_REF_KINDS.get(str(contract.get("kind")), set())
        actual_ref_kinds = {
            str(global_contracts[reference][1].get("kind"))
            for reference in contract.get("refs", [])
            if reference in global_contracts
        }
        missing_ref_kinds = required_ref_kinds - actual_ref_kinds
        if missing_ref_kinds:
            errors.append(f"{source}: contract {contract_id} is missing schema refs of kind {', '.join(sorted(missing_ref_kinds))}")
    metrics["pending_decisions"] = pending_decisions
    metrics["pending_requirements"] = pending_requirements
    if not allow_draft and (pending_decisions or pending_requirements):
        errors.append(f"Final specifications contain {pending_decisions} pending decisions and {pending_requirements} pending requirements")
    if not allow_draft:
        for required_kind in ("product-journey", "architecture-flow", "runtime-module"):
            if metrics[f"page_kind_{required_kind}"] == 0:
                errors.append(f"Final specifications require at least one {required_kind} page")
        for required_contract in ("product-flow", "architecture-flow", "runtime-module", "developer-flow", "scenario"):
            if metrics[f"contract_{required_contract}"] == 0:
                errors.append(f"Final specifications require at least one {required_contract} contract")
        if metrics["requirements"] == 0:
            errors.append("Final specifications require traceable requirements")
    return errors, metrics


def validate_generated(pages: list[dict[str, Any]], metrics: Counter[str]) -> list[str]:
    errors: list[str] = []
    parsers: dict[str, DocumentParser] = {}
    for page in pages:
        route = str(page["route"])
        path = ROOT / route
        if not path.is_file():
            errors.append(f"Generated page is missing: {route}")
            continue
        generated_text = path.read_text(encoding="utf-8")
        parser = DocumentParser()
        parser.feed(generated_text)
        parsers[route] = parser
        if parser.duplicate_ids:
            errors.append(f"{route}: duplicate HTML ids {', '.join(sorted(parser.duplicate_ids))}")
        if parser.inputs:
            errors.append(f"{route}: generated page contains input elements")
        if parser.h1 != 1:
            errors.append(f"{route}: expected exactly one h1, found {parser.h1}")
        if parser.aria_current != 1:
            errors.append(f"{route}: expected exactly one aria-current page link, found {parser.aria_current}")
        if parser.external_assets:
            errors.append(f"{route}: external runtime assets are forbidden: {parser.external_assets[0]}")
        if parser.forbidden_classes:
            errors.append(f"{route}: forbidden navigation classes {', '.join(sorted(parser.forbidden_classes))}")
        metrics["pages_with_input_elements"] += int(bool(parser.inputs))
        metrics["pages_with_forbidden_navigation"] += int(bool(parser.forbidden_classes))
        metrics["pages_with_shell_failures"] += int(parser.h1 != 1 or parser.aria_current != 1)
        for register_kind in ("requirements", "decisions"):
            for item in page.get(register_kind, []):
                if str(item.get("id", "")) not in generated_text:
                    errors.append(f"{route}: {register_kind[:-1]} {item.get('id')} is not rendered on its owning page")

    for route, parser in parsers.items():
        base = posixpath.dirname(route) or "."
        for raw_href in parser.hrefs:
            href = raw_href.split("?", 1)[0]
            if href.startswith(("https://", "http://", "mailto:")):
                continue
            path_part, marker, anchor = href.partition("#")
            target_route = route if not path_part else posixpath.normpath(posixpath.join(base, path_part))
            if target_route.startswith("../"):
                errors.append(f"{route}: link escapes .specs: {raw_href}")
                continue
            target_path = ROOT / target_route
            if not target_path.exists():
                errors.append(f"{route}: broken relative link {raw_href}")
                continue
            if marker and target_route.endswith(".html"):
                target_parser = parsers.get(target_route)
                if target_parser is None or anchor not in target_parser.ids:
                    errors.append(f"{route}: missing target anchor {raw_href}")
    metrics["broken_relative_links"] = sum("broken relative link" in error or "missing target anchor" in error for error in errors)
    return errors


def main() -> int:
    args = parse_args()
    try:
        pages = load_pages()
    except Exception as exc:  # loader failures must be reported as validation evidence
        payload = {"passed": False, "spec_status": SPEC_STATUS, "errors": [f"Source loading failed: {exc}"], "metrics": {}}
        print(json.dumps(payload, indent=2) if args.json else payload["errors"][0])
        return 1
    source_errors, metrics = validate_sources(pages, args.allow_draft)
    generated_errors = validate_generated(pages, metrics)
    errors = source_errors + generated_errors
    payload = {"passed": not errors, "spec_status": SPEC_STATUS, "errors": errors, "metrics": dict(sorted(metrics.items()))}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif errors:
        print("Specification validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print(f"Specification validation passed: {metrics['html_pages']} HTML pages.")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
