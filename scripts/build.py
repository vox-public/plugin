"""Build external Plugin and hosted skill-only ZIPs from the same source files."""
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    catalog = json.loads((ROOT / 'catalog.json').read_text())
    assert len(catalog['skills']) == 26
    shared = sorted([*ROOT.glob('skills/*/SKILL.md'), *ROOT.glob('references/*')])
    for path in shared:
        assert path.is_file() and not path.is_symlink()
        text = path.read_text()
        assert '/Users/' not in text and '[[share/' not in text, path
        if path.suffix == '.md':
            for href in re.findall(r'\]\(([^)]+)\)', text):
                if '://' not in href and not href.startswith('#'):
                    target = (path.parent / href.split('#')[0]).resolve()
                    assert target.is_relative_to(ROOT) and target.is_file(), (path, href)
    digests = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in shared}
    digest = hashlib.sha256(json.dumps(digests, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    manifest = {'version': '0.1.0', 'skills_count': 26, 'sha256': digest,
                'capability_directories': ['/workspace/vox-ai/skills'], 'files': digests}
    (ROOT / 'bundle-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    destination = ROOT / 'dist'
    destination.mkdir(exist_ok=True)
    common = shared + [ROOT / 'bundle-manifest.json', ROOT / 'catalog.json']
    external = common + [ROOT / '.codex-plugin/plugin.json', ROOT / '.claude-plugin/plugin.json',
                         ROOT / '.mcp.json', ROOT / 'README.md']
    for name, paths in [('vox-ai-plugin.zip', external), ('vox-ai-skills.zip', common)]:
        with zipfile.ZipFile(destination / name, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(paths):
                info = zipfile.ZipInfo(str(path.relative_to(ROOT)), date_time=(2026, 9, 16, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                archive.writestr(info, path.read_bytes())
    with zipfile.ZipFile(destination / 'vox-ai-skills.zip') as hosted:
        assert not any('plugin.json' in n or 'mcp.json' in n for n in hosted.namelist())
        with zipfile.ZipFile(destination / 'vox-ai-plugin.zip') as external:
            assert all(hosted.read(name) == external.read(name) for name in digests)
    print(json.dumps({'skills': 26, 'shared_sha256': digest, 'links': 'valid', 'artifacts': 2}))


if __name__ == '__main__':
    main()
