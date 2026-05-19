#!/usr/bin/env python3
"""
Local development server for NPR 4660 docs.

Features:
  - Serves docs/ as static files
  - Generates manifest.json on startup and whenever data files change
  - Injects a live-reload snippet into index.html so the browser
    refreshes automatically when content is modified

Usage:
  python serve.py          # port 8000 (default)
  python serve.py 9000     # custom port
"""

import http.server
import json
import os
import re
import sys
import threading
import time
from pathlib import Path

ROOT     = Path(__file__).resolve().parent
DOCS     = ROOT / 'docs'
DATA     = DOCS / 'data'
MANIFEST = DATA / 'manifest.json'

state      = {'version': '0'}
state_lock = threading.Lock()


# -- Manifest ------------------------------------------------------------------

def folder_label(name: str) -> str:
    return name.replace('_', ' ').title()


def generate_manifest() -> None:
    examples = []

    for ex_dir in sorted(DATA.iterdir()):
        if not ex_dir.is_dir() or ex_dir.name.startswith('.'):
            continue
        figuren = []
        for fig_dir in sorted(ex_dir.iterdir()):
            if not fig_dir.is_dir():
                continue
            m = re.match(r'^figuur(\d+)$', fig_dir.name)
            if not m or not (fig_dir / 'README.md').exists():
                continue
            files = [f.name for f in fig_dir.iterdir() if f.is_file()]
            figuren.append({
                'id':      fig_dir.name,
                'nr':      int(m.group(1)),
                'pngFile': next((f for f in files if f.lower().endswith('.png')), None),
                'ttlFile': next((f for f in files if f.lower().endswith('.ttl')), None),
            })
        figuren.sort(key=lambda f: f['nr'])
        if figuren:
            examples.append({'id': ex_dir.name, 'label': folder_label(ex_dir.name), 'figuren': figuren})

    MANIFEST.write_text(json.dumps({'examples': examples}, indent=2, ensure_ascii=False), encoding='utf-8')
    total = sum(len(e['figuren']) for e in examples)
    print(f'  manifest.json: {len(examples)} voorbeeld(en), {total} figuren')


# -- File watcher --------------------------------------------------------------

def snapshot() -> dict:
    result = {}
    for root, _, files in os.walk(DATA):
        for f in files:
            if f == 'manifest.json':
                continue
            p = Path(root) / f
            try:
                result[str(p)] = p.stat().st_mtime
            except OSError:
                pass
    return result


def watch_loop() -> None:
    prev = snapshot()
    while True:
        time.sleep(1)
        curr = snapshot()
        if curr != prev:
            prev = curr
            print('\nWijziging gedetecteerd - manifest bijwerken...')
            generate_manifest()
            with state_lock:
                state['version'] = str(time.time())


# -- HTTP handler --------------------------------------------------------------

# Tiny polling script injected into index.html - triggers reload on version change.
RELOAD_JS = (
    b'<script>'
    b'(function(){'
    b'var v=null;'
    b'setInterval(function(){'
    b"fetch('/_v',{cache:'no-store'}).then(function(r){return r.text();}).then(function(nv){"
    b'if(v===null){v=nv;}else if(v!==nv){location.reload();}'
    b'}).catch(function(){});'
    b'},800);'
    b'})();'
    b'</script>'
)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DOCS), **kwargs)

    def do_GET(self):
        # Version endpoint polled by the injected reload script
        if self.path == '/_v':
            with state_lock:
                body = state['version'].encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # Intercept index.html to inject the reload snippet
        clean = self.path.split('?')[0].rstrip('/')
        if clean in ('', '/index.html'):
            try:
                content = (DOCS / 'index.html').read_bytes()
                content = content.replace(b'</body>', RELOAD_JS + b'</body>', 1)
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Cache-Control', 'no-store')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            except OSError:
                pass

        super().do_GET()

    def log_message(self, fmt, *args):
        code = args[1] if len(args) > 1 else ''
        if str(code) not in ('200', '304'):
            print(f'  {self.address_string()} - {fmt % args}')


# -- Entry point ---------------------------------------------------------------

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

    print('NPR 4660 - lokale server')
    print('-' * 40)
    print('Manifest genereren...')
    generate_manifest()
    print(f'\nOpen: http://localhost:{port}')
    print('Live reload actief (bestanden worden bewaakt)')
    print('Ctrl+C om te stoppen\n')

    threading.Thread(target=watch_loop, daemon=True).start()

    server = http.server.ThreadingHTTPServer(('', port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nServer gestopt.')
