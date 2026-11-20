#!/usr/bin/env python3
"""Copy editable templates and bundled fonts into a portable output folder."""
import argparse
from pathlib import Path
import shutil


def prepare(destination, kind='all'):
    root = Path(__file__).resolve().parents[1]
    destination = Path(destination).resolve()
    templates = {}
    if kind in {'resume', 'all'}:
        for language in ['ko', 'en']:
            templates[f'resume-{language}.html'] = (
                root / f'skills/html-a4-resume/assets/resume-{language}.html')
    if kind in {'portfolio', 'all'}:
        templates['portfolio.html'] = root / 'skills/html-pdf-portfolio/assets/portfolio.html'
    fonts = {f'assets/fonts/{name}': root / f'assets/fonts/{name}'
             for name in ['PretendardVariable.woff2', 'LICENSE.txt', 'README.md']}
    targets = {**templates, **fonts}
    reusable = set()
    if not templates:
        raise ValueError('kind must be resume, portfolio, or all')
    for relative, source in targets.items():
        if not source.is_file():
            raise ValueError('A bundled template or font resource is missing')
        if (destination / relative).exists():
            target = destination / relative
            if relative in fonts and target.is_file() and target.read_bytes() == source.read_bytes():
                reusable.add(relative)
                continue
            raise ValueError('Output already exists; choose a new version folder')
    for relative, source in targets.items():
        if relative in reusable:
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if relative in templates:
            target.write_text(source.read_text(encoding='utf-8').replace(
                '../../../assets/fonts/', 'assets/fonts/'), encoding='utf-8')
        else:
            shutil.copy2(source, target)
    return [name for name in targets if name not in reusable]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--kind', choices=['resume', 'portfolio', 'all'], default='all')
    args = parser.parse_args()
    try:
        files = prepare(args.destination, args.kind)
    except (OSError, ValueError) as error:
        parser.exit(1, str(error) + '\n')
    print(f'Prepared {len(files)} files in {args.destination.resolve()}')
    print('Edit the HTML with actual evidence, then export and inspect each PDF.')


if __name__ == '__main__':
    main()
