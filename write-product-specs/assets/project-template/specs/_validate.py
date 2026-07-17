#!/usr/bin/env python3
"""Validate source completeness, generated structure, links, identities, and shell policy."""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable

from _config import NAV_GROUP_ORDER, NAV_SUBGROUP_ORDER, SCAFFOLD_CONTENT_REPLACED, SPEC_STATUS
from _inventory import (
    ARCHITECTURE_FLOW_INVENTORY,
    CLIENT_SURFACE_INVENTORY,
    CLIENT_SURFACES_NOT_APPLICABLE_REASON,
    FEATURE_INVENTORY,
    PRODUCT_JOURNEY_INVENTORY,
    RUNTIME_COMMON_NOT_APPLICABLE_REASON,
    RUNTIME_DISCOVERY_EXCLUSIONS,
    RUNTIME_DISCOVERY_ROOTS,
    RUNTIME_MODULE_INVENTORY,
    RUNTIME_SETTINGS_NOT_APPLICABLE_REASON,
)
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
    "product-journey": {"outcome-scope", "actors-authority", "preconditions", "happy-path", "alternatives-denials", "states-effects", "handoffs", "notifications-audit", "failure-recovery", "client-behavior", "acceptance", "related-contracts"},
    "feature": {"outcome-scope", "actors-authority", "product-flows", "states-effects", "permissions", "failure-recovery", "acceptance", "related-contracts"},
    "architecture-flow": {"purpose-scope", "components-ownership", "trigger-inputs", "chronological-sequence", "transactions-consistency", "durable-writes", "contracts", "idempotency-concurrency", "timeouts-retries", "failure-reconciliation", "security-audit", "observability-operations", "acceptance", "dependent-journeys"},
    "runtime-module": {"responsibility-boundary", "developer-code-flow-directory", "model-schema", "product-runtime-handoffs", "commands-queries", "api-security", "events-jobs-recovery", "transitions-acceptance", "related-designs"},
    "client-runtime": {"scope-ownership", "routes-surfaces", "state-owners", "interface-authority", "interaction-states", "accessibility", "failure-recovery", "evidence"},
    "decision-register": {"decision-register"},
    "coverage": {"requirement-coverage", "contract-coverage"},
}
DEVELOPER_FLOW_FIELDS = {
    "id",
    "title",
    "trigger",
    "initiator",
    "authority",
    "entry_point",
    "steps",
    "data_effects",
    "transaction",
    "handoff",
    "duplicates_concurrency",
    "terminal",
    "failures",
    "observability",
    "recovery",
}
DEVELOPER_STEP_FIELDS = {"title", "symbols", "reads", "writes", "behavior"}
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
AMBIGUOUS_FOCUSED_TITLE = re.compile(r"^(?:backend architecture|integrations|other flows|technical details|feature behavior|runtime modules?)$", re.IGNORECASE)

CONTRACT_REQUIRED_FIELDS = {
    "product-flow": {"actors", "preconditions", "terminal", "alternatives", "scenario_ids"},
    "architecture-flow": {"trigger", "inputs", "terminal", "failures", "scenario_ids"},
    "runtime-module": {"owned_paths", "public_boundary", "dependencies"},
    "developer-flow": {"module_id", "scenario_ids"},
    "data-schema": {"owner", "lifecycle", "concurrency"},
    "input-schema": {"owner", "version", "unknown_fields", "unknown_values"},
    "output-schema": {"owner", "version", "unknown_fields", "unknown_values"},
    "event-schema": {"owner", "version", "unknown_fields", "unknown_values"},
    "job-schema": {"owner", "version", "unknown_fields", "unknown_values"},
    "provider-schema": {"owner", "version", "unknown_fields", "unknown_values"},
    "api-operation": {"protocol", "address", "authentication", "scope", "success", "errors", "idempotency", "compatibility", "client_mapping"},
    "event": {"producer", "trigger", "dispatch", "ordering", "deduplication", "consumer", "retry", "dead_letter", "replay", "observability"},
    "job": {"trigger", "handler", "ordering", "deduplication", "retry", "dead_letter", "replay", "observability"},
    "provider": {"adapter", "credentials", "command", "outcomes", "timeout", "retry", "circuit", "callback_security", "reconciliation", "telemetry"},
    "permission": {"actor", "scope", "allowed", "denial", "audit"},
    "state-transition": {"aggregate", "from_state", "command", "to_state", "owner", "effects", "invalid_behavior"},
    "route": {"client", "route", "state_owners", "interface", "states", "accessibility"},
    "scenario": {"actor", "authority", "fixture", "invocation", "response", "effects", "forbidden_effects", "controls", "cleanup", "evidence"},
    "migration": {"origin", "target", "order", "compatibility", "rollback", "verification"},
    "client-surface": {"routes", "state_owners", "authority", "states", "accessibility", "evidence"},
}

CANONICAL_SHELL_CLASSES = {
    "site-shell",
    "navigation-scrim",
    "sidebar",
    "sidebar-header",
    "documentation-nav",
    "sidebar-footer",
    "main",
    "topbar",
    "topbar-actions",
    "documentation-layout",
    "content",
    "breadcrumbs",
    "page-navigation",
    "page-rail",
    "footer",
}
CANONICAL_ASSET_HASHES = {
    "assets/styles.css": "3ee937b67f461a1ef807a9cc4c020f6be965581317ecc14d61abb6be771064d1",
    "assets/specs.js": "efcd6a6113fde6186804c5dc4f314ed5881d273e9d61bec3e16245fb1ea30ec2",
}

INVENTORY_DEFINITIONS = (
    ("product_journeys", PRODUCT_JOURNEY_INVENTORY, "product-journey", {"id", "title", "route", "actors", "entry_points", "architecture_flows", "runtime_modules", "scenario_ids"}),
    ("features", FEATURE_INVENTORY, "feature", {"id", "title", "route", "journey_ids", "architecture_flows", "runtime_modules", "scenario_ids"}),
    ("architecture_flows", ARCHITECTURE_FLOW_INVENTORY, "architecture-flow", {"id", "title", "route", "trigger", "terminal", "runtime_modules", "scenario_ids"}),
    ("runtime_modules", RUNTIME_MODULE_INVENTORY, "runtime-module", {"id", "title", "route", "role", "source_unit", "owned_paths", "public_boundary", "entry_flows", "scenario_ids"}),
    ("client_surfaces", CLIENT_SURFACE_INVENTORY, "client-runtime", {"id", "title", "route", "owned_paths", "routes", "scenario_ids"}),
)


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


def has_value(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict, set)):
        return bool(value)
    return value is not None


def has_exact_symbol(value: Any) -> bool:
    text = " ".join(str(item) for item in all_values(value))
    return bool(re.search(r"[./:]|\w+\([^)]*\)", text))


def has_code_symbol(value: Any) -> bool:
    text = " ".join(str(item) for item in all_values(value))
    return bool(re.search(r"::|#|\w+\([^)]*\)|\b\w+(?:\.\w+)+\b|\.(?:py|go|ts|tsx|js|jsx|java|rb|rs|cs)\b", text))


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
        self.class_counts: Counter[str] = Counter()
        self.theme_toggles = 0

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
        self.class_counts.update(class_names)
        self.forbidden_classes.update(class_names & {"feature-tabs", "subtabs", "search", "filter-bar"})
        if "data-theme-toggle" in values:
            self.theme_toggles += 1
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
            if not has_value(block.get("owner")):
                errors.append(f"{location}: contract code block requires an exact owner")
            if contract_kind == "data-schema":
                for field in ("lifecycle", "concurrency"):
                    if not has_value(block.get(field)):
                        errors.append(f"{location}: data schema requires {field}")
            if contract_kind in SEALED_SCHEMA_KINDS and block.get("sealed") is not True:
                errors.append(f"{location}: public payload schema {block.get('contract_id')} must set sealed=True")
            if contract_kind in SEALED_SCHEMA_KINDS:
                for field in ("unknown_fields", "unknown_values"):
                    if not has_value(block.get(field)):
                        errors.append(f"{location}: sealed payload schema requires {field}")
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
        if not isinstance(flow.get("steps"), list) or len(flow.get("steps", [])) < 4:
            errors.append(f"{location}: developer flow must contain at least four chronological steps")
        else:
            for step_index, step in enumerate(flow["steps"], 1):
                if not isinstance(step, dict):
                    errors.append(f"{location}: developer flow step {step_index} must be a dictionary")
                    continue
                step_missing = sorted(DEVELOPER_STEP_FIELDS - set(step))
                if step_missing:
                    errors.append(f"{location}: developer flow step {step_index} is missing {', '.join(step_missing)}")
                for field in DEVELOPER_STEP_FIELDS:
                    if field in step and not has_value(step[field]):
                        errors.append(f"{location}: developer flow step {step_index} has empty {field}")
                if has_value(step.get("symbols")) and not has_exact_symbol(step.get("symbols")):
                    errors.append(f"{location}: developer flow step {step_index} must name exact files/modules/symbols")
        for field in DEVELOPER_FLOW_FIELDS - {"steps"}:
            if field in flow and not has_value(flow[field]):
                errors.append(f"{location}: developer flow field {field} must be explicit")
        if has_value(flow.get("entry_point")) and not has_code_symbol(flow.get("entry_point")):
            errors.append(f"{location}: developer flow entry_point must name an exact route/event/schedule and symbol")
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
        is_starter = page.get("starter") is True
        metrics["starter_pages"] += int(is_starter)
        if is_starter and not allow_draft:
            errors.append(f"{source}: starter page remains in final specifications")
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
        nav_subgroup = str(page.get("nav_subgroup", ""))
        configured_subgroups = NAV_SUBGROUP_ORDER.get(str(page["nav_group"]), [])
        if nav_subgroup and configured_subgroups and nav_subgroup not in configured_subgroups:
            errors.append(f"{source}: nav_subgroup {nav_subgroup!r} is absent from NAV_SUBGROUP_ORDER")
        if not str(page["title"]).strip() or not str(page["summary"]).strip():
            errors.append(f"{source}: title and summary must be non-empty")
        if kind not in {"overview", "reference", "coverage", "decision-register"} and AMBIGUOUS_FOCUSED_TITLE.fullmatch(str(page["title"]).strip()):
            errors.append(f"{source}: focused page title is too vague to predict its flow or owner")

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

        if not is_starter:
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
            required_contract_fields = CONTRACT_REQUIRED_FIELDS.get(contract_kind, set())
            missing_contract_fields = sorted(required_contract_fields - set(contract))
            if missing_contract_fields:
                errors.append(f"{source}: {contract_kind} {contract_id} is missing {', '.join(missing_contract_fields)}")
            for field in required_contract_fields & set(contract):
                if not has_value(contract[field]):
                    errors.append(f"{source}: {contract_kind} {contract_id} has empty {field}")
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

        if not is_starter:
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


def validate_inventory(pages: list[dict[str, Any]], allow_draft: bool, metrics: Counter[str]) -> list[str]:
    errors: list[str] = []
    pages_by_route = {str(page.get("route")): page for page in pages}
    contracts = {
        str(contract.get("id")): contract
        for page in pages
        for contract in page.get("contracts", [])
        if isinstance(contract, dict) and contract.get("id")
    }
    scenario_ids = {contract_id for contract_id, contract in contracts.items() if contract.get("kind") == "scenario"}
    inventory_ids: dict[str, str] = {}
    inventory_route_owners: dict[str, str] = {}
    ids_by_name: dict[str, set[str]] = {}

    for name, entries, expected_kind, required_fields in INVENTORY_DEFINITIONS:
        ids_by_name[name] = set()
        metrics[f"inventory_{name}"] = len(entries)
        if not isinstance(entries, list):
            errors.append(f"{name} inventory must be a list")
            continue
        if not entries and not allow_draft:
            if name == "client_surfaces" and CLIENT_SURFACES_NOT_APPLICABLE_REASON.strip():
                metrics["client_surfaces_not_applicable"] = 1
            else:
                errors.append(f"Final specifications require a non-empty {name} inventory")
        for index, entry in enumerate(entries, 1):
            location = f"{name} inventory entry {index}"
            if not isinstance(entry, dict):
                errors.append(f"{location} must be a dictionary")
                continue
            missing = sorted(required_fields - set(entry))
            if missing:
                errors.append(f"{location} is missing {', '.join(missing)}")
                continue
            for field in required_fields:
                if not has_value(entry[field]):
                    errors.append(f"{location} has empty {field}")
            entry_id = str(entry["id"])
            if entry_id in inventory_ids:
                errors.append(f"{location} duplicates inventory id {entry_id} from {inventory_ids[entry_id]}")
            inventory_ids[entry_id] = name
            ids_by_name[name].add(entry_id)
            route = str(entry["route"])
            if route in inventory_route_owners:
                errors.append(
                    f"{location} reuses focused page {route} already owned by inventory {inventory_route_owners[route]}; "
                    "every inventory entry requires its own page"
                )
            else:
                inventory_route_owners[route] = entry_id
            page = pages_by_route.get(route)
            if page is None:
                errors.append(f"{location} points to missing page {route}")
            elif page.get("kind") != expected_kind:
                errors.append(f"{location} points to {page.get('kind')!r}, expected {expected_kind!r}")
            for scenario_id in entry.get("scenario_ids", []):
                if scenario_id not in scenario_ids:
                    errors.append(f"{location} references missing scenario contract {scenario_id}")

    cross_references = (
        (PRODUCT_JOURNEY_INVENTORY, "architecture_flows", "architecture_flows"),
        (PRODUCT_JOURNEY_INVENTORY, "runtime_modules", "runtime_modules"),
        (FEATURE_INVENTORY, "journey_ids", "product_journeys"),
        (FEATURE_INVENTORY, "architecture_flows", "architecture_flows"),
        (FEATURE_INVENTORY, "runtime_modules", "runtime_modules"),
        (ARCHITECTURE_FLOW_INVENTORY, "runtime_modules", "runtime_modules"),
    )
    for entries, field, target_inventory in cross_references:
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            for reference in entry.get(field, []):
                if reference not in ids_by_name.get(target_inventory, set()):
                    errors.append(f"Inventory {entry.get('id')} references missing {target_inventory} id {reference}")

    inventory_routes_by_kind = {
        expected_kind: {str(entry.get("route")) for entry in entries if isinstance(entry, dict)}
        for _, entries, expected_kind, _ in INVENTORY_DEFINITIONS
    }
    for page in pages:
        kind = str(page.get("kind"))
        if page.get("starter") is True or kind not in inventory_routes_by_kind:
            continue
        if str(page.get("route")) not in inventory_routes_by_kind[kind]:
            errors.append(f"{page.get('_source')}: focused {kind} page is absent from its source-backed inventory")

    for entry in RUNTIME_MODULE_INVENTORY:
        if not isinstance(entry, dict) or "route" not in entry:
            continue
        page = pages_by_route.get(str(entry["route"]))
        if page is None:
            continue
        actual_flows = {
            str(block.get("flow", {}).get("id"))
            for block in all_blocks(page)
            if block.get("type") == "developer-flow" and isinstance(block.get("flow"), dict)
        }
        declared_flows = {str(flow_id) for flow_id in entry.get("entry_flows", [])}
        if actual_flows != declared_flows:
            errors.append(
                f"Runtime module inventory {entry.get('id')} entry_flows do not match its developer code-flow directory: "
                f"declared={sorted(declared_flows)}, rendered={sorted(actual_flows)}"
            )
    errors.extend(validate_runtime_discovery(allow_draft, metrics))
    return errors


def validate_runtime_discovery(
    allow_draft: bool,
    metrics: Counter[str],
    *,
    repo_root: Path | None = None,
    discovery_roots: Any = None,
    exclusions: Any = None,
    runtime_modules: Any = None,
    settings_not_applicable_reason: str | None = None,
    common_not_applicable_reason: str | None = None,
) -> list[str]:
    """Prove that repository runtime units map one-to-one to focused handbook owners."""

    errors: list[str] = []
    repo_root = repo_root or ROOT.parent
    discovery_roots = RUNTIME_DISCOVERY_ROOTS if discovery_roots is None else discovery_roots
    exclusions = RUNTIME_DISCOVERY_EXCLUSIONS if exclusions is None else exclusions
    runtime_modules = RUNTIME_MODULE_INVENTORY if runtime_modules is None else runtime_modules
    settings_reason = RUNTIME_SETTINGS_NOT_APPLICABLE_REASON if settings_not_applicable_reason is None else settings_not_applicable_reason
    common_reason = RUNTIME_COMMON_NOT_APPLICABLE_REASON if common_not_applicable_reason is None else common_not_applicable_reason

    if not isinstance(discovery_roots, list):
        return ["RUNTIME_DISCOVERY_ROOTS must be a list"]
    if not discovery_roots and not allow_draft:
        errors.append("Final specifications require repository-backed RUNTIME_DISCOVERY_ROOTS")

    discovered: set[str] = set()
    allowed_modes = {"child-directories", "child-files", "root"}
    child_directory_roots = {
        str(root.get("path"))
        for root in discovery_roots
        if isinstance(root, dict) and root.get("mode") == "child-directories"
    }
    for index, root in enumerate(discovery_roots, 1):
        location = f"runtime discovery root {index}"
        if not isinstance(root, dict):
            errors.append(f"{location} must be a dictionary")
            continue
        missing = {"path", "mode", "include_extensions"} - set(root)
        if missing:
            errors.append(f"{location} is missing {', '.join(sorted(missing))}")
            continue
        relative = Path(str(root["path"]))
        if relative.is_absolute() or ".." in relative.parts:
            errors.append(f"{location} path must stay inside the repository: {relative}")
            continue
        mode = str(root["mode"])
        if mode not in allowed_modes:
            errors.append(f"{location} has unsupported mode {mode!r}")
            continue
        extensions = root["include_extensions"]
        if not isinstance(extensions, list) or not extensions or any(not isinstance(item, str) or not item.startswith(".") for item in extensions):
            errors.append(f"{location} include_extensions must be a non-empty list of suffixes such as .py or .go")
            continue
        absolute = repo_root / relative
        if not absolute.exists():
            errors.append(f"{location} path does not exist: {relative.as_posix()}")
            continue

        def contains_source(path: Path) -> bool:
            return any(candidate.is_file() and candidate.suffix in extensions for candidate in path.rglob("*"))

        candidates: list[Path]
        if mode == "root":
            nested_source_directories = [
                candidate
                for candidate in absolute.iterdir()
                if candidate.is_dir() and not candidate.name.startswith(".") and contains_source(candidate)
            ] if absolute.is_dir() else []
            if nested_source_directories and relative.as_posix() not in child_directory_roots:
                errors.append(
                    f"{location} root mode would hide source-bearing child units under {relative.as_posix()}; "
                    "add a child-directories discovery root for the same path or choose narrower roots"
                )
            has_direct_source = absolute.is_dir() and any(
                candidate.is_file() and candidate.suffix in extensions for candidate in absolute.iterdir()
            )
            candidates = [absolute] if has_direct_source else []
        elif mode == "child-directories":
            candidates = [candidate for candidate in absolute.iterdir() if candidate.is_dir() and not candidate.name.startswith(".") and contains_source(candidate)]
        else:
            candidates = [candidate for candidate in absolute.iterdir() if candidate.is_file() and candidate.suffix in extensions]
        if not candidates:
            errors.append(f"{location} discovered no source units under {relative.as_posix()}")
        for candidate in candidates:
            unit = candidate.relative_to(repo_root).as_posix()
            if unit in discovered:
                errors.append(f"Runtime source unit is discovered by more than one root: {unit}")
            discovered.add(unit)

    if not isinstance(exclusions, list):
        errors.append("RUNTIME_DISCOVERY_EXCLUSIONS must be a list")
        exclusions = []
    excluded: set[str] = set()
    for index, exclusion in enumerate(exclusions, 1):
        location = f"runtime discovery exclusion {index}"
        if not isinstance(exclusion, dict) or not {"path", "reason"} <= set(exclusion):
            errors.append(f"{location} requires path and reason")
            continue
        path = str(exclusion["path"])
        reason = str(exclusion["reason"]).strip()
        if path not in discovered:
            errors.append(f"{location} does not match a discovered source unit: {path}")
        if len(reason) < 20:
            errors.append(f"{location} requires a concrete non-runtime reason of at least 20 characters")
        if path in excluded:
            errors.append(f"{location} duplicates exclusion {path}")
        excluded.add(path)

    expected_units = discovered - excluded
    source_owners: dict[str, list[str]] = {}
    roles: list[str] = []
    allowed_roles = {"settings", "common", "implementation"}
    for index, entry in enumerate(runtime_modules if isinstance(runtime_modules, list) else [], 1):
        if not isinstance(entry, dict):
            continue
        entry_id = str(entry.get("id", f"entry-{index}"))
        role = str(entry.get("role", ""))
        roles.append(role)
        if role not in allowed_roles:
            errors.append(f"Runtime module inventory {entry_id} has invalid role {role!r}; expected settings, common, or implementation")
        source_unit = str(entry.get("source_unit", ""))
        source_owners.setdefault(source_unit, []).append(entry_id)
        if source_unit and source_unit not in entry.get("owned_paths", []):
            errors.append(f"Runtime module inventory {entry_id} must include source_unit {source_unit} in owned_paths")

    for source_unit, owners in source_owners.items():
        if source_unit not in expected_units:
            errors.append(f"Runtime module inventory source_unit is not an included discovered unit: {source_unit}")
        if len(owners) != 1:
            errors.append(f"Runtime source unit {source_unit} has multiple handbook owners: {', '.join(owners)}")
    for source_unit in sorted(expected_units - set(source_owners)):
        errors.append(f"Discovered runtime source unit has no focused handbook owner: {source_unit}")

    settings_count = roles.count("settings")
    common_count = roles.count("common")
    if not allow_draft:
        if settings_count == 0 and len(settings_reason.strip()) < 20:
            errors.append("Final runtime inventory requires one settings owner or a concrete not-applicable reason of at least 20 characters")
        elif settings_count != 1:
            errors.append(f"Final runtime inventory requires exactly one settings owner, found {settings_count}")
        if settings_count and settings_reason.strip():
            errors.append("RUNTIME_SETTINGS_NOT_APPLICABLE_REASON must be empty when a settings owner exists")
        if common_count == 0 and len(common_reason.strip()) < 20:
            errors.append("Final runtime inventory requires one common owner or a concrete not-applicable reason of at least 20 characters")
        elif common_count != 1:
            errors.append(f"Final runtime inventory requires exactly one common owner, found {common_count}")
        if common_count and common_reason.strip():
            errors.append("RUNTIME_COMMON_NOT_APPLICABLE_REASON must be empty when a common owner exists")
        expected_prefix = [role for role, count, reason in (("settings", settings_count, settings_reason), ("common", common_count, common_reason)) if count and not reason.strip()]
        if roles[:len(expected_prefix)] != expected_prefix:
            errors.append(f"Runtime inventory must list settings then common before implementation units; found prefix {roles[:len(expected_prefix)]}")

    metrics["runtime_discovery_roots"] = len(discovery_roots)
    metrics["runtime_units_discovered"] = len(discovered)
    metrics["runtime_units_excluded"] = len(excluded)
    metrics["runtime_units_owned"] = len(source_owners)
    return errors


def validate_generated(pages: list[dict[str, Any]], metrics: Counter[str]) -> list[str]:
    errors: list[str] = []
    parsers: dict[str, DocumentParser] = {}
    for relative, expected_hash in CANONICAL_ASSET_HASHES.items():
        asset = ROOT / relative
        if not asset.is_file():
            errors.append(f"Canonical shell asset is missing: {relative}")
            continue
        actual_hash = hashlib.sha256(asset.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            errors.append(f"Canonical shell asset drifted: {relative}")
    metrics["canonical_shell_assets"] = len(CANONICAL_ASSET_HASHES) - sum("shell asset" in error for error in errors)
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
        missing_shell_classes = sorted(css_class for css_class in CANONICAL_SHELL_CLASSES if parser.class_counts[css_class] != 1)
        if missing_shell_classes:
            errors.append(f"{route}: canonical Stride shell landmarks missing or duplicated: {', '.join(missing_shell_classes)}")
        if parser.theme_toggles != 1:
            errors.append(f"{route}: expected exactly one theme switcher, found {parser.theme_toggles}")
        topbar_match = re.search(r'<header class="topbar">(.*?)</header>', generated_text, flags=re.DOTALL)
        if topbar_match is None or "data-theme-toggle" not in topbar_match.group(1):
            errors.append(f"{route}: theme switcher must be in the top-right topbar actions")
        sidebar_footer_match = re.search(r'<div class="sidebar-footer">(.*?)</div>', generated_text, flags=re.DOTALL)
        if sidebar_footer_match and "data-theme-toggle" in sidebar_footer_match.group(1):
            errors.append(f"{route}: sidebar must not contain a second theme switcher")
        metrics["pages_with_input_elements"] += int(bool(parser.inputs))
        metrics["pages_with_forbidden_navigation"] += int(bool(parser.forbidden_classes))
        shell_failed = bool(missing_shell_classes or parser.theme_toggles != 1 or topbar_match is None or "data-theme-toggle" not in topbar_match.group(1))
        metrics["pages_with_shell_failures"] += int(parser.h1 != 1 or parser.aria_current != 1 or shell_failed)
        for contract in page.get("contracts", []):
            if str(contract.get("id", "")) not in generated_text:
                errors.append(f"{route}: contract {contract.get('id')} is not rendered on its owning page")
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
    inventory_errors = validate_inventory(pages, args.allow_draft, metrics)
    generated_errors = validate_generated(pages, metrics)
    errors = source_errors + inventory_errors + generated_errors
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
