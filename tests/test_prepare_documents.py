"""Portable template packaging keeps font resources and license with the HTML."""
import hashlib
import importlib.util
from pathlib import Path
import re
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('prepare_documents', ROOT / 'tools/prepare_documents.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PrepareTests(unittest.TestCase):
    def test_all_templates_resolve_their_local_fonts(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            MODULE.prepare(root)
            self.assertEqual(len(list(root.glob('*.html'))), 3)
            for template in root.glob('*.html'):
                font_urls = re.findall(r'url\("([^"]+\.woff2)"\)', template.read_text())
                self.assertTrue(font_urls)
                for url in font_urls:
                    font = root / url
                    self.assertTrue(font.is_file())
                    self.assertEqual(font.read_bytes()[:4], b'wOF2')

    def test_resume_scope_only_creates_two_resume_templates(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            MODULE.prepare(root, 'resume')
            self.assertEqual({p.name for p in root.glob('*.html')}, {'resume-ko.html', 'resume-en.html'})

    def test_portfolio_scope_only_creates_portfolio(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            MODULE.prepare(root, 'portfolio')
            self.assertEqual({p.name for p in root.glob('*.html')}, {'portfolio.html'})

    def test_resume_then_portfolio_can_share_unchanged_fonts(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            MODULE.prepare(root, 'resume')
            original = (root / 'assets/fonts/PretendardVariable.woff2').read_bytes()
            created = MODULE.prepare(root, 'portfolio')
            self.assertEqual(created, ['portfolio.html'])
            self.assertEqual((root / 'assets/fonts/PretendardVariable.woff2').read_bytes(), original)

    def test_license_and_font_bytes_are_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            MODULE.prepare(root, 'resume')
            for filename in ['PretendardVariable.woff2', 'LICENSE.txt']:
                self.assertEqual((root / 'assets/fonts' / filename).read_bytes(),
                                 (ROOT / 'assets/fonts' / filename).read_bytes())
            digest = hashlib.sha256((root / 'assets/fonts/PretendardVariable.woff2').read_bytes()).hexdigest()
            self.assertEqual(digest, '9599f12fd42fc0bce1cd50b47a0c022e108d7aa64dd0d1bb0ed44f3282d900b4')

    def test_existing_work_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            MODULE.prepare(root, 'resume')
            original = root / 'resume-ko.html'
            original.write_text('Edited candidate work')
            with self.assertRaises(ValueError):
                MODULE.prepare(root, 'resume')
            self.assertEqual(original.read_text(), 'Edited candidate work')

    def test_preflight_conflict_does_not_create_partial_templates(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'assets/fonts').mkdir(parents=True)
            (root / 'assets/fonts/LICENSE.txt').write_text('Existing license')
            with self.assertRaises(ValueError):
                MODULE.prepare(root)
            self.assertEqual(list(root.glob('*.html')), [])

    def test_invalid_kind_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                MODULE.prepare(folder, 'unexpected')


if __name__ == '__main__':
    unittest.main()
