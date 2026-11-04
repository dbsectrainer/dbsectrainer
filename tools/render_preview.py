#!/usr/bin/env python3
"""Render README.md through GitHub's Markdown API and build a local preview.

The preview is deliberately explicit about what it is: the Markdown HTML comes
from GitHub's own `/markdown` API, while the surrounding profile chrome is a
small local harness. It is not a capture of github.com and is never presented
as one.
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import shutil
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
OUT_DIR = ROOT / "docs" / "evidence" / "build-results"
VENDOR_CSS = ROOT / "tools" / "vendor" / "github-markdown.css"
USER_AGENT = "dbsectrainer-profile-preview/1.0"
GITHUB_API = "https://api.github.com"
CONTEXT = "dbsectrainer/dbsectrainer"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def request_json(url: str) -> dict:
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": USER_AGENT}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.load(response)


def render_markdown(text: str) -> tuple[str, int]:
    payload = json.dumps({"text": text, "mode": "gfm", "context": CONTEXT}).encode("utf-8")
    headers = {
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        f"{GITHUB_API}/markdown", data=payload, headers=headers, method="POST"
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8"), response.status


def download(url: str, destination: Path, timeout: int = 45) -> bool:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = response.read()
            if not data:
                return False
            destination.write_bytes(data)
            return True
    except Exception:
        return False


def profile_snapshot() -> dict:
    fallback = {
        "name": "Donnivis Baker",
        "login": "dbsectrainer",
        "bio": "Senior Software Engineer | Cloud & Security Architect | DevOps Leader",
        "public_repos": None,
        "followers": None,
        "source": "fallback",
    }
    try:
        data = request_json(f"{GITHUB_API}/users/dbsectrainer")
        return {
            "name": data.get("name") or fallback["name"],
            "login": data.get("login") or fallback["login"],
            "bio": data.get("bio") or fallback["bio"],
            "public_repos": data.get("public_repos"),
            "followers": data.get("followers"),
            "avatar_url": data.get("avatar_url"),
            "source": "github-api",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception:
        return fallback


def build_page(rendered_html: str, profile: dict, commit: str) -> str:
    name = html.escape(str(profile.get("name") or "Donnivis Baker"))
    login = html.escape(str(profile.get("login") or "dbsectrainer"))
    bio = html.escape(str(profile.get("bio") or ""))
    meta_parts = []
    if profile.get("public_repos") is not None:
        meta_parts.append(f"{profile['public_repos']} public repositories")
    if profile.get("followers") is not None:
        meta_parts.append(f"{profile['followers']} followers")
    meta = html.escape(" · ".join(meta_parts))
    avatar_path = OUT_DIR / "avatar.png"
    if avatar_path.exists():
        avatar = (
            '<img class="avatar" src="avatar.png" width="296" height="296" '
            f'alt="Portrait of {name}">'
        )
    else:
        avatar = '<div class="avatar avatar-fallback" aria-hidden="true">DB</div>'
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <title>{name} ({login}) — GitHub profile preview</title>
  <link rel="icon" href="data:,">
  <link rel="stylesheet" href="github-markdown.css">
  <style>
    :root {{
      --page-bg: #f6f8fa;
      --card-bg: #ffffff;
      --border: #d0d7de;
      --muted: #59636e;
      --text: #1f2328;
      --link: #0969da;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--page-bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
    }}
    .preview-banner {{
      background: #fff8c5;
      border-bottom: 1px solid #d4a72c;
      color: var(--text);
      font-size: 12px;
      line-height: 1.5;
      padding: 8px 16px;
      text-align: center;
    }}
    .profile-shell {{
      display: grid;
      grid-template-columns: 296px minmax(0, 1fr);
      gap: 32px;
      margin: 0 auto;
      max-width: 1280px;
      padding: 32px 24px 16px;
    }}
    .profile-sidebar {{ align-self: start; min-width: 0; }}
    .avatar {{
      border: 1px solid var(--border);
      border-radius: 50%;
      display: block;
      height: auto;
      max-width: 296px;
      width: 100%;
    }}
    .avatar-fallback {{
      align-items: center;
      background: #ddf4ff;
      color: #0550ae;
      display: flex;
      font-size: 64px;
      font-weight: 700;
      height: 296px;
      justify-content: center;
    }}
    .profile-name {{ font-size: 24px; font-weight: 600; line-height: 1.25; margin: 16px 0 0; }}
    .profile-login {{ color: var(--muted); font-size: 20px; font-weight: 300; margin: 0 0 16px; }}
    .profile-bio {{ font-size: 16px; line-height: 1.5; margin: 0 0 16px; }}
    .profile-meta {{ color: var(--muted); font-size: 14px; margin: 0 0 12px; }}
    .profile-link {{ color: var(--link); font-size: 14px; text-decoration: none; }}
    .profile-link:hover {{ text-decoration: underline; }}
    .readme-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 6px;
      min-width: 0;
      overflow: hidden;
    }}
    .readme-header {{
      background: #f6f8fa;
      border-bottom: 1px solid var(--border);
      color: var(--muted);
      font-size: 14px;
      padding: 12px 16px;
    }}
    .readme-header a {{ color: var(--link); text-decoration: none; }}
    .readme-header a:hover {{ text-decoration: underline; }}
    .markdown-body {{ padding: 32px 40px; }}
    .page-footer {{
      color: var(--muted);
      font-size: 12px;
      line-height: 1.6;
      margin: 0 auto;
      max-width: 1280px;
      padding: 8px 24px 32px;
    }}
    @media (max-width: 900px) {{
      .profile-shell {{
        gap: 20px;
        grid-template-columns: minmax(0, 1fr);
        padding: 16px 12px 8px;
      }}
      .profile-sidebar {{
        align-items: center;
        display: flex;
        flex-wrap: wrap;
        gap: 12px 16px;
        min-width: 0;
      }}
      .avatar {{ max-width: 80px; width: 80px; }}
      .avatar-fallback {{ flex: 0 0 80px; font-size: 24px; height: 80px; }}
      .profile-name {{ font-size: 20px; margin: 0; min-width: 0; overflow-wrap: anywhere; }}
      .profile-login {{ font-size: 16px; margin: 0; min-width: 0; }}
      .profile-bio, .profile-meta {{ display: none; }}
      .profile-link {{ margin-left: auto; white-space: nowrap; }}
      .markdown-body {{ padding: 24px 16px; }}
      .markdown-body table {{
        display: table;
        font-size: 14px;
        table-layout: auto;
        width: 100%;
      }}
      .markdown-body th,
      .markdown-body td {{
        overflow-wrap: break-word;
        padding: 5px 7px;
        white-space: normal;
        word-break: normal;
      }}
      .markdown-body th:first-child,
      .markdown-body td:first-child {{
        width: 32%;
      }}
      .markdown-body pre {{
        white-space: pre-wrap;
        word-break: break-word;
      }}
      .page-footer {{ padding: 8px 12px 24px; }}
    }}
  </style>
</head>
<body>
  <div class="preview-banner" role="note">
    <strong>Local preview</strong> — README HTML rendered by GitHub's Markdown API.
    The surrounding profile layout is a local harness, not the live github.com page.
  </div>
  <div class="profile-shell">
    <aside class="profile-sidebar" aria-label="Profile summary">
      {avatar}
      <p class="profile-name">{name}</p>
      <p class="profile-login">{login}</p>
      <p class="profile-bio">{bio}</p>
      <p class="profile-meta">{meta}</p>
      <a class="profile-link" href="https://github.com/{login}">View GitHub profile →</a>
    </aside>
    <main class="readme-card">
      <div class="readme-header"><a href="https://github.com/{login}">{login}</a> / README.md</div>
      <article class="markdown-body">
        {rendered_html.strip()}
      </article>
    </main>
  </div>
  <footer class="page-footer">
    Generated from <code>README.md</code> at commit {commit[:12]} on {generated}.
    Markdown HTML: GitHub <code>/markdown</code> API. Layout: local preview harness.
    This is not a github.com capture.
  </footer>
</body>
</html>
"""


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not VENDOR_CSS.exists():
        print(f"error: missing {VENDOR_CSS.relative_to(ROOT)}", file=sys.stderr)
        return 2

    source = README.read_text(encoding="utf-8")
    try:
        rendered, status = render_markdown(source)
    except urllib.error.HTTPError as exc:
        print(f"error: GitHub Markdown API returned HTTP {exc.code}", file=sys.stderr)
        if exc.code == 403:
            print("hint: unauthenticated API limits may be exhausted; set GITHUB_TOKEN", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"error: GitHub Markdown API request failed: {exc}", file=sys.stderr)
        return 1

    if not rendered.strip():
        print("error: GitHub Markdown API returned an empty document", file=sys.stderr)
        return 1

    (OUT_DIR / "readme-rendered.html").write_text(rendered, encoding="utf-8")
    shutil.copyfile(VENDOR_CSS, OUT_DIR / "github-markdown.css")

    profile = profile_snapshot()
    avatar_url = profile.get("avatar_url") or "https://github.com/dbsectrainer.png?size=460"
    download(avatar_url, OUT_DIR / "avatar.png")
    (OUT_DIR / "profile-snapshot.json").write_text(
        json.dumps(profile, indent=2) + "\n", encoding="utf-8"
    )

    commit = "unknown"
    try:
        import subprocess

        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        pass

    page = build_page(rendered, profile, commit)
    preview_path = OUT_DIR / "preview.html"
    preview_path.write_text(page, encoding="utf-8")

    ids = set(re.findall(r'\bid="([^"]+)"', rendered))
    toc_targets = sorted(set(re.findall(r'href="#([^"]+)"', rendered)))
    missing = [target for target in toc_targets if target not in ids]
    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "commit": commit,
        "readme_sha256": sha256_bytes(source.encode("utf-8")),
        "rendered_html_sha256": sha256_bytes(rendered.encode("utf-8")),
        "preview_html_sha256": sha256_bytes(page.encode("utf-8")),
        "api": f"{GITHUB_API}/markdown",
        "api_status": status,
        "rendered_bytes": len(rendered.encode("utf-8")),
        "preview_bytes": len(page.encode("utf-8")),
        "anchors": sorted(ids),
        "toc_targets": toc_targets,
        "missing_targets": missing,
        "profile_source": profile.get("source"),
        "avatar_downloaded": (OUT_DIR / "avatar.png").exists(),
    }
    (OUT_DIR / "render-metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    print(f"GitHub Markdown API: HTTP {status}; rendered {metadata['rendered_bytes']} bytes")
    print(f"Preview: {preview_path.relative_to(ROOT)}")
    print(f"TOC targets: {len(toc_targets)}; missing: {len(missing)}")
    if missing:
        print("error: unresolved rendered anchors: " + ", ".join(missing), file=sys.stderr)
        return 1
    print("PASS: every TOC target exists in the GitHub-rendered HTML")
    return 0


if __name__ == "__main__":
    sys.exit(main())
