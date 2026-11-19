#!/usr/bin/env python3
"""Checks the static site in app/: every local src/href exists, every #anchor has a target."""
import re
import sys
from pathlib import Path

APP = Path(__file__).resolve().parent.parent / "app"
html = (APP / "index.html").read_text(encoding="utf-8")
errors = []

for url in re.findall(r'(?:src|href)="([^"]+)"', html):
    if re.match(r"(https?:|data:|mailto:)", url):
        continue
    if url.startswith("#"):
        if url != "#" and f'id="{url[1:]}"' not in html:
            errors.append(f"anchor without target: {url}")
    elif not (APP / url.split("#")[0]).is_file():
        errors.append(f"missing file: {url}")

if errors:
    sys.exit("\n".join(errors))
print("site OK")
