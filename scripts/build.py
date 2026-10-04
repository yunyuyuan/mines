#!/usr/bin/env python3
"""Bundle the upstream Mines engine for offline use and GitHub Pages."""
from base64 import b64encode
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def build() -> None:
    original_js = (ROOT / 'vendor/mines.js').read_text()
    wasm = (ROOT / 'vendor/mines.wasm').read_bytes()
    css = (ROOT / 'src/game.css').read_text()
    markup = (ROOT / 'src/game.html').read_text()
    touch = (ROOT / 'src/touch.js').read_text()
    license_text = (ROOT / 'vendor/LICENSE').read_text()
    marker = 'var moduleOverrides = Object.assign({}, Module);'
    if original_js.count(marker) != 1:
        raise RuntimeError('Upstream loader has changed: review the bundle adapter.')
    # Upstream pre-JS recreates Module. Insert after that setup and before
    # Emscripten reads its configuration. No game code is modified.
    adapter = (
        "Module['wasmBinary'] = Uint8Array.from(\n"
        "  atob(document.getElementById('wasm-data').textContent.trim()),\n"
        "  function (character) { return character.charCodeAt(0); }\n"
        ");\n"
    )
    engine = original_js.replace(marker, adapter + marker)
    engine = engine.replace('</script', '<\\/script')
    document = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mines</title>
<!--
{license_text.replace('--', '—')}
-->
<style>
{css}</style>
</head>
<body>
{markup}
<noscript>This game requires JavaScript and WebAssembly.</noscript>
<script type="application/octet-stream" id="wasm-data">{b64encode(wasm).decode()}</script>
<script>
{engine}
</script>
<script>
{touch}
</script>
</body>
</html>
'''
    public = ROOT / 'public'
    public.mkdir(exist_ok=True)
    (public / 'index.html').write_text(document)
    # GitHub Pages: deploy main / (root), with no Node or build service needed.
    (ROOT / 'index.html').write_text(document)
    (ROOT / '.nojekyll').touch()
    manifest = {
        'upstream_version': '20260923.616da16',
        'upstream_url': 'https://www.chiark.greenend.org.uk/~sgtatham/puzzles/js/mines.html',
        'mines_js_sha256': hashlib.sha256(original_js.encode()).hexdigest(),
        'mines_wasm_sha256': hashlib.sha256(wasm).hexdigest(),
        'offline_html_sha256': hashlib.sha256(document.encode()).hexdigest(),
        'external_runtime_dependencies': []
    }
    (ROOT / 'SOURCE.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Built {ROOT / "index.html"} ({len(document.encode()):,} bytes)')


if __name__ == '__main__':
    build()
