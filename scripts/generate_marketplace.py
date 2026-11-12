#!/usr/bin/env python3
"""Regenerate .claude-plugin/marketplace.json from plugins/*/.claude-plugin/plugin.json.

Usage: python scripts/generate_marketplace.py [--check]
The header (name, owner, metadata) stays the source of truth in marketplace.json;
only the `plugins` list is generated. --check fails if the file is out of sync.
"""
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, ".claude-plugin", "marketplace.json")
PLUGINS_DIR = os.path.join(ROOT, "plugins")


def read_text(path):
    with open(path, encoding="utf-8-sig") as f:
        return f.read()


def build():
    current = json.loads(read_text(TARGET))
    plugins = []
    for d in sorted(os.listdir(PLUGINS_DIR)):
        manifest_path = os.path.join(PLUGINS_DIR, d, ".claude-plugin", "plugin.json")
        if not os.path.isdir(os.path.join(PLUGINS_DIR, d)) or not os.path.isfile(manifest_path):
            continue
        m = json.loads(read_text(manifest_path))
        entry = {"name": m["name"], "source": f"./plugins/{d}", "description": m.get("description"),
                 "version": m.get("version")}
        if m.get("keywords"):
            entry["keywords"] = m["keywords"]
        plugins.append(entry)
    nxt = dict(current)
    nxt["plugins"] = plugins
    out = json.dumps(nxt, ensure_ascii=False, indent=2, separators=(",", ": "))
    # A string array stays on one line, like in the hand-edited file.
    out = re.sub(r'\[\s+((?:"[^"\n]*",?\s+)+)\]',
                 lambda m: "[" + re.sub(r",\s+", ", ", m.group(1).strip()) + "]", out)
    return out + "\n", len(plugins)


def main(argv):
    output, count = build()
    if "--check" in argv:
        if read_text(TARGET).replace("\r\n", "\n") != output:
            print("✖  marketplace.json is out of sync — run `python scripts/generate_marketplace.py`.",
                  file=sys.stderr)
            return 1
        print("✔  marketplace.json is up to date.")
        return 0
    with open(TARGET, "w", encoding="utf-8", newline="\n") as f:
        f.write(output)
    print(f"✔  marketplace.json generated ({count} plugin(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
