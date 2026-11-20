#!/usr/bin/env python3
"""Print local HTML with Chrome/Chromium/Edge; Python standard library only."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('html', type=Path)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--browser', help='Chrome/Chromium/Edge executable path')
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    source, target = args.html.resolve(), args.pdf.resolve()
    if not source.is_file() or source.suffix.lower() not in {'.html', '.htm'}:
        parser.error('Input must be an existing HTML file')
    if target.suffix.lower() != '.pdf' or source == target:
        parser.error('Output must be a separate .pdf file')
    if target.exists() and not args.overwrite:
        parser.error('Output exists; choose another path or pass --overwrite')
    candidates = [args.browser] if args.browser else [
        shutil.which('google-chrome'), shutil.which('chromium'),
        shutil.which('chromium-browser'), shutil.which('msedge'),
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
        str(Path(os.environ.get('PROGRAMFILES', 'C:/Program Files')) / 'Google/Chrome/Application/chrome.exe'),
        str(Path(os.environ.get('LOCALAPPDATA', 'C:/Users/Default/AppData/Local')) / 'Google/Chrome/Application/chrome.exe'),
    ]
    browser = next((str(p) for p in candidates if p and Path(p).is_file()), None)
    if not browser:
        parser.error('Browser not found. Pass --browser or use Print > Save as PDF in your browser.')
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.pdf-export-', dir=target.parent) as profile:
        staged = Path(profile) / 'result.pdf'
        command = [browser, '--headless=new', '--disable-gpu', '--no-first-run',
                   '--disable-extensions', '--disable-background-networking',
                   '--allow-file-access-from-files', '--no-pdf-header-footer',
                   '--run-all-compositor-stages-before-draw', '--virtual-time-budget=3000',
                   '--user-data-dir=' + str(Path(profile) / 'browser'),
                   '--print-to-pdf=' + str(staged), source.as_uri()]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        except subprocess.TimeoutExpired:
            parser.exit(1, 'Browser timed out. Check local assets or use browser Print.\n')
        if result.returncode or not staged.is_file() or staged.stat().st_size == 0:
            parser.exit(1, f'PDF export failed (browser exit code {result.returncode}):\n' + result.stderr[-3000:] + '\n')
        if target.exists() and not args.overwrite:
            parser.error('Output was created during export; choose another path')
        shutil.copyfile(staged, target)
    print('Created:', target)
    print('Reopen and inspect page size, text, images, and links before submission.')


if __name__ == '__main__':
    main()
