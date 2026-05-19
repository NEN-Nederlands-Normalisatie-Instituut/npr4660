#!/usr/bin/env python3
"""Generate docs/data/manifest.json by scanning the docs/data/ directory tree."""

import json
import re
from pathlib import Path

DATA     = Path(__file__).resolve().parent / 'docs' / 'data'
MANIFEST = DATA / 'manifest.json'


def folder_label(name: str) -> str:
    return name.replace('_', ' ').title()


def scan() -> list:
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
            examples.append({
                'id':      ex_dir.name,
                'label':   folder_label(ex_dir.name),
                'figuren': figuren,
            })

    return examples


if __name__ == '__main__':
    examples = scan()
    MANIFEST.write_text(
        json.dumps({'examples': examples}, indent=2, ensure_ascii=False),
        encoding='utf-8',
    )
    total = sum(len(e['figuren']) for e in examples)
    print(f'manifest.json geschreven - {len(examples)} voorbeeld(en), {total} figuren')
