"""Shared, dependency-free safety policy for generated specification HTML."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


SAFE_LINK_SCHEMES = {"http", "https", "mailto", "tel"}
FORBIDDEN_ACTIVE_TAGS = {"base", "embed", "form", "iframe", "object", "style", "svg"}
RESOURCE_TAG_ATTRIBUTES = {
    "link": "href",
    "video": "poster",
}
_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")
_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_BAD_PERCENT_RE = re.compile(r"%(?![0-9A-Fa-f]{2})")
_CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_CSS_ESCAPE_RE = re.compile(r"\\(?:([0-9A-Fa-f]{1,6})(?:\s)?|(.))", re.DOTALL)
_CSS_URL_START_RE = re.compile(r"url\s*\(", re.IGNORECASE)
_CSS_URL_RE = re.compile(
    r"url\s*\(\s*(?:(['\"])(.*?)\1|([^)]*))\s*\)",
    re.IGNORECASE | re.DOTALL,
)


@dataclass
class HtmlScan:
    """Security-relevant facts collected from one HTML document or fragment."""

    ids: list[str] = field(default_factory=list)
    hrefs: list[str] = field(default_factory=list)
    resources: list[str] = field(default_factory=list)
    unanchored_sections: list[str] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)


def _basic_url_issue(url: str, *, resource: bool) -> str | None:
    if not url:
        return "resource URL is empty" if resource else "link URL is empty"
    if url != url.strip() or _CONTROL_RE.search(url):
        return "URL contains leading, trailing, or control whitespace"
    if "\\" in url:
        return "URL contains a backslash"
    if _BAD_PERCENT_RE.search(url):
        return "URL contains an invalid percent escape"

    parsed = urlsplit(url)
    scheme = parsed.scheme.lower()
    if resource:
        if scheme == "data":
            return "embedded data resources are forbidden"
        if scheme or parsed.netloc:
            return "external resources are forbidden"
    else:
        if parsed.netloc and not scheme:
            return "protocol-relative links are forbidden"
        if scheme and scheme not in SAFE_LINK_SCHEMES:
            return f"unsafe link scheme: {scheme}"
        if not scheme and _SCHEME_RE.match(url):
            return "unsafe or malformed link scheme"
    return None


class _PolicyParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.result = HtmlScan()

    def _inspect(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        normalized = [(name.lower(), value or "") for name, value in attrs]
        values = dict(normalized)

        identifier = values.get("id", "")
        if identifier:
            self.result.ids.append(identifier)
        if tag == "h2" and not identifier:
            self.result.unanchored_sections.append(tag)

        if tag in FORBIDDEN_ACTIVE_TAGS:
            self.result.violations.append(f"forbidden active <{tag}> element")
        if tag == "script" and not values.get("src", "").strip():
            self.result.violations.append("inline <script> content is forbidden")
        if tag == "meta" and values.get("http-equiv", "").strip().lower() == "refresh":
            self.result.violations.append("meta refresh is forbidden")

        for name, value in normalized:
            if name.startswith("on"):
                self.result.violations.append(f"event-handler attribute is forbidden: {name}")
            if name in {"style", "srcdoc", "srcset"}:
                self.result.violations.append(f"inline {name} attribute is forbidden")
            if name in {"action", "formaction"}:
                issue = _basic_url_issue(value, resource=False)
                if issue:
                    self.result.violations.append(f"{name} {issue}")

        href = values.get("href", "")
        if tag == "a" and href:
            self.result.hrefs.append(href)
            issue = _basic_url_issue(href, resource=False)
            if issue:
                self.result.violations.append(issue)

        resource_urls: list[str] = []
        if values.get("src", ""):
            resource_urls.append(values["src"])
        resource_attribute = RESOURCE_TAG_ATTRIBUTES.get(tag)
        if resource_attribute and values.get(resource_attribute, ""):
            resource_urls.append(values[resource_attribute])
        for resource_url in resource_urls:
            self.result.resources.append(resource_url)
            issue = _basic_url_issue(resource_url, resource=True)
            if issue:
                self.result.violations.append(issue)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._inspect(tag, attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._inspect(tag, attrs)


def scan_html(source: str) -> HtmlScan:
    """Return structural facts and fail-closed HTML policy violations."""

    parser = _PolicyParser()
    try:
        parser.feed(source)
        parser.close()
    except Exception as exc:  # HTMLParser failures must make authored HTML unusable.
        parser.result.violations.append(f"HTML parsing failed: {exc}")
    return parser.result


def _within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def url_issue(
    document_path: Path,
    url: str,
    root: Path,
    resource: bool,
    require_exists: bool,
) -> str | None:
    """Return the policy violation for a URL, or ``None`` when it is safe."""

    issue = _basic_url_issue(url, resource=resource)
    if issue:
        return issue

    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc:
        return None
    if resource and not parsed.path:
        return "local resource URL has no path"
    if not parsed.path:
        return None
    if parsed.path.startswith("/"):
        return "absolute local URLs are forbidden"

    decoded_path = unquote(parsed.path)
    if _CONTROL_RE.search(decoded_path) or "\\" in decoded_path:
        return "decoded local URL contains a control character or backslash"

    resolved_root = root.resolve()
    resolved_document = document_path.resolve(strict=False)
    if not _within(resolved_document, resolved_root):
        return "document path escapes the specification root"

    target = (resolved_document.parent / decoded_path).resolve(strict=False)
    if not _within(target, resolved_root):
        return "local URL escapes the specification root"
    if require_exists:
        if not target.exists():
            return f"local target is missing: {parsed.path}"
        if not target.is_file():
            return f"local target is not a file: {parsed.path}"
    return None


def _decode_css_escapes(source: str) -> str:
    def replace(match: re.Match[str]) -> str:
        hexadecimal, escaped = match.groups()
        if escaped is not None:
            return escaped
        try:
            codepoint = int(hexadecimal, 16)
            if codepoint == 0 or codepoint > 0x10FFFF:
                return "\ufffd"
            return chr(codepoint)
        except (TypeError, ValueError):
            return "\ufffd"

    return _CSS_ESCAPE_RE.sub(replace, source)


def css_issues(stylesheet_path: Path, root: Path) -> list[str]:
    """Validate one stylesheet and every local ``url()`` resource it references."""

    issues: list[str] = []
    resolved_root = root.resolve()
    resolved_stylesheet = stylesheet_path.resolve(strict=False)
    if not _within(resolved_stylesheet, resolved_root):
        return ["stylesheet escapes the specification root"]
    if not resolved_stylesheet.is_file():
        return ["stylesheet is missing or is not a file"]
    try:
        source = resolved_stylesheet.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"stylesheet could not be read as UTF-8: {exc}"]

    without_comments = _CSS_COMMENT_RE.sub("", source)
    if "/*" in without_comments or "*/" in without_comments:
        issues.append("stylesheet contains an unterminated or unmatched comment")
    normalized = _decode_css_escapes(without_comments)

    if re.search(r"@\s*import\b", normalized, re.IGNORECASE):
        issues.append("CSS @import is forbidden")
    if re.search(r"\bexpression\s*\(", normalized, re.IGNORECASE):
        issues.append("CSS expression() is forbidden")
    if re.search(r"\b(?:java|vb)script\s*:", normalized, re.IGNORECASE):
        issues.append("script URL syntax is forbidden in CSS")

    starts = list(_CSS_URL_START_RE.finditer(normalized))
    matches = []
    cursor = 0
    for start in starts:
        if start.start() < cursor:
            continue
        match = _CSS_URL_RE.match(normalized, start.start())
        if match is None:
            issues.append("CSS contains a malformed url() value")
            cursor = start.end()
            continue
        matches.append(match)
        cursor = match.end()

    for match in matches:
        url = (match.group(2) if match.group(1) else match.group(3) or "").strip()
        issue = url_issue(
            resolved_stylesheet,
            url,
            resolved_root,
            resource=True,
            require_exists=True,
        )
        if issue:
            issues.append(f"CSS url({url!r}) {issue}")
    return issues
