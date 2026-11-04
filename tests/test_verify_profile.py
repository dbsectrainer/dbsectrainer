"""Regression tests for the profile README validator."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import verify_profile as vp  # noqa: E402

SAMPLE = """# Profile

## Table of Contents

- [About Me](#user-content-about-me)

<a id="about-me"></a>
## About Me

![Python](https://img.shields.io/badge/Python-3776AB)

<p align="center"><img src="line.png" alt="" width="100%"></p>
"""


class ParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parsed = vp.parse_readme(SAMPLE)

    def test_toc_is_parsed(self) -> None:
        self.assertEqual(len(self.parsed["toc"]), 1)
        self.assertEqual(self.parsed["toc"][0]["fragment"], "user-content-about-me")

    def test_explicit_anchor_is_prefixed(self) -> None:
        self.assertEqual(
            self.parsed["anchors"][0]["rendered_id"], "user-content-about-me"
        )

    def test_images_are_parsed(self) -> None:
        self.assertEqual(len(self.parsed["images"]), 2)
        self.assertEqual(self.parsed["images"][0]["alt"], "Python")
        self.assertEqual(self.parsed["images"][1]["alt"], "")

    def test_toc_anchors_resolve(self) -> None:
        self.assertTrue(vp.check_anchor_targets(self.parsed).ok)

    def test_missing_anchor_is_reported(self) -> None:
        parsed = vp.parse_readme(SAMPLE.replace("#user-content-about-me", "#nope"))
        check = vp.check_anchor_targets(parsed)
        self.assertFalse(check.ok)
        self.assertIn("unresolved TOC links", check.detail)

    def test_heading_structure_passes(self) -> None:
        check = vp.check_heading_structure(self.parsed, SAMPLE)
        self.assertTrue(check.ok, check.detail)

    def test_skipped_heading_level_is_reported(self) -> None:
        text = "# Title\n\n### Too Deep\n"
        parsed = vp.parse_readme(text)
        check = vp.check_heading_structure(parsed, text)
        self.assertFalse(check.ok)
        self.assertIn("skips a level", check.detail)

    def test_markdown_image_requires_alt(self) -> None:
        parsed = vp.parse_readme("![](https://example.test/image.png)\n")
        self.assertFalse(vp.check_images(parsed).ok)

    def test_html_image_requires_alt_attribute(self) -> None:
        parsed = vp.parse_readme('<img src="image.png">\n')
        self.assertFalse(vp.check_images(parsed).ok)

    def test_decorative_html_alt_is_allowed(self) -> None:
        parsed = vp.parse_readme('<img src="line.png" alt="">\n')
        self.assertTrue(vp.check_images(parsed).ok)

    def test_placeholder_detection(self) -> None:
        self.assertFalse(vp.check_placeholder_content("https://yourwebsite.com").ok)
        self.assertTrue(vp.check_placeholder_content(SAMPLE).ok)

    def test_trailing_whitespace_detection(self) -> None:
        self.assertFalse(vp.check_trailing_whitespace("line \nnext\n").ok)
        self.assertTrue(vp.check_trailing_whitespace("line\nnext\n").ok)

    def test_external_urls_are_deduplicated(self) -> None:
        text = (
            "[a](https://example.test/a) [b](https://example.test/a) "
            "![img](https://example.test/i.png)\n"
        )
        urls = vp.external_urls(vp.parse_readme(text))
        self.assertEqual(urls, ["https://example.test/a", "https://example.test/i.png"])


class RealReadmeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = vp.README.read_text(encoding="utf-8")
        self.parsed = vp.parse_readme(self.text)

    def test_no_placeholders(self) -> None:
        self.assertTrue(vp.check_placeholder_content(self.text).ok)

    def test_anchors_resolve(self) -> None:
        check = vp.check_anchor_targets(self.parsed)
        self.assertTrue(check.ok, check.detail)

    def test_heading_structure(self) -> None:
        check = vp.check_heading_structure(self.parsed, self.text)
        self.assertTrue(check.ok, check.detail)

    def test_images_have_alt_text(self) -> None:
        check = vp.check_images(self.parsed)
        self.assertTrue(check.ok, check.detail)

    def test_archived_svgs_are_safe(self) -> None:
        check = vp.check_svgs()
        self.assertTrue(check.ok, check.detail)


if __name__ == "__main__":
    unittest.main()
