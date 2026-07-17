#!/usr/bin/env python3
"""Run deterministic generation and mechanical quality checks for a generated .specs site."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a repository specification system")
    parser.add_argument("--repo", default=".", type=Path, help="Repository root")
    parser.add_argument(
        "--allow-draft",
        action="store_true",
        help="Prove rough-cut structure while permitting draft status and pending decisions",
    )
    return parser.parse_args()


def run(name: str, command: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    output = (completed.stdout + completed.stderr).strip().splitlines()
    return {
        "name": name,
        "command": command,
        "exit_code": completed.returncode,
        "passed": completed.returncode == 0,
        "output_tail": output[-20:],
        "stdout": completed.stdout,
    }


def generated_snapshot(specs: Path) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for path in sorted(specs.rglob("*.html")):
        snapshot[path.relative_to(specs).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return snapshot


def parse_validation(result: dict[str, Any]) -> dict[str, Any]:
    try:
        payload = json.loads(result["stdout"])
    except (json.JSONDecodeError, TypeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def main() -> int:
    args = parse_args()
    repo = args.repo.expanduser().resolve()
    specs = repo / ".specs"
    required = (specs / "_build.py", specs / "_validate.py", specs / "_conformance_tests.py")
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        print(json.dumps({"mechanical_gate_passed": False, "errors": ["Missing: " + path for path in missing]}, indent=2))
        return 1

    py = sys.executable
    commands: list[dict[str, Any]] = []
    first = run("build_first", [py, ".specs/_build.py"], repo)
    commands.append(first)
    first_snapshot = generated_snapshot(specs) if first["passed"] else {}

    validation_command = [py, ".specs/_validate.py", "--json"]
    if args.allow_draft:
        validation_command.append("--allow-draft")
    validation = run("validate", validation_command, repo)
    commands.append(validation)
    commands.append(run("conformance_tests", [py, ".specs/_conformance_tests.py"], repo))
    second = run("build_second", [py, ".specs/_build.py"], repo)
    commands.append(second)
    second_snapshot = generated_snapshot(specs) if second["passed"] else {}
    deterministic = bool(first_snapshot) and first_snapshot == second_snapshot

    if (repo / ".git").exists():
        commands.append(run("diff_check", ["git", "diff", "--check"], repo))

    errors = []
    for command in commands:
        if not command["passed"]:
            errors.append(f"{command['name']} failed with exit code {command['exit_code']}")
    if not deterministic:
        errors.append("Generated HTML changed between identical consecutive builds")

    validation_payload = parse_validation(validation)
    validation_metrics = validation_payload.get("metrics", {})
    completion_gate_passed = (
        not errors
        and validation_payload.get("spec_status") == "final"
        and validation_metrics.get("pending_decisions", 0) == 0
        and validation_metrics.get("pending_requirements", 0) == 0
    )
    report = {
        "schema_version": 1,
        "repo": repo.name,
        "mechanical_gate_passed": not errors,
        "completion_gate_passed": completion_gate_passed,
        "draft_mode": args.allow_draft,
        "deterministic_generation": deterministic,
        "metrics": validation_metrics,
        "validation_errors": validation_payload.get("errors", []),
        "commands": [{key: value for key, value in item.items() if key != "stdout"} for item in commands],
        "errors": errors,
        "semantic_rating_required": True,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
