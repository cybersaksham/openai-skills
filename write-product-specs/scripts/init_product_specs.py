#!/usr/bin/env python3
"""Install a product-specification scaffold and three-skill repository pipeline safely."""

from __future__ import annotations

import argparse
import html
import shutil
import subprocess
import sys
from pathlib import Path


TEXT_SUFFIXES = {"", ".css", ".gitignore", ".html", ".js", ".md", ".py", ".svg", ".tmpl", ".yaml"}
SKILL_NAMES = ("maintain-specifications", "create-feature-plan", "implement-feature")
CLAUDE_ALIASES = (
    (Path(".claude"), Path(".agents"), True),
    (Path("CLAUDE.md"), Path("AGENTS.md"), False),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create .specs and install the specification-first repository skill pipeline.",
    )
    parser.add_argument("--repo", required=True, type=Path, help="Target repository root")
    parser.add_argument("--product-name", required=True, help="Human-facing product name")
    parser.add_argument("--tagline", required=True, help="One-sentence product promise")
    parser.add_argument("--backend-path", default="backend", help="Primary backend/runtime path")
    parser.add_argument("--client-path", default="frontend", help="Primary client/frontend path")
    parser.add_argument("--deployment-path", default="deployment", help="Deployment/infra path")
    return parser.parse_args()


def validate_value(label: str, value: str) -> str:
    result = value.strip()
    if not result:
        raise ValueError(f"{label} must not be empty")
    if "\x00" in result or "\n" in result or "\r" in result:
        raise ValueError(f"{label} must be a single safe line")
    return result


def ensure_safe_repo(repo: Path) -> Path:
    resolved = repo.expanduser().resolve()
    if not resolved.is_dir():
        raise ValueError(f"Repository root does not exist or is not a directory: {resolved}")
    if (resolved / ".specs").is_symlink() or (resolved / ".agents").is_symlink():
        raise ValueError("Refusing to initialize through a .specs or .agents symbolic link")
    specs = resolved / ".specs"
    if specs.exists() and any(specs.iterdir()):
        raise ValueError(
            f"Specification system already exists: {specs}. "
            "Inspect and evolve it with the skill; do not initialize over it."
        )
    validate_claude_aliases(resolved)
    return resolved


def validate_claude_aliases(repo: Path) -> None:
    """Refuse every Claude path except the exact compatibility aliases."""
    for relative, expected_target, _ in CLAUDE_ALIASES:
        destination = repo / relative
        if destination.is_symlink():
            actual_target = destination.readlink()
            if actual_target != expected_target:
                raise ValueError(
                    f"Refusing to replace Claude alias {destination}: "
                    f"expected {expected_target}, found {actual_target}"
                )
            continue
        if destination.exists():
            raise ValueError(
                f"Refusing to replace existing Claude path: {destination}. "
                f"Move or reconcile it before creating the required alias to {expected_target}."
            )


def render_text(content: str, replacements: dict[str, str]) -> str:
    for marker, value in replacements.items():
        content = content.replace(marker, value)
    return content


def copy_tree_missing(source_root: Path, target_root: Path, replacements: dict[str, str]) -> list[Path]:
    created: list[Path] = []
    for source in sorted(source_root.rglob("*")):
        relative = source.relative_to(source_root)
        destination_relative = relative.with_suffix("") if source.suffix == ".tmpl" else relative
        destination = target_root / destination_relative
        if source.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue
        if destination.exists():
            raise FileExistsError(f"Refusing to overwrite existing file: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix in TEXT_SUFFIXES:
            destination.write_text(render_text(source.read_text(), replacements))
        else:
            shutil.copyfile(source, destination)
        created.append(destination)
    return created


def copy_file_missing(source: Path, destination: Path) -> bool:
    if destination.exists():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    return True


def install_skills(skill_root: Path, repo: Path, replacements: dict[str, str]) -> tuple[list[Path], list[str]]:
    template_root = skill_root / "assets" / "project-template" / "skills"
    target_root = repo / ".agents" / "skills"
    created: list[Path] = []
    skipped: list[str] = []
    for name in SKILL_NAMES:
        target = target_root / name
        if target.exists():
            skipped.append(name)
            continue
        created.extend(copy_tree_missing(template_root / name, target, replacements))

    maintain = target_root / "maintain-specifications"
    if "maintain-specifications" not in skipped:
        references = skill_root / "references"
        scripts = skill_root / "scripts"
        copies = (
            (references / "documentation-standard.md", maintain / "references" / "documentation-standard.md"),
            (references / "evaluation-rubric.md", maintain / "references" / "rating-framework.md"),
            (scripts / "spec_quality_gate.py", maintain / "scripts" / "spec_quality_gate.py"),
        )
        for source, destination in copies:
            if copy_file_missing(source, destination):
                created.append(destination)
    return created, skipped


def install_root_harness(template_root: Path, repo: Path, replacements: dict[str, str]) -> tuple[bool, str]:
    target = repo / "AGENTS.md"
    if target.exists():
        return False, "Existing AGENTS.md preserved; merge the bundled specification routing block semantically."
    content = render_text((template_root / "AGENTS.md.tmpl").read_text(), replacements)
    target.write_text(content)
    return True, "Created root AGENTS.md because no harness existed."


def install_claude_aliases(repo: Path) -> list[Path]:
    """Create the only supported Claude compatibility entries as relative links."""
    created: list[Path] = []
    for relative, target, target_is_directory in CLAUDE_ALIASES:
        destination = repo / relative
        if destination.is_symlink():
            continue
        destination.symlink_to(target, target_is_directory=target_is_directory)
        created.append(destination)
    return created


def main() -> int:
    args = parse_args()
    if sys.version_info < (3, 10):
        print("Python 3.10 or newer is required.", file=sys.stderr)
        return 2

    try:
        product_name = validate_value("Product name", args.product_name)
        tagline = validate_value("Tagline", args.tagline)
        backend_path = validate_value("Backend path", args.backend_path)
        client_path = validate_value("Client path", args.client_path)
        deployment_path = validate_value("Deployment path", args.deployment_path)
        repo = ensure_safe_repo(args.repo)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    skill_root = Path(__file__).resolve().parents[1]
    template_root = skill_root / "assets" / "project-template"
    specs_template = template_root / "specs"
    if not specs_template.is_dir():
        print(f"Bundled specification template is missing: {specs_template}", file=sys.stderr)
        return 2

    replacements = {
        "__PRODUCT_NAME__": product_name,
        "__PRODUCT_NAME_REPR__": repr(product_name),
        "__PRODUCT_TAGLINE__": tagline,
        "__PRODUCT_TAGLINE_REPR__": repr(tagline),
        "__PRODUCT_INITIAL__": html.escape(product_name[:1].upper() or "P", quote=True),
        "__BACKEND_PATH__": backend_path,
        "__CLIENT_PATH__": client_path,
        "__DEPLOYMENT_PATH__": deployment_path,
    }

    created: list[Path] = []
    try:
        created.extend(copy_tree_missing(specs_template, repo / ".specs", replacements))
        skill_files, skipped = install_skills(skill_root, repo, replacements)
        created.extend(skill_files)
        harness_created, harness_message = install_root_harness(template_root, repo, replacements)
        if harness_created:
            created.append(repo / "AGENTS.md")
        created.extend(install_claude_aliases(repo))
    except (FileExistsError, OSError) as exc:
        print(f"Initialization stopped safely: {exc}", file=sys.stderr)
        return 2

    build = subprocess.run(
        [sys.executable, str(repo / ".specs" / "_build.py")],
        cwd=repo,
        text=True,
        capture_output=True,
    )
    if build.returncode:
        print(build.stdout, end="")
        print(build.stderr, end="", file=sys.stderr)
        print("Scaffold was copied, but its starter build failed.", file=sys.stderr)
        return build.returncode

    print(f"Created specification scaffold at {repo / '.specs'}")
    print(f"Created {len(created)} entries without overwriting existing paths.")
    print(harness_message)
    print("Claude compatibility: .claude -> .agents and CLAUDE.md -> AGENTS.md")
    if skipped:
        print("Existing skills preserved for semantic merge: " + ", ".join(skipped))
    print("The scaffold status is draft by design. Populate project-specific source pages, resolve decisions,")
    print("set SPEC_STATUS = 'final', merge any existing harness, then run:")
    print("  python3 .agents/skills/maintain-specifications/scripts/spec_quality_gate.py --repo .")
    print("For a blocked rough cut, prove structure without claiming completion with:")
    print("  python3 .agents/skills/maintain-specifications/scripts/spec_quality_gate.py --repo . --allow-draft")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
