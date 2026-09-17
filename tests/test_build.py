import contextlib
import io
import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.build import ROOT, build


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'plugin'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', 'dist', '__pycache__'))

    def change_json(self, name, change):
        path = self.root / name
        value = json.loads(path.read_text())
        change(value)
        path.write_text(json.dumps(value))

    def run_build(self):
        with contextlib.redirect_stdout(io.StringIO()):
            build(self.root)

    def test_reproducible_archives_and_hosted_isolation(self):
        self.run_build()
        before = {p.name: p.read_bytes() for p in (self.root / 'dist').glob('*.zip')}
        self.run_build()
        self.assertEqual(before, {p.name: p.read_bytes() for p in (self.root / 'dist').glob('*.zip')})
        with zipfile.ZipFile(self.root / 'dist/vox-ai-skills.zip') as hosted:
            self.assertFalse(any(name.startswith('.') for name in hosted.namelist()))
            with zipfile.ZipFile(self.root / 'dist/vox-ai-plugin.zip') as external:
                for name in hosted.namelist():
                    self.assertEqual(hosted.read(name), external.read(name))

    def test_bad_catalog_path_rejected_before_artifacts(self):
        self.change_json('catalog.json', lambda c: c['skills'][0].update(path='skills/missing/SKILL.md'))
        with self.assertRaisesRegex(ValueError, 'Catalog paths'):
            self.run_build()
        self.assertFalse((self.root / 'dist').exists())

    def test_duplicate_skill_rejected(self):
        self.change_json('catalog.json', lambda c: c['skills'].append(c['skills'][0]))
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            self.run_build()

    def test_missing_skill_rejected(self):
        (self.root / 'skills/voice-agent-design/SKILL.md').unlink()
        with self.assertRaisesRegex(ValueError, 'Catalog paths'):
            self.run_build()

    def test_frontmatter_mismatch_rejected(self):
        path = self.root / 'skills/voice-agent-design/SKILL.md'
        path.write_text(path.read_text().replace('name: voice-agent-design', 'name: wrong-name'))
        with self.assertRaisesRegex(ValueError, 'Frontmatter name'):
            self.run_build()

    def test_host_versions_must_match(self):
        self.change_json('.claude-plugin/plugin.json', lambda p: p.update(version='9.0.0'))
        with self.assertRaisesRegex(ValueError, 'disagree on version'):
            self.run_build()

    def test_bad_marketplace_source_rejected(self):
        self.change_json('.claude-plugin/marketplace.json',
                         lambda p: p['plugins'][0].update(source='./missing'))
        with self.assertRaisesRegex(ValueError, 'marketplace source'):
            self.run_build()

    def test_public_bundle_cannot_point_at_dev(self):
        self.change_json('.mcp.json', lambda p: p['mcpServers']['vox-ai'].update(
            url='https://mcp.dev.services.tryvox.co/mcp'))
        with self.assertRaisesRegex(ValueError, 'Public bundle'):
            self.run_build()


if __name__ == '__main__':
    unittest.main()
