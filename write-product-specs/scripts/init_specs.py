#!/usr/bin/env python3
"""Initialize a product-neutral static HTML specification system."""

from __future__ import annotations

import argparse
import html
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a new .specs source tree and generate its starter HTML.",
    )
    parser.add_argument("--root", required=True, type=Path, help="Product repository root")
    parser.add_argument("--product-name", required=True, help="Human-facing product name")
    parser.add_argument(
        "--tagline",
        default="TODO: define the product promise in one sentence.",
        help="One-sentence product promise; may be filled later",
    )
    return parser.parse_args()


def copy_template(template_root: Path, target: Path, replacements: dict[str, str]) -> None:
    for source in sorted(template_root.rglob("*")):
        relative = source.relative_to(template_root)
        if source.is_dir():
            (target / relative).mkdir(parents=True, exist_ok=True)
            continue
        destination_relative = relative.with_suffix("") if source.suffix == ".tmpl" else relative
        destination = target / destination_relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix in {".py", ".tmpl", ".css", ".js", ".svg", ".gitignore"}:
            content = source.read_text()
            for marker, value in replacements.items():
                content = content.replace(marker, value)
            destination.write_text(content)
        else:
            shutil.copyfile(source, destination)


def main() -> int:
    args = parse_args()
    if sys.version_info < (3, 10):
        print("The bundled specification scaffold requires Python 3.10 or newer.", file=sys.stderr)
        return 2

    product_name = args.product_name.strip()
    tagline = args.tagline.strip()
    if not product_name:
        print("Product name must not be empty.", file=sys.stderr)
        return 2
    if not tagline:
        print("Product tagline must not be empty.", file=sys.stderr)
        return 2

    root = args.root.expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"Repository root does not exist or is not a directory: {root}", file=sys.stderr)
        return 2

    target = root / ".specs"
    if target.is_symlink():
        print(f"Refusing to initialize through a symbolic link: {target}", file=sys.stderr)
        return 2
    if target.exists() and any(target.iterdir()):
        print(
            f"Refusing to overwrite existing specification system: {target}\n"
            "Inspect and evolve the existing generator instead.",
            file=sys.stderr,
        )
        return 2

    template_root = Path(__file__).resolve().parents[1] / "assets" / "specs-template"
    if not template_root.is_dir():
        print(f"Bundled specification template is missing: {template_root}", file=sys.stderr)
        return 2

    target.mkdir(parents=True, exist_ok=True)
    replacements = {
        "__PRODUCT_NAME_REPR__": repr(product_name),
        "__PRODUCT_TAGLINE_REPR__": repr(tagline),
        "__PRODUCT_INITIAL__": html.escape(product_name[:1].upper(), quote=True),
    }
    copy_template(template_root, target, replacements)
    (target / "features").mkdir(exist_ok=True)

    subprocess.run([sys.executable, str(target / "_build.py")], cwd=root, check=True)
    print(f"Created specification system: {target}")
    print("Next: replace placeholders, populate feature/design manifests, build, validate, and visually audit.")
    print("  python3 .specs/_build.py")
    print("  python3 .specs/_validate.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
