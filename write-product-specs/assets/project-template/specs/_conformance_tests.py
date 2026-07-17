#!/usr/bin/env python3
"""Regression tests for the generic specification source and renderer contracts."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from _spec_core import href_for, inline, load_pages, render_block


class SpecificationCoreTests(unittest.TestCase):
    def test_inline_escapes_text_and_renders_local_links(self) -> None:
        rendered = inline('Use <unsafe> and [[Details|architecture/system-map.html#scope]]', 'features/example.html')
        self.assertIn('&lt;unsafe&gt;', rendered)
        self.assertIn('../architecture/system-map.html#scope', rendered)

    def test_nested_routes_compute_asset_and_page_links(self) -> None:
        self.assertEqual(href_for('architecture/backend/accounts.html', 'index.html'), '../../index.html')
        self.assertEqual(href_for('architecture/backend/accounts.html', '#flow'), '#flow')

    def test_unknown_block_type_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, 'Unsupported specification block type'):
            render_block({'type': 'raw-html'}, 'index.html')

    def test_code_blocks_escape_content(self) -> None:
        rendered = render_block({'type': 'code', 'language': 'html', 'code': '<script>alert(1)</script>'}, 'index.html')
        self.assertNotIn('<script>', rendered)
        self.assertIn('&lt;script&gt;', rendered)

    def test_loader_rejects_sources_without_page(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, 'broken.py').write_text('VALUE = 1\n')
            with self.assertRaisesRegex(ValueError, 'has no PAGE'):
                load_pages(Path(directory))

    def test_loader_reads_independent_page_modules(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, 'one.py').write_text("PAGE = {'route': 'one.html'}\n")
            pages = load_pages(Path(directory))
            self.assertEqual(pages[0]['route'], 'one.html')
            self.assertTrue(pages[0]['_source'].endswith('one.py'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
