#!/usr/bin/env python3
"""Verify the published GitHub profile on github.com.

This complements the local GitHub-Markdown-API preview: it checks the actual
profile page after deployment, exercises every table-of-contents link in a real
browser, captures clean header/TOC screenshots, and records console/network
evidence.

Requires network access and Playwright with Chromium. It is intentionally not
part of `make check` because it validates the deployed profile, not the source
tree.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SCREENSHOT_DIR = ROOT / "docs" / "evidence" / "screenshots" / "live"
RESULTS_DIR = ROOT / "docs" / "evidence" / "test-results"


def capture(desktop_page, mobile_page, url: str) -> dict:
    out: dict = {"url": url, "generated_at": datetime.now(timezone.utc).isoformat()}

    desktop_page.goto(url, wait_until="domcontentloaded", timeout=60000)
    desktop_page.wait_for_selector("article.markdown-body", timeout=60000)
    desktop_page.wait_for_timeout(2500)

    out["title"] = desktop_page.title()
    out["content"] = desktop_page.evaluate(
        """() => {
            const article = document.querySelector('article.markdown-body');
            return {
                has_selected_work: article.innerText.includes('Selected Work'),
                has_aegis: article.innerText.includes('AEGIS'),
                h1: article.querySelector('h1')?.innerText || null
            };
        }"""
    )
    out["h1_visible"] = desktop_page.evaluate(
        """() => {
            const heading = document.querySelector('article.markdown-body h1');
            if (!heading) return false;
            const rect = heading.getBoundingClientRect();
            const x = rect.left + rect.width / 2;
            const y = rect.top + rect.height / 2;
            return rect.top >= 0 && rect.bottom <= window.innerHeight
                && document.elementsFromPoint(x, y)[0].closest('h1') === heading;
        }"""
    )
    out["images"] = desktop_page.eval_on_selector_all(
        "article.markdown-body img",
        """images => images.map((image) => ({
            src: image.getAttribute('src'),
            alt: image.getAttribute('alt'),
            complete: image.complete,
            naturalWidth: image.naturalWidth
        }))""",
    )
    out["broken_images"] = [
        image["src"]
        for image in out["images"]
        if not image["complete"] or image["naturalWidth"] == 0
    ]
    out["toc"] = desktop_page.eval_on_selector_all(
        'article.markdown-body a[href^="#user-content-"]',
        """links => links.map((link) => ({
            text: link.textContent.trim(),
            href: link.getAttribute('href')
        }))""",
    )

    clicks = []
    for entry in out["toc"]:
        page_target = entry["href"][1:]
        desktop_page.evaluate("() => window.scrollTo(0, 0)")
        desktop_page.wait_for_timeout(150)
        desktop_page.locator(
            f'article.markdown-body a[href="{entry["href"]}"]'
        ).first.click()
        desktop_page.wait_for_timeout(500)
        clicks.append(
            desktop_page.evaluate(
                """(target) => {
                    const element = document.getElementById(target);
                    const rect = element ? element.getBoundingClientRect() : null;
                    return {
                        target,
                        hash: location.hash,
                        scrollY: window.scrollY,
                        top: rect ? rect.top : null,
                        visible: rect ? (rect.top >= -5 && rect.top <= window.innerHeight) : false
                    };
                }""",
                page_target,
            )
        )
    out["toc_clicks"] = clicks

    desktop_page.evaluate("() => window.scrollTo(0, 0)")
    desktop_page.wait_for_timeout(700)
    desktop_page.screenshot(path=SCREENSHOT_DIR / "live-profile-header-desktop.png")
    desktop_page.locator(
        'article.markdown-body a[href="#user-content-selected-work"]'
    ).first.click()
    desktop_page.wait_for_timeout(700)
    desktop_page.screenshot(path=SCREENSHOT_DIR / "live-profile-toc-desktop.png")

    mobile_page.goto(url, wait_until="domcontentloaded", timeout=60000)
    mobile_page.wait_for_selector("article.markdown-body", timeout=60000)
    mobile_page.wait_for_timeout(2500)
    mobile = {
        "layout": mobile_page.evaluate(
            """() => ({
                innerWidth: window.innerWidth,
                visualWidth: window.visualViewport ? window.visualViewport.width : null,
                clientWidth: document.documentElement.clientWidth,
                scrollWidth: document.documentElement.scrollWidth,
                articleWidth: document.querySelector('article.markdown-body').getBoundingClientRect().width
            })"""
        ),
        "h1_visible": mobile_page.evaluate(
            """() => {
                const heading = document.querySelector('article.markdown-body h1');
                if (!heading) return false;
                const rect = heading.getBoundingClientRect();
                return rect.top >= 0 && rect.bottom <= window.innerHeight;
            }"""
        ),
        "images": mobile_page.eval_on_selector_all(
            "article.markdown-body img",
            """images => images.map((image) => ({
                src: image.getAttribute('src'),
                complete: image.complete,
                naturalWidth: image.naturalWidth
            }))""",
        ),
    }
    mobile["broken_images"] = [
        image["src"]
        for image in mobile["images"]
        if not image["complete"] or image["naturalWidth"] == 0
    ]
    mobile_page.evaluate("() => window.scrollTo(0, 0)")
    mobile_page.wait_for_timeout(700)
    mobile_page.screenshot(path=SCREENSHOT_DIR / "live-profile-header-mobile.png")
    mobile["screenshot"] = "docs/evidence/screenshots/live/live-profile-header-mobile.png"
    out["mobile"] = mobile

    out["axe"] = {
        "run": False,
        "reason": "GitHub CSP blocks external axe-core injection on github.com; "
        "accessibility was verified on the GitHub-API preview (0 violations).",
    }
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="https://github.com/dbsectrainer")
    parser.add_argument("--json", type=Path, default=RESULTS_DIR / "live-profile-verification.json")
    args = parser.parse_args()

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            desktop_context = browser.new_context(
                viewport={"width": 1440, "height": 900},
                device_scale_factor=1,
                color_scheme="light",
            )
            desktop = desktop_context.new_page()
            desktop_errors = {"console": [], "failed": [], "bad": []}
            desktop.on(
                "console",
                lambda message: desktop_errors["console"].append(
                    {"type": message.type, "text": message.text[:500]}
                )
                if message.type == "error"
                else None,
            )
            desktop.on(
                "requestfailed",
                lambda request: desktop_errors["failed"].append(
                    {"url": request.url[:500], "failure": request.failure}
                ),
            )
            desktop.on(
                "response",
                lambda response: desktop_errors["bad"].append(
                    {"url": response.url[:500], "status": response.status}
                )
                if response.status >= 400
                else None,
            )

            mobile_context = browser.new_context(
                viewport={"width": 390, "height": 844},
                device_scale_factor=1,
                is_mobile=True,
                has_touch=True,
                color_scheme="light",
            )
            mobile = mobile_context.new_page()
            mobile_errors = {"console": [], "failed": [], "bad": []}
            mobile.on(
                "console",
                lambda message: mobile_errors["console"].append(
                    {"type": message.type, "text": message.text[:500]}
                )
                if message.type == "error"
                else None,
            )
            mobile.on(
                "requestfailed",
                lambda request: mobile_errors["failed"].append(
                    {"url": request.url[:500], "failure": request.failure}
                ),
            )
            mobile.on(
                "response",
                lambda response: mobile_errors["bad"].append(
                    {"url": response.url[:500], "status": response.status}
                )
                if response.status >= 400
                else None,
            )

            result = capture(desktop, mobile, args.url)
            result["desktop_errors"] = desktop_errors
            result["mobile_errors"] = mobile_errors
            result["pass"] = (
                result["content"]["has_selected_work"]
                and result["content"]["has_aegis"]
                and result["h1_visible"]
                and not result["broken_images"]
                and len(result["toc"]) == 8
                and all(click["visible"] for click in result["toc_clicks"])
                and not desktop_errors["console"]
                and not desktop_errors["failed"]
                and not desktop_errors["bad"]
                and result["mobile"]["h1_visible"]
                and not result["mobile"]["broken_images"]
                and not mobile_errors["console"]
                and not mobile_errors["failed"]
                and not mobile_errors["bad"]
                and result["mobile"]["layout"]["scrollWidth"]
                <= result["mobile"]["layout"]["visualWidth"] + 1
            )
            result["screenshots"] = [
                "docs/evidence/screenshots/live/live-profile-header-desktop.png",
                "docs/evidence/screenshots/live/live-profile-header-mobile.png",
                "docs/evidence/screenshots/live/live-profile-toc-desktop.png",
            ]
            desktop_context.close()
            mobile_context.close()
        finally:
            browser.close()

    args.json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Live profile: {result['url']}")
    print(f"Title: {result['title']}")
    print(f"H1 visible: {result['h1_visible']}")
    print(f"Images: {len(result['images'])}; broken: {len(result['broken_images'])}")
    print(f"TOC: {len(result['toc'])} links; visible after click: "
          f"{sum(1 for click in result['toc_clicks'] if click['visible'])}")
    print(
        "Console/network: "
        f"desktop {len(result['desktop_errors']['console'])}/"
        f"{len(result['desktop_errors']['failed'])}/"
        f"{len(result['desktop_errors']['bad'])}; "
        f"mobile {len(result['mobile_errors']['console'])}/"
        f"{len(result['mobile_errors']['failed'])}/"
        f"{len(result['mobile_errors']['bad'])}"
    )
    print(f"Mobile layout: {result['mobile']['layout']}")
    print(f"JSON result: {args.json.relative_to(ROOT)}")
    if result["pass"]:
        print("PASS: published profile content, images, TOC, console, network, and mobile layout")
        return 0
    print("FAIL: one or more live profile checks failed", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
