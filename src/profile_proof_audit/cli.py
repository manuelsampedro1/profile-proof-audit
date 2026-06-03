from __future__ import annotations

import argparse
import json
import re
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path


REQUIRED_SECTIONS = [
    "Current Focus",
    "Selected Work",
    "How I Work With Codex",
    "Public Workbench",
    "Latest Proof",
    "Principles",
]

RISKY_PHRASES = [
    "guaranteed",
    "production-ready",
    "best in the world",
    "fully autonomous",
    "perfect",
]


@dataclass(frozen=True)
class LinkCheck:
    text: str
    target: str
    kind: str
    status: str


@dataclass(frozen=True)
class AuditReport:
    schema_version: str
    file: str
    score: int
    sections_present: list[str]
    sections_missing: list[str]
    selected_work_rows: int
    latest_proof_items: int
    link_checks: list[LinkCheck]
    issues: list[str]
    warnings: list[str]


def headings(markdown: str) -> list[str]:
    result: list[str] = []
    for line in markdown.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            result.append(match.group(1).strip())
    return result


def section_body(markdown: str, section: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(section)}\s*$", re.MULTILINE)
    match = pattern.search(markdown)
    if not match:
        return ""
    rest = markdown[match.end() :]
    next_match = re.search(r"^##\s+", rest, re.MULTILINE)
    if next_match:
        return rest[: next_match.start()]
    return rest


def markdown_links(markdown: str) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = []
    for match in re.finditer(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", markdown):
        text = match.group(1).strip()
        target = match.group(2).strip()
        if target.startswith("#"):
            continue
        links.append((text, target))
    return links


def is_external(target: str) -> bool:
    parsed = urllib.parse.urlparse(target)
    return parsed.scheme in {"http", "https"}


def http_status(target: str, timeout: float = 5.0, attempts: int = 2) -> str:
    request = urllib.request.Request(target, method="GET", headers={"User-Agent": "profile-proof-audit"})
    status = 0
    for attempt in range(max(1, attempts)):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                status = getattr(response, "status", 0)
            break
        except urllib.error.HTTPError as error:
            status = error.code
            break
        except (urllib.error.URLError, TimeoutError, socket.timeout, OSError):
            if attempt == max(1, attempts) - 1:
                return "unknown"
    if status == 200:
        return "ok"
    if status == 404:
        return "not-found"
    return f"http-{status}"


def check_links(markdown: str, base_dir: Path, check_http: bool) -> list[LinkCheck]:
    checks: list[LinkCheck] = []
    for text, target in markdown_links(markdown):
        if is_external(target):
            status = http_status(target) if check_http else "unchecked"
            checks.append(LinkCheck(text, target, "external", status))
            continue
        clean_target = target.split("#", 1)[0]
        if not clean_target:
            status = "ok"
        else:
            status = "ok" if (base_dir / clean_target).exists() else "missing"
        checks.append(LinkCheck(text, target, "relative", status))
    return checks


def count_selected_work_rows(markdown: str) -> int:
    body = section_body(markdown, "Selected Work")
    rows = 0
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if "---" in stripped or "Repo |" in stripped:
            continue
        if stripped.count("|") >= 3:
            rows += 1
    return rows


def count_latest_proof_items(markdown: str) -> int:
    body = section_body(markdown, "Latest Proof")
    return sum(1 for line in body.splitlines() if line.strip().startswith("- "))


def risky_phrase_warnings(markdown: str) -> list[str]:
    lowered = markdown.lower()
    return [f"Risky unsupported phrase found: `{phrase}`." for phrase in RISKY_PHRASES if phrase in lowered]


def build_report(readme_path: Path, check_http: bool = False) -> AuditReport:
    markdown = readme_path.read_text(encoding="utf-8")
    present = headings(markdown)
    missing_sections = [section for section in REQUIRED_SECTIONS if section not in present]
    link_checks = check_links(markdown, readme_path.parent, check_http)
    selected_rows = count_selected_work_rows(markdown)
    latest_items = count_latest_proof_items(markdown)
    issues: list[str] = []
    warnings: list[str] = risky_phrase_warnings(markdown)

    for section in missing_sections:
        issues.append(f"Missing required section: {section}.")
    for check in link_checks:
        if check.status in {"missing", "not-found"}:
            issues.append(f"Broken link `{check.text}` -> `{check.target}` ({check.status}).")
        elif check.status.startswith("http-") or check.status == "unknown":
            warnings.append(f"Uncertain link `{check.text}` -> `{check.target}` ({check.status}).")
    if selected_rows < 3:
        warnings.append("Selected Work has fewer than 3 proof rows.")
    if latest_items < 2:
        warnings.append("Latest Proof has fewer than 2 items.")

    score = max(0, 100 - (len(issues) * 15) - (len(warnings) * 5))
    return AuditReport(
        schema_version="profile-proof-audit.v1",
        file=str(readme_path),
        score=score,
        sections_present=present,
        sections_missing=missing_sections,
        selected_work_rows=selected_rows,
        latest_proof_items=latest_items,
        link_checks=link_checks,
        issues=issues,
        warnings=warnings,
    )


def render_markdown(report: AuditReport) -> str:
    lines = [
        "# Profile Proof Audit",
        "",
        f"Score: {report.score}/100",
        "",
        "## Issues",
        "",
    ]
    lines.extend(f"- {issue}" for issue in report.issues or ["none"])
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- {warning}" for warning in report.warnings or ["none"])
    lines.extend(["", "## Sections", ""])
    lines.extend(f"- present: {section}" for section in report.sections_present)
    if report.sections_missing:
        lines.extend(f"- missing: {section}" for section in report.sections_missing)
    lines.extend(["", "## Link Checks", ""])
    for check in report.link_checks:
        lines.append(f"- {check.status}: [{check.text}]({check.target})")
    if not report.link_checks:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="profile-proof-audit")
    parser.add_argument("readme", help="Path to profile README.md.")
    parser.add_argument("--check-http", action="store_true", help="Check external links over HTTP.")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    readme = Path(args.readme).expanduser()
    if not readme.exists() or not readme.is_file():
        print(f"README path does not exist: {readme}", file=sys.stderr)
        return 2
    report = build_report(readme, args.check_http)
    if args.format == "json":
        print(json.dumps(asdict(report), indent=2))
    else:
        print(render_markdown(report), end="")
    return 0
