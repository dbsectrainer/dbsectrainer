#!/usr/bin/env python3
"""Validate the GitHub profile README and its supporting assets.

The profile has no application server. Its "runtime" is GitHub's Markdown
renderer, so this validator checks the things that can break the rendered
profile: anchors, TOC targets, heading structure, image alt text, local asset
references, placeholder content, accidental secrets, and external links.

Network-dependent checks are opt-in:
    --check-links   verify every external URL
    --check-mcp     verify the six npm/MCP registry package entries

Exit code 0 means every requested check passed.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import html
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
MCP_CONFIG = ROOT / "tools" / "mcp_packages.json"
RESULTS_DIR = ROOT / "docs" / "evidence" / "test-results"
USER_AGENT = "dbsectrainer-profile-audit/1.0"

# These hosts intentionally challenge non-browser clients. They are reported
# as "blocked, allowed" instead of being treated as dead links.
ALLOWED_BLOCKED = {
    "www.linkedin.com": {999},
    "www.npmjs.com": {403},
}

LOCAL_REPO_BLOB_PREFIX = "https://github.com/dbsectrainer/dbsectrainer/blob/main/"

PLACEHOLDER_PATTERNS = [
    r"your\.email@example\.com",
    r"yourwebsite\.com",
    r"yourusername",
    r"\bexample\.com\b",
    r"\bTODO\b",
    r"\bTBD\b",
    r"lorem ipsum",
    r"\bplaceholder\b",
]

SECRET_PATTERNS = [
    ("AWS access key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("npm token", re.compile(r"\bnpm_[A-Za-z0-9]{36,}\b")),
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("Slack webhook", re.compile(r"https://hooks\.slack\.com/services/[A-Za-z0-9/]+")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
]

TEXT_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".json", ".txt", ".html", ".css", ".toml", ".sh", ".svg", ".xml"}
IGNORED_DIRS = {".git", "__pycache__", ".venv", "node_modules", "screenshots"}


@dataclass
class Check:
    name: str
    ok: bool
    detail: str = ""
    warnings: list[str] = field(default_factory=list)


@dataclass
class LinkResult:
    url: str
    status: int | None
    final_url: str
    ok: bool
    note: str = ""


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return "unknown"


def sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def lines_outside_fences(text: str):
    """Yield (line_number, line) for lines that are not inside a code fence."""
    in_fence = False
    for number, line in enumerate(text.splitlines(), 1):
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield number, line


def parse_anchors(text: str) -> list[dict]:
    anchors = []
    for number, line in lines_outside_fences(text):
        for match in re.finditer(r"<a\s+[^>]*\bid=[\"']([^\"']+)[\"'][^>]*>", line, re.I):
            anchors.append(
                {
                    "id": match.group(1),
                    "rendered_id": f"user-content-{match.group(1)}",
                    "line": number,
                }
            )
    return anchors


def parse_toc(text: str) -> list[dict]:
    entries: list[dict] = []
    in_toc = False
    for number, line in lines_outside_fences(text):
        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading and heading.group(1) == "##" and "Table of Contents" in heading.group(2):
            in_toc = True
            continue
        if in_toc and heading and heading.group(1) == "##":
            break
        if in_toc:
            for match in re.finditer(r"\[([^\]]+)\]\(#([^)]+)\)", line):
                entries.append(
                    {
                        "text": match.group(1).strip(),
                        "fragment": match.group(2).strip(),
                        "line": number,
                    }
                )
    return entries


def parse_headings(text: str) -> list[dict]:
    headings = []
    for number, line in lines_outside_fences(text):
        match = re.match(r"^(#{1,6})\s+(.*?)\s*$", line)
        if match:
            headings.append(
                {
                    "level": len(match.group(1)),
                    "text": match.group(2).strip(),
                    "line": number,
                }
            )
        for raw in re.finditer(r"<h([1-6])\b[^>]*>(.*?)</h\1>", line, re.I | re.S):
            raw_text = re.sub(r"<[^>]+>", "", raw.group(2))
            raw_text = html.unescape(raw_text).strip()
            headings.append(
                {
                    "level": int(raw.group(1)),
                    "text": raw_text,
                    "line": number,
                }
            )
    headings.sort(key=lambda heading: heading["line"])
    return headings


def parse_markdown_links(text: str) -> list[dict]:
    links = []
    for number, line in lines_outside_fences(text):
        for match in re.finditer(r"(?<!!)\[([^\]]+)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", line):
            links.append(
                {
                    "text": match.group(1).strip(),
                    "target": html.unescape(match.group(2).strip()),
                    "line": number,
                    "kind": "markdown",
                }
            )
    return links


def parse_html_refs(text: str) -> list[dict]:
    refs = []
    for number, line in lines_outside_fences(text):
        for match in re.finditer(r"<a\b[^>]*\bhref=[\"']([^\"']+)[\"'][^>]*>", line, re.I):
            refs.append(
                {
                    "text": "anchor",
                    "target": html.unescape(match.group(1).strip()),
                    "line": number,
                    "kind": "html-a",
                }
            )
    return refs


def parse_markdown_images(text: str) -> list[dict]:
    images = []
    for number, line in lines_outside_fences(text):
        for match in re.finditer(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", line):
            images.append(
                {
                    "alt": match.group(1),
                    "src": html.unescape(match.group(2).strip()),
                    "line": number,
                    "kind": "markdown",
                }
            )
    return images


def parse_html_images(text: str) -> list[dict]:
    images = []
    for number, line in lines_outside_fences(text):
        for match in re.finditer(r"<img\b[^>]*>", line, re.I):
            tag = match.group(0)
            src = re.search(r"\bsrc=[\"']([^\"']*)[\"']", tag, re.I)
            alt = re.search(r"\balt=[\"']([^\"']*)[\"']", tag, re.I)
            images.append(
                {
                    "alt": alt.group(1) if alt else None,
                    "src": html.unescape(src.group(1).strip()) if src else "",
                    "line": number,
                    "kind": "html",
                }
            )
    return images


def parse_readme(text: str) -> dict:
    return {
        "anchors": parse_anchors(text),
        "toc": parse_toc(text),
        "headings": parse_headings(text),
        "links": parse_markdown_links(text) + parse_html_refs(text),
        "images": parse_markdown_images(text) + parse_html_images(text),
    }


def check_placeholder_content(text: str) -> Check:
    found = []
    for pattern in PLACEHOLDER_PATTERNS:
        for match in re.finditer(pattern, text, re.I):
            line = text[: match.start()].count("\n") + 1
            found.append(f"line {line}: {match.group(0)!r}")
    return Check(
        "no placeholder content",
        not found,
        "; ".join(found) if found else "no placeholder markers",
    )


def check_trailing_whitespace(text: str) -> Check:
    bad = [f"line {number}" for number, line in enumerate(text.splitlines(), 1) if line != line.rstrip()]
    return Check(
        "no trailing whitespace",
        not bad,
        ", ".join(bad[:10]) + ("..." if len(bad) > 10 else "") if bad else "clean",
    )


def check_anchor_targets(parsed: dict) -> Check:
    anchor_ids = {a["rendered_id"] for a in parsed["anchors"]}
    duplicates = sorted({a["rendered_id"] for a in parsed["anchors"] if [b["rendered_id"] for b in parsed["anchors"]].count(a["rendered_id"]) > 1})
    missing = [entry for entry in parsed["toc"] if entry["fragment"] not in anchor_ids]
    details = []
    if duplicates:
        details.append(f"duplicate anchors: {', '.join(duplicates)}")
    if missing:
        details.append("unresolved TOC links: " + ", ".join(f"{m['text']} -> #{m['fragment']}" for m in missing))
    ok = not duplicates and not missing and bool(parsed["toc"])
    return Check(
        "TOC anchors resolve",
        ok,
        "; ".join(details) if details else f"{len(parsed['toc'])} TOC links resolve to {len(anchor_ids)} anchors",
    )


def check_heading_structure(parsed: dict, text: str) -> Check:
    headings = parsed["headings"]
    h1s = [h for h in headings if h["level"] == 1]
    problems = []
    if len(h1s) != 1:
        problems.append(f"expected exactly one H1, found {len(h1s)}")
    previous = 0
    for heading in headings:
        if previous and heading["level"] > previous + 1:
            problems.append(f"line {heading['line']}: H{previous} -> H{heading['level']} skips a level")
        previous = heading["level"]

    h2s = [h for h in headings if h["level"] == 2]
    toc_fragments = {entry["fragment"] for entry in parsed["toc"]}
    lines = text.splitlines()
    unanchored = []
    for heading in h2s:
        if "Table of Contents" in heading["text"]:
            continue
        index = heading["line"] - 1
        probe = index - 1
        while probe >= 0 and not lines[probe].strip():
            probe -= 1
        nearby = lines[probe] if probe >= 0 else ""
        anchor_match = re.search(r"<a\s+[^>]*\bid=[\"']([^\"']+)[\"']", nearby, re.I)
        if not anchor_match:
            unanchored.append(f"line {heading['line']}: {heading['text']}")
            continue
        fragment = f"user-content-{anchor_match.group(1)}"
        if fragment not in toc_fragments:
            problems.append(f"line {heading['line']}: {heading['text']} is missing from the TOC")
    if unanchored:
        problems.append("H2 sections without explicit anchors: " + "; ".join(unanchored))
    return Check(
        "heading hierarchy and section anchors",
        not problems,
        "; ".join(problems) if problems else f"{len(headings)} headings, one H1, every H2 anchored and in the TOC",
    )


def check_images(parsed: dict) -> Check:
    problems = []
    for image in parsed["images"]:
        if not image["src"]:
            problems.append(f"line {image['line']}: image has no src")
        if image["alt"] is None:
            problems.append(f"line {image['line']}: HTML image has no alt attribute")
        elif image["kind"] == "markdown" and not image["alt"].strip():
            problems.append(f"line {image['line']}: Markdown image has empty alt text")
    return Check(
        "images have alt text",
        not problems,
        "; ".join(problems) if problems else f"{len(parsed['images'])} images have alt attributes",
    )


def is_external(target: str) -> bool:
    return bool(re.match(r"^https?://", target, re.I))


def check_local_assets(parsed: dict) -> Check:
    missing = []
    checked = 0
    for item in parsed["links"] + parsed["images"]:
        target = item["target"] if "target" in item else item["src"]
        if not target or target.startswith("#") or is_external(target) or target.startswith("mailto:"):
            continue
        path_part = urllib.parse.urlsplit(target).path
        if not path_part:
            continue
        checked += 1
        candidate = (ROOT / path_part.lstrip("/")).resolve()
        if not str(candidate).startswith(str(ROOT)):
            missing.append(f"{target} escapes the repository")
        elif not candidate.exists():
            missing.append(f"{target} does not exist")
    return Check(
        "local assets and links exist",
        not missing,
        "; ".join(missing) if missing else f"{checked} local references checked",
    )


def scan_secrets() -> Check:
    findings = []
    scanned = 0
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        scanned += 1
        for label, pattern in SECRET_PATTERNS:
            for match in pattern.finditer(text):
                line = text[: match.start()].count("\n") + 1
                findings.append(f"{path.relative_to(ROOT)}:{line}: possible {label}")
    return Check(
        "no committed secrets",
        not findings,
        "; ".join(findings) if findings else f"{scanned} text files scanned; no secret patterns",
    )


def check_svgs() -> Check:
    problems = []
    svg_paths = sorted((ROOT / "docs" / "archive" / "legacy-svg").glob("*.svg"))
    for path in svg_paths:
        try:
            root = ET.fromstring(path.read_text(encoding="utf-8"))
        except Exception as exc:
            problems.append(f"{path.name}: invalid XML ({exc})")
            continue
        if not root.tag.endswith("svg"):
            problems.append(f"{path.name}: root element is not <svg>")
        if not root.get("width") or not root.get("height"):
            problems.append(f"{path.name}: missing width/height")
        raw = path.read_text(encoding="utf-8").lower()
        if "<script" in raw or re.search(r"\son[a-z]+\s*=", raw):
            problems.append(f"{path.name}: contains script or event handler")
        if re.search(r"(?:href|src)=[\"']https?://", raw):
            problems.append(f"{path.name}: references an external resource")
    return Check(
        "archived SVG assets are well formed",
        not problems,
        "; ".join(problems) if problems else f"{len(svg_paths)} SVG files parse and contain no active content",
    )


def external_urls(parsed: dict) -> list[str]:
    urls = set()
    for item in parsed["links"]:
        if is_external(item["target"]):
            urls.add(item["target"])
    for image in parsed["images"]:
        if is_external(image["src"]):
            urls.add(image["src"])
    return sorted(urls)


def fetch_status(url: str, retries: int = 2) -> LinkResult:
    if url.startswith(LOCAL_REPO_BLOB_PREFIX):
        relative = url[len(LOCAL_REPO_BLOB_PREFIX):].split("#", 1)[0].split("?", 1)[0]
        target = (ROOT / relative).resolve()
        if str(target).startswith(str(ROOT)) and target.exists():
            return LinkResult(
                url,
                None,
                url,
                True,
                "repository file exists locally; remote publish is pending",
            )
        return LinkResult(url, None, url, False, f"repository file not found: {relative}")

    last_error = ""
    for attempt in range(retries + 1):
        request = urllib.request.Request(
            url,
            headers={"User-Agent": USER_AGENT, "Accept": "*/*"},
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=25) as response:
                response.read(1024)
                status = response.status
                final_url = response.geturl()
            host = urllib.parse.urlsplit(final_url).hostname or ""
            allowed = ALLOWED_BLOCKED.get(host, set())
            if 200 <= status < 400:
                return LinkResult(url, status, final_url, True, "")
            if status in allowed:
                return LinkResult(url, status, final_url, True, f"{host} blocks automated clients (allowed)")
            return LinkResult(url, status, final_url, False, f"HTTP {status}")
        except urllib.error.HTTPError as exc:
            host = urllib.parse.urlsplit(url).hostname or ""
            allowed = ALLOWED_BLOCKED.get(host, set())
            if exc.code in allowed:
                return LinkResult(url, exc.code, url, True, f"{host} blocks automated clients (allowed)")
            last_error = f"HTTP {exc.code}"
            if exc.code < 500 and exc.code != 429:
                return LinkResult(url, exc.code, url, False, last_error)
        except Exception as exc:  # noqa: BLE001 - report the actual network error
            last_error = f"{type(exc).__name__}: {exc}"
        if attempt < retries:
            time.sleep(1.5 * (attempt + 1))
    return LinkResult(url, None, url, False, last_error or "request failed")


def check_links(parsed: dict, workers: int = 8) -> tuple[Check, list[LinkResult]]:
    urls = external_urls(parsed)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(fetch_status, urls))
    failures = [r for r in results if not r.ok]
    allowed = [r for r in results if r.ok and r.note]
    detail = f"{len(results)} external URLs checked"
    if allowed:
        detail += f"; {len(allowed)} allowed bot-blocked"
    if failures:
        detail += "; failures: " + "; ".join(f"{r.url} ({r.note})" for r in failures)
    return Check("external links resolve", not failures, detail), results


def check_mcp(parsed: dict) -> tuple[Check, list[dict]]:
    if not MCP_CONFIG.exists():
        return Check("MCP package metadata", False, f"missing {MCP_CONFIG.relative_to(ROOT)}"), []
    config = json.loads(MCP_CONFIG.read_text(encoding="utf-8"))
    packages = config.get("packages", [])
    problems = []
    observations = []
    readme_text = README.read_text(encoding="utf-8")
    for package in packages:
        name = package["name"]
        npm_link = f"https://www.npmjs.com/package/{name}"
        if npm_link not in readme_text:
            problems.append(f"{name}: npm link missing from README")
        if package["repo"] not in readme_text:
            problems.append(f"{name}: repository link missing from README")
        try:
            with urllib.request.urlopen(
                urllib.request.Request(
                    f"https://registry.npmjs.org/{urllib.parse.quote(name)}",
                    headers={"User-Agent": USER_AGENT},
                ),
                timeout=25,
            ) as response:
                npm_data = json.load(response)
            latest = npm_data.get("dist-tags", {}).get("latest")
            maintainers = {m.get("name") for m in npm_data.get("maintainers", [])}
            if not latest:
                problems.append(f"{name}: npm package has no latest version")
            if "dbsectrainer" not in maintainers:
                problems.append(f"{name}: dbsectrainer is not an npm maintainer")
            npm_observation = {"latest": latest, "maintainers": sorted(maintainers)}
        except Exception as exc:  # noqa: BLE001
            problems.append(f"{name}: npm registry lookup failed ({exc})")
            npm_observation = {"error": str(exc)}

        try:
            with urllib.request.urlopen(
                urllib.request.Request(
                    f"https://registry.modelcontextprotocol.io/v0/servers?search={urllib.parse.quote(name)}&limit=10",
                    headers={"User-Agent": USER_AGENT},
                ),
                timeout=25,
            ) as response:
                registry_data = json.load(response)
            names = [entry.get("server", {}).get("name") for entry in registry_data.get("servers", [])]
            if package["registry_id"] not in names:
                problems.append(f"{name}: {package['registry_id']} not found in the official MCP registry")
            registry_observation = {"names": names}
        except Exception as exc:  # noqa: BLE001
            problems.append(f"{name}: MCP registry lookup failed ({exc})")
            registry_observation = {"error": str(exc)}

        observations.append(
            {
                "name": name,
                "repo": package["repo"],
                "npm": npm_observation,
                "mcp_registry": registry_observation,
            }
        )
    return Check(
        "MCP package metadata",
        not problems,
        "; ".join(problems) if problems else f"{len(packages)} packages found on npm and in the official MCP registry",
    ), observations


def write_results(checks: list[Check], links: list[LinkResult], mcp: list[dict], payload: dict) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output = RESULTS_DIR / "profile-validation.json"
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "commit": git_commit(),
        "readme_sha256": sha256(README),
        **payload,
        "checks": [asdict(check) for check in checks],
        "links": [asdict(link) for link in links],
        "mcp_packages": mcp,
        "ok": all(check.ok for check in checks),
    }
    output.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-links", action="store_true", help="verify every external URL")
    parser.add_argument("--check-mcp", action="store_true", help="verify npm and MCP registry package entries")
    parser.add_argument("--json-out", type=Path, default=None, help="write the JSON result to this path")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    text = README.read_text(encoding="utf-8")
    parsed = parse_readme(text)

    checks = [
        check_placeholder_content(text),
        check_trailing_whitespace(text),
        check_anchor_targets(parsed),
        check_heading_structure(parsed, text),
        check_images(parsed),
        check_local_assets(parsed),
        scan_secrets(),
        check_svgs(),
    ]

    links: list[LinkResult] = []
    mcp: list[dict] = []
    if args.check_links:
        link_check, links = check_links(parsed)
        checks.append(link_check)
    if args.check_mcp:
        mcp_check, mcp = check_mcp(parsed)
        checks.append(mcp_check)

    for check in checks:
        status = "PASS" if check.ok else "FAIL"
        if not args.quiet:
            print(f"[{status}] {check.name}: {check.detail}")
            for warning in check.warnings:
                print(f"       warning: {warning}")

    payload = {}
    output = write_results(checks, links, mcp, payload)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(output.read_text(encoding="utf-8"), encoding="utf-8")

    failures = [check for check in checks if not check.ok]
    if not args.quiet:
        print(f"\n{len(checks) - len(failures)}/{len(checks)} checks passed")
        print(f"JSON result: {output.relative_to(ROOT)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
