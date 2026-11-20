#!/usr/bin/env python3
"""Check PDF page count, geometry, text, and URI annotations (requires pypdf)."""
import argparse
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--kind', choices=['poster', 'portfolio'], required=True)
    parser.add_argument('--require-uri', action='append', default=[])
    args = parser.parse_args()
    try:
        from pypdf import PdfReader
    except ImportError:
        parser.exit(2, 'pypdf is unavailable. Use a Python environment with pypdf, or inspect manually.\n')
    reader = PdfReader(args.pdf)
    errors, urls = [], set()
    count = len(reader.pages)
    if args.kind == 'poster' and count != 1:
        errors.append('Poster must contain one page')
    if args.kind == 'portfolio' and not 1 <= count <= 10:
        errors.append('Portfolio must contain 1 to 10 pages')
    for i, page in enumerate(reader.pages, 1):
        w, h = float(page.mediabox.width), float(page.mediabox.height)
        if args.kind == 'poster':
            if not all(abs(a - b) < 2 for a, b in zip(sorted([w, h]), [595.276, 841.89])):
                errors.append(f'Page {i}: expected A4, got {w:.2f} x {h:.2f} pt')
        elif abs(w / h - 16 / 9) > 0.01:
            errors.append(f'Page {i}: expected 16:9')
        if not (page.extract_text() or '').strip():
            errors.append(f'Page {i}: no extractable text')
        for ref in page.get('/Annots', []):
            action = ref.get_object().get('/A', {})
            if hasattr(action, 'get_object'):
                action = action.get_object()
            if action.get('/URI'):
                urls.add(str(action['/URI']))
    for uri in args.require_uri:
        if uri not in urls:
            errors.append('Missing link annotation: ' + uri)
    for error in errors:
        print('FAIL:', error)
    print(f'Pages: {count}; distinct URI links: {len(urls)}')
    print('Visual inspection of every page is still required.')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
