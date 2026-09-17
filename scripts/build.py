"""Validate and build external Plugin and hosted skill-only ZIPs."""
import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_json(path):
    return json.loads(path.read_text())


def validate(root):
    catalog = load_json(root / 'catalog.json')
    entries = catalog['skills']
    names = [entry['name'] for entry in entries]
    require(bool(names) and len(names) == len(set(names)), 'Duplicate or empty catalog skills')
    paths = [entry['path'] for entry in entries]
    actual = sorted(root.glob('skills/*/SKILL.md'))
    require(len(paths) == len(set(paths)), 'Duplicate catalog paths')
    require(set(paths) == {p.relative_to(root).as_posix() for p in actual},
            'Catalog paths must exactly match skill files')
    require(dict(Counter(entry['layer'] for entry in entries)) == catalog['layers'],
            'Catalog layer counts do not match skills')
    for entry in entries:
        path = root / entry['path']
        require(entry['path'] == f"skills/{entry['name']}/SKILL.md", 'Skill name/path mismatch')
        parts = path.read_text().split('---', 2)
        require(len(parts) == 3 and not parts[0].strip(), f'Missing frontmatter: {path}')
        frontmatter = yaml.safe_load(parts[1])
        require(isinstance(frontmatter, dict), f'Invalid frontmatter: {path}')
        require(frontmatter.get('name') == entry['name'], f'Frontmatter name mismatch: {path}')
        require(frontmatter.get('description') == entry['description'],
                f'Frontmatter description mismatch: {path}')
        require(frontmatter.get('metadata', {}).get('layer') == entry['layer'],
                f'Frontmatter layer mismatch: {path}')

    codex = load_json(root / '.codex-plugin/plugin.json')
    claude = load_json(root / '.claude-plugin/plugin.json')
    for key in ('name', 'version', 'description', 'author', 'skills', 'mcpServers'):
        require(codex.get(key) == claude.get(key) and key in codex,
                f'Host manifests disagree on {key}')
    require(codex['name'] == 'vox-ai', 'Unexpected plugin name')
    require(re.fullmatch(r'\d+\.\d+\.\d+', codex['version']), 'Invalid release version')
    require(codex['skills'] == './skills/' and codex['mcpServers'] == './.mcp.json',
            'Unexpected component paths')
    connection = load_json(root / '.mcp.json')['mcpServers']['vox-ai']
    require(connection == {'type': 'http', 'url': 'https://mcp.tryvox.co/mcp'},
            'Public bundle must use the reviewed public MCP connection without credentials')
    for host, location in [('codex', '.agents/plugins/marketplace.json'),
                           ('claude', '.claude-plugin/marketplace.json')]:
        market = load_json(root / location)
        require(market['name'] == 'vox-ai' and len(market['plugins']) == 1,
                f'Unexpected {host} marketplace')
        plugin = market['plugins'][0]
        expected_source = {'source': 'local', 'path': './'} if host == 'codex' else './'
        require(plugin['name'] == codex['name'] and plugin['source'] == expected_source,
                f'Invalid {host} marketplace source')

    shared = sorted([*actual, *root.glob('references/*')])
    for path in shared:
        require(path.is_file() and not path.is_symlink(), f'Not a regular file: {path}')
        content = path.read_text()
        require('/Users/' not in content and '[[share/' not in content,
                f'Private path in {path}')
        if path.suffix == '.md':
            for href in re.findall(r'\]\(([^)]+)\)', content):
                if '://' not in href and not href.startswith('#'):
                    target = (path.parent / href.split('#')[0]).resolve()
                    require(target.is_relative_to(root.resolve()) and target.is_file(),
                            f'Invalid reference in {path}: {href}')
    return codex['version'], len(entries), shared


def build(root=ROOT):
    version, count, shared = validate(root)
    digests = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in shared}
    digest = hashlib.sha256(json.dumps(digests, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    manifest = {'version': version, 'skills_count': count, 'sha256': digest,
                'capability_directories': ['/workspace/vox-ai/skills'], 'files': digests}
    (root / 'bundle-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    destination = root / 'dist'
    destination.mkdir(exist_ok=True)
    common = shared + [root / 'bundle-manifest.json', root / 'catalog.json']
    external = common + [root / '.codex-plugin/plugin.json', root / '.claude-plugin/plugin.json',
                         root / '.mcp.json', root / 'README.md']
    for name, paths in [('vox-ai-plugin.zip', external), ('vox-ai-skills.zip', common)]:
        with zipfile.ZipFile(destination / name, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(paths):
                info = zipfile.ZipInfo(str(path.relative_to(root)), date_time=(2026, 9, 16, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                archive.writestr(info, path.read_bytes())
    with zipfile.ZipFile(destination / 'vox-ai-skills.zip') as hosted:
        require(not any('plugin.json' in n or 'mcp.json' in n for n in hosted.namelist()),
                'Host connection leaked into skill-only archive')
        with zipfile.ZipFile(destination / 'vox-ai-plugin.zip') as external_zip:
            require(all(hosted.read(name) == external_zip.read(name) for name in hosted.namelist()),
                    'Shared archives differ')
    print(json.dumps({'skills': count, 'shared_sha256': digest, 'links': 'valid', 'artifacts': 2}))


if __name__ == '__main__':
    build()
