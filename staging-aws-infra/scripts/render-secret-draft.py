#!/usr/bin/env python3
"""Render a private, user-editable secret draft without touching SOPS."""

import argparse
import json
import os
import re
import sys
from pathlib import Path


PLACEHOLDER = "__USER_INPUT_REQUIRED__"
KEY_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def fail(message: str) -> None:
    print(f"secret draft failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> object:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        fail(f"file not found: {path}")
    except json.JSONDecodeError as error:
        fail(f"invalid JSON in {path}: {error}")


def load_required_keys(path: Path) -> list[str]:
    payload = load_json(path)
    keys = payload.get("keys") if isinstance(payload, dict) else payload
    if not isinstance(keys, list) or not keys:
        fail("required keys must be a non-empty JSON array or an object with a keys array")
    if any(not isinstance(key, str) or not KEY_PATTERN.fullmatch(key) for key in keys):
        fail("required keys must be valid environment-variable names")
    if len(set(keys)) != len(keys):
        fail("required keys must not contain duplicates")
    return keys


def load_infra_values(path: Path) -> dict[str, str]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        fail("infra values must be a JSON object")
    if any(not isinstance(key, str) or not KEY_PATTERN.fullmatch(key) for key in payload):
        fail("infra value keys must be valid environment-variable names")
    if any(not isinstance(value, str) for value in payload.values()):
        fail("infra values must be strings")
    return payload


def inside_git_worktree(path: Path) -> bool:
    for parent in (path, *path.parents):
        if (parent / ".git").exists():
            return True
    return False


def write_private_json(path: Path, payload: dict[str, str]) -> None:
    path = path.expanduser().resolve()
    if inside_git_worktree(path.parent):
        fail("output must be outside a Git working tree")
    if path.exists():
        fail(f"output already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render a private secret draft from repository keys and approved infrastructure values."
    )
    parser.add_argument("--required-keys", required=True, type=Path)
    parser.add_argument("--infra-values", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    required_keys = load_required_keys(args.required_keys)
    infra_values = load_infra_values(args.infra_values)
    extra_keys = sorted(set(infra_values) - set(required_keys))
    if extra_keys:
        fail("infra values include keys absent from the repository requirements: " + ", ".join(extra_keys))

    draft = {key: infra_values.get(key, PLACEHOLDER) for key in required_keys}
    write_private_json(args.output, draft)

    derived = sorted(infra_values)
    unresolved = sorted(set(required_keys) - set(infra_values))
    print(f"secret draft written: {args.output.expanduser().resolve()}")
    print("derived keys: " + (", ".join(derived) if derived else "none"))
    print("user-required keys: " + (", ".join(unresolved) if unresolved else "none"))


if __name__ == "__main__":
    main()
