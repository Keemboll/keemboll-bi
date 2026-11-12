#!/usr/bin/env python3
"""Bump the version (plugin.json) of plugins whose content changed between two revisions
without their version having been changed.

Usage: python scripts/bump_versions.py <base> [head]
Level inferred from commit messages: `!:` / BREAKING CHANGE -> major, `feat` -> minor, otherwise patch.
"""
import json
import os
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                          check=True).stdout


def level_of(messages):
    msgs = [m for m in messages if m.strip()]
    if any(re.search(r"BREAKING CHANGE|^\w+(\([^)]*\))?!:", m, re.M) for m in msgs):
        return "major"
    if any(re.search(r"^feat(\(|:)", m, re.M) for m in msgs):
        return "minor"
    return "patch"


def bump(version, level):
    major, minor, patch = (int(x) for x in version.split("."))
    if level == "major":
        return f"{major + 1}.0.0"
    if level == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def main(argv):
    head = argv[1] if len(argv) > 1 and argv[1] else "HEAD"
    base = argv[0] if argv else ""
    if not base or re.fullmatch(r"0+", base):
        base = f"{head}~1"
    try:
        git("rev-parse", "--verify", base)
    except subprocess.CalledProcessError:
        print("No base revision: nothing to do.")
        return 0

    changed = [p for p in git("diff", "--name-only", base, head).splitlines() if p]
    messages = git("log", "--format=%s%n%b%x00", f"{base}..{head}").split("\0")
    level = level_of(messages)

    for d in sorted(os.listdir(os.path.join(ROOT, "plugins"))):
        prefix = f"plugins/{d}/"
        manifest_rel = f"{prefix}.claude-plugin/plugin.json"
        manifest_path = os.path.join(ROOT, manifest_rel)
        if not os.path.isfile(manifest_path):
            continue
        if not any(f.startswith(prefix) and f != manifest_rel for f in changed):
            continue
        try:
            before = json.loads(git("show", f"{base}:{manifest_rel}")).get("version")
        except (subprocess.CalledProcessError, ValueError):
            before = None  # new plugin
        with open(manifest_path, encoding="utf-8-sig") as f:
            text = f.read()
        manifest = json.loads(text)
        if before is None or manifest.get("version") != before:
            print(f"{manifest['name']} : version already handled ({manifest.get('version')}).")
            continue
        nxt = bump(manifest["version"], level)
        text = re.sub(r'("version"\s*:\s*")[^"]+(")', rf"\g<1>{nxt}\g<2>", text, count=1)
        with open(manifest_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        print(f"{manifest['name']} : {manifest['version']} → {nxt} ({level})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
