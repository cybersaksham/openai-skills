#!/usr/bin/env python3
"""Render one private environment draft from an application's .env.example."""

import argparse
import os
import re
import sys
from pathlib import Path


KEY_VALUE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")


def fail(message: str) -> None:
    print(f"environment draft failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_values(path: Path | None) -> dict[str, str]:
    values: dict[str, str] = {}
    if path is None:
        source_name = "<stdin>"
        lines = sys.stdin.read().splitlines()
    else:
        source_name = str(path)
        lines = path.read_text(encoding="utf-8").splitlines()
    for line_number, raw_line in enumerate(lines, 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = KEY_VALUE.fullmatch(line)
        if match is None:
            fail(f"invalid values entry at {source_name}:{line_number}")
        key, value = match.groups()
        if key in values:
            fail(f"duplicate values key: {key}")
        values[key] = value
    return values


def inside_git_worktree(path: Path) -> bool:
    return any((parent / ".git").exists() for parent in (path, *path.parents))


def render(
    example: Path, values: dict[str, str], blank_keys: set[str], output: Path
) -> tuple[list[str], list[str]]:
    lines = example.read_text(encoding="utf-8").splitlines(keepends=True)
    template_keys = {
        match.group(1)
        for line in lines
        if (match := KEY_VALUE.fullmatch(line.rstrip("\r\n"))) is not None
    }
    unknown_values = sorted(set(values) - template_keys)
    unknown_blanks = sorted(blank_keys - template_keys)
    if unknown_values:
        fail("values contain keys absent from example: " + ", ".join(unknown_values))
    if unknown_blanks:
        fail("blank keys absent from example: " + ", ".join(unknown_blanks))

    rendered: list[str] = []
    derived: list[str] = []
    blanked: list[str] = []
    for raw_line in lines:
        suffix = "\n" if raw_line.endswith("\n") else ""
        match = KEY_VALUE.fullmatch(raw_line.rstrip("\r\n"))
        if match is None:
            rendered.append(raw_line)
            continue
        key, _ = match.groups()
        if key in values:
            rendered.append(f"{key}={values[key]}{suffix}")
            derived.append(key)
        elif key in blank_keys:
            rendered.append(f"{key}={suffix}")
            blanked.append(key)
        else:
            rendered.append(raw_line)

    target = output.expanduser().resolve()
    if inside_git_worktree(target.parent):
        fail("output must be outside a Git working tree")
    if target.exists():
        fail(f"output already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(target.parent, 0o700)
    descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.writelines(rendered)
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        target.unlink(missing_ok=True)
        raise
    return derived, blanked


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render a private .env draft from an application's .env.example."
    )
    parser.add_argument("--example", required=True, type=Path)
    parser.add_argument(
        "--values",
        required=True,
        help="private KEY=VALUE input file, or - to read it from standard input",
    )
    parser.add_argument("--blank-key", action="append", default=[])
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if not args.example.is_file():
        fail(f"example file not found: {args.example}")
    values_path = None if args.values == "-" else Path(args.values)
    if values_path is not None and not values_path.is_file():
        fail(f"values file not found: {values_path}")
    values = load_values(values_path)
    derived, blanked = render(args.example, values, set(args.blank_key), args.output)
    print(f"environment draft written: {args.output.expanduser().resolve()}")
    print("derived keys: " + (", ".join(sorted(derived)) if derived else "none"))
    print("blank user-required keys: " + (", ".join(sorted(blanked)) if blanked else "none"))


if __name__ == "__main__":
    main()
