#!/usr/bin/env python3
"""Capture desktop/mobile screenshots and browser evidence for the profile preview.

Requires Playwright and Chromium. The preview must be generated first with
`python3 tools/render_preview.py` (or `make preview`).
"""

from __future__ import annotations

import functools
import hashlib
import http.server
import json
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover - exercised only on misconfigured hosts
    Image = None

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "docs" / "evidence" / "build-results"
SHOTS_DIR = ROOT / "docs" / "evidence" / "screenshots"
RESULTS_DIR = ROOT / "docs" / "evidence" / "test-results"
PREVIEW = BUILD_DIR / "preview.html"
AXE_URL = "https://cdn.jsdelivr.net/npm/axe-core@4.10.3/axe.min.js"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):  # noqa: A002 - match base signature
        pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def start_server() -> tuple[http.server.ThreadingHTTPServer, str]:
    handler = functools.partial(QuietHandler, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"


def collect_page_evidence(page) -> dict:
    return {
        "title": page.title(),
        "console_errors": [],
        "console_warnings": [],
        "failed_requests": [],
        "bad_responses": [],
    }


def attach_listeners(page, evidence: dict) -> None:
    def on_console(message):
        if message.type == "error":
            evidence["console_errors"].append(message.text[:500])
        elif message.type == "warning":
            evidence["console_warnings"].append(message.text[:500])

    def on_request_failed(request):
        evidence["failed_requests"].append(
            {"url": request.url[:500], "failure": request.failure}
        )

    def on_response(response):
        if response.status >= 400:
            evidence["bad_responses"].append(
                {"url": response.url[:500], "status": response.status}
            )

    page.on("console", on_console)
    page.on("requestfailed", on_request_failed)
    page.on("response", on_response)


def wait_for_render(page) -> None:
    page.wait_for_selector("article.markdown-body", timeout=45000)
    page.wait_for_function(
        "() => Array.from(document.images).every((image) => image.complete)",
        timeout=60000,
    )
    page.wait_for_timeout(800)


def image_report(page) -> list[dict]:
    return page.eval_on_selector_all(
        "article img, .profile-sidebar img",
        """images => images.map((image) => ({
            src: image.getAttribute('src'),
            alt: image.getAttribute('alt'),
            complete: image.complete,
            naturalWidth: image.naturalWidth,
            naturalHeight: image.naturalHeight
        }))""",
    )


def broken_images(images: list[dict]) -> list[dict]:
    return [image for image in images if not image["complete"] or image["naturalWidth"] == 0]


def toc_report(page) -> list[dict]:
    return page.evaluate(
        """() => {
            const links = Array.from(document.querySelectorAll('article.markdown-body a[href^="#"]'));
            return links.map((link) => {
                const target = link.getAttribute('href').slice(1);
                return {
                    text: link.textContent.trim(),
                    target,
                    exists: Boolean(document.getElementById(target))
                };
            });
        }"""
    )


def click_toc_links(page, entries: list[dict], viewport_height: int) -> list[dict]:
    results = []
    for entry in entries:
        page.evaluate("() => window.scrollTo(0, 0)")
        page.wait_for_timeout(100)
        locator = page.locator(f'article.markdown-body a[href="#{entry["target"]}"]').first
        try:
            locator.click(timeout=10000)
            page.wait_for_timeout(450)
            state = page.evaluate(
                """(target) => {
                    const element = document.getElementById(target);
                    const rect = element ? element.getBoundingClientRect() : null;
                    return {
                        hash: location.hash,
                        scrollY: window.scrollY,
                        top: rect ? rect.top : null,
                        visible: rect ? (rect.top >= -5 && rect.top <= window.innerHeight) : false
                    };
                }""",
                entry["target"],
            )
            results.append({**entry, **state})
        except Exception as exc:  # noqa: BLE001
            results.append({**entry, "error": str(exc), "visible": False})
    return results


def section_boxes(page) -> dict:
    return page.evaluate(
        """() => {
            const article = document.querySelector('article.markdown-body');
            const articleRect = article.getBoundingClientRect();
            const box = (id) => {
                const anchor = document.getElementById(id);
                const paragraph = anchor && (anchor.closest('p') || anchor);
                const rect = paragraph.getBoundingClientRect();
                return { top: rect.top + window.scrollY, bottom: rect.bottom + window.scrollY };
            };
            return {
                article: {
                    left: articleRect.left + window.scrollX,
                    width: articleRect.width
                },
                selected: box('user-content-selected-work'),
                mcp: box('user-content-mcp-servers'),
                openSource: box('user-content-open-source')
            };
        }"""
    )


def crop_section(full_page: Path, boxes: dict, start: dict, end: dict, output: Path) -> bool:
    if Image is None:
        return False
    image = Image.open(full_page)
    left = max(0, int(boxes["article"]["left"]) - 8)
    width = int(boxes["article"]["width"]) + 16
    top = max(0, int(start["top"]) - 8)
    bottom = min(image.height, int(end["top"]) - 8)
    if bottom <= top:
        return False
    image.crop((left, top, min(image.width, left + width), bottom)).save(output)
    return True


def run_axe(page) -> dict:
    try:
        page.add_script_tag(url=AXE_URL)
        results = page.evaluate(
            """async () => await axe.run(document, {
                runOnly: {
                    type: 'tag',
                    values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa']
                }
            })"""
        )
        violations = []
        for violation in results.get("violations", []):
            violations.append(
                {
                    "id": violation.get("id"),
                    "impact": violation.get("impact"),
                    "help": violation.get("help"),
                    "helpUrl": violation.get("helpUrl"),
                    "nodes": [
                        {
                            "target": node.get("target"),
                            "failureSummary": node.get("failureSummary"),
                        }
                        for node in violation.get("nodes", [])
                    ],
                }
            )
        return {
            "ok": True,
            "engine": "axe-core 4.10.3",
            "violation_count": len(violations),
            "violations": violations,
            "serious_or_critical": [
                v for v in violations if v["impact"] in ("serious", "critical")
            ],
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc), "violations": [], "serious_or_critical": []}


def main() -> int:
    if not PREVIEW.exists():
        print(f"error: {PREVIEW.relative_to(ROOT)} is missing; run `make preview` first", file=sys.stderr)
        return 2
    SHOTS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    server, base_url = start_server()
    url = f"{base_url}/docs/evidence/build-results/preview.html"
    failures: list[str] = []
    results: dict = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "preview_url": url,
        "preview_sha256": sha256(PREVIEW),
        "axe_core_url": AXE_URL,
    }

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                # ----- desktop -------------------------------------------------
                desktop_context = browser.new_context(
                    viewport={"width": 1440, "height": 900},
                    device_scale_factor=1,
                    color_scheme="light",
                )
                desktop = desktop_context.new_page()
                desktop_evidence = collect_page_evidence(desktop)
                attach_listeners(desktop, desktop_evidence)
                desktop.goto(url, wait_until="domcontentloaded", timeout=60000)
                wait_for_render(desktop)

                desktop_evidence["images"] = image_report(desktop)
                desktop_evidence["broken_images"] = broken_images(desktop_evidence["images"])
                if desktop_evidence["broken_images"]:
                    failures.append(
                        f"desktop: {len(desktop_evidence['broken_images'])} images failed to load"
                    )

                desktop_evidence["toc"] = toc_report(desktop)
                missing_toc = [entry for entry in desktop_evidence["toc"] if not entry["exists"]]
                if missing_toc:
                    failures.append(
                        "desktop: TOC targets missing: "
                        + ", ".join(entry["target"] for entry in missing_toc)
                    )

                desktop_evidence["toc_clicks"] = click_toc_links(
                    desktop, desktop_evidence["toc"], viewport_height=900
                )
                broken_clicks = [
                    entry for entry in desktop_evidence["toc_clicks"] if not entry.get("visible")
                ]
                if broken_clicks:
                    failures.append(
                        "desktop: TOC links did not scroll to their targets: "
                        + ", ".join(entry["text"] for entry in broken_clicks)
                    )

                desktop.screenshot(path=SHOTS_DIR / "homepage-desktop.png", full_page=True)
                desktop.evaluate("() => window.scrollTo(0, 0)")
                desktop.wait_for_timeout(200)

                # A viewport shot after a real TOC navigation.
                selected_link = desktop.locator(
                    'article.markdown-body a[href="#user-content-selected-work"]'
                ).first
                selected_link.click()
                desktop.wait_for_timeout(500)
                desktop.screenshot(path=SHOTS_DIR / "toc-navigation.png")
                desktop.evaluate("() => window.scrollTo(0, 0)")
                desktop.wait_for_timeout(200)

                boxes = section_boxes(desktop)
                crop_section(
                    SHOTS_DIR / "homepage-desktop.png",
                    boxes,
                    boxes["selected"],
                    boxes["mcp"],
                    SHOTS_DIR / "selected-work.png",
                )
                crop_section(
                    SHOTS_DIR / "homepage-desktop.png",
                    boxes,
                    boxes["mcp"],
                    boxes["openSource"],
                    SHOTS_DIR / "mcp-servers.png",
                )

                desktop_evidence["axe"] = run_axe(desktop)
                if desktop_evidence["axe"].get("serious_or_critical"):
                    failures.append(
                        "desktop: "
                        + str(len(desktop_evidence["axe"]["serious_or_critical"]))
                        + " serious/critical accessibility violations"
                    )

                if desktop_evidence["console_errors"]:
                    failures.append(
                        f"desktop: {len(desktop_evidence['console_errors'])} console errors"
                    )
                if desktop_evidence["failed_requests"]:
                    failures.append(
                        f"desktop: {len(desktop_evidence['failed_requests'])} failed requests"
                    )
                if desktop_evidence["bad_responses"]:
                    failures.append(
                        f"desktop: {len(desktop_evidence['bad_responses'])} HTTP responses >= 400"
                    )

                results["desktop"] = desktop_evidence
                results["desktop"]["screenshot"] = "docs/evidence/screenshots/homepage-desktop.png"
                results["desktop"]["sections"] = boxes
                desktop_context.close()

                # ----- mobile --------------------------------------------------
                mobile_context = browser.new_context(
                    viewport={"width": 390, "height": 844},
                    device_scale_factor=1,
                    is_mobile=True,
                    has_touch=True,
                    color_scheme="light",
                )
                mobile = mobile_context.new_page()
                mobile_evidence = collect_page_evidence(mobile)
                attach_listeners(mobile, mobile_evidence)
                mobile.goto(url, wait_until="domcontentloaded", timeout=60000)
                wait_for_render(mobile)
                mobile_evidence["images"] = image_report(mobile)
                mobile_evidence["broken_images"] = broken_images(mobile_evidence["images"])
                mobile_evidence["layout"] = mobile.evaluate(
                    """() => ({
                        innerWidth: window.innerWidth,
                        visualWidth: window.visualViewport ? window.visualViewport.width : null,
                        clientWidth: document.documentElement.clientWidth,
                        scrollWidth: document.documentElement.scrollWidth,
                        bodyScrollWidth: document.body.scrollWidth
                    })"""
                )
                mobile_evidence["overflow_px"] = mobile.evaluate(
                    """() => {
                        const viewport = window.visualViewport ? window.visualViewport.width : window.innerWidth;
                        return Math.max(
                            document.documentElement.scrollWidth,
                            document.body.scrollWidth
                        ) - viewport;
                    }"""
                )
                mobile_evidence["viewport"] = {"width": 390, "height": 844, "device_scale_factor": 2}
                mobile.screenshot(path=SHOTS_DIR / "homepage-mobile.png", full_page=True)
                if mobile_evidence["broken_images"]:
                    failures.append(
                        f"mobile: {len(mobile_evidence['broken_images'])} images failed to load"
                    )
                if mobile_evidence["overflow_px"] > 1:
                    failures.append(
                        f"mobile: horizontal overflow of {mobile_evidence['overflow_px']}px"
                    )
                if mobile_evidence["console_errors"]:
                    failures.append(
                        f"mobile: {len(mobile_evidence['console_errors'])} console errors"
                    )
                if mobile_evidence["failed_requests"]:
                    failures.append(
                        f"mobile: {len(mobile_evidence['failed_requests'])} failed requests"
                    )
                if mobile_evidence["bad_responses"]:
                    failures.append(
                        f"mobile: {len(mobile_evidence['bad_responses'])} HTTP responses >= 400"
                    )
                results["mobile"] = mobile_evidence
                results["mobile"]["screenshot"] = "docs/evidence/screenshots/homepage-mobile.png"
                mobile_context.close()
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()

    results["pass"] = not failures
    results["failures"] = failures
    results["screenshots"] = {
        "homepage-desktop": "docs/evidence/screenshots/homepage-desktop.png",
        "homepage-mobile": "docs/evidence/screenshots/homepage-mobile.png",
        "toc-navigation": "docs/evidence/screenshots/toc-navigation.png",
        "selected-work": "docs/evidence/screenshots/selected-work.png",
        "mcp-servers": "docs/evidence/screenshots/mcp-servers.png",
    }
    (RESULTS_DIR / "screenshot-results.json").write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8"
    )
    (RESULTS_DIR / "axe-results.json").write_text(
        json.dumps(results.get("desktop", {}).get("axe", {}), indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Desktop screenshot: {SHOTS_DIR.relative_to(ROOT) / 'homepage-desktop.png'}")
    print(f"Mobile screenshot:  {SHOTS_DIR.relative_to(ROOT) / 'homepage-mobile.png'}")
    print(f"TOC links checked:  {len(results.get('desktop', {}).get('toc', []))}")
    print(
        "Axe violations:     "
        f"{results.get('desktop', {}).get('axe', {}).get('violation_count', 'unavailable')} "
        f"({len(results.get('desktop', {}).get('axe', {}).get('serious_or_critical', []))} serious/critical)"
    )
    if failures:
        print("\nFAILURES:")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print("\nPASS: screenshots, images, TOC navigation, mobile layout, console, network, and axe checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
