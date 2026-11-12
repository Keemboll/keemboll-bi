"""Helpers shared by the repository scripts (standard library only, Python 3.8+)."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGINS_DIR = os.path.join(ROOT, "plugins")


def utf8_console():
    """Windows console: force UTF-8."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def read_text(path):
    with open(path, encoding="utf-8-sig") as f:
        return f.read()


def write_text(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def parse_frontmatter(text):
    """Simple YAML frontmatter (single-line key: value) -> dict, or None if absent."""
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text.lstrip("﻿"), re.S)
    if not m:
        return None
    fm = {}
    for line in m.group(1).splitlines():
        kv = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if kv:
            fm[kv.group(1)] = re.sub(r"^[\"']|[\"']$", "", kv.group(2)).strip()
    return fm


def strip_frontmatter(text):
    return re.sub(r"^---\r?\n.*?\r?\n---\r?\n?", "", text.lstrip("﻿"), count=1, flags=re.S)


def plugin_names():
    return [d for d in sorted(os.listdir(PLUGINS_DIR))
            if os.path.isfile(os.path.join(PLUGINS_DIR, d, ".claude-plugin", "plugin.json"))]


def load_plugin(name):
    """Manifest, skills and subagents of a plugin."""
    pdir = os.path.join(PLUGINS_DIR, name)
    manifest = json.loads(read_text(os.path.join(pdir, ".claude-plugin", "plugin.json")))
    skills = []
    sroot = os.path.join(pdir, "skills")
    for s in sorted(os.listdir(sroot)) if os.path.isdir(sroot) else []:
        skill_file = os.path.join(sroot, s, "SKILL.md")
        if os.path.isfile(skill_file):
            fm = parse_frontmatter(read_text(skill_file)) or {}
            skills.append({"name": s, "dir": os.path.join(sroot, s), "description": fm.get("description", "")})
    agents = []
    aroot = os.path.join(pdir, "agents")
    for a in sorted(os.listdir(aroot)) if os.path.isdir(aroot) else []:
        if a.endswith(".md"):
            fm = parse_frontmatter(read_text(os.path.join(aroot, a))) or {}
            agents.append({"name": a[:-3], "path": os.path.join(aroot, a), "description": fm.get("description", "")})
    return {"name": name, "dir": pdir, "manifest": manifest, "version": manifest.get("version", "0.0.0"),
            "skills": skills, "agents": agents}


def short_description(description):
    """Description without the trailing \"Triggers: ...\" keyword list."""
    return re.split(r"\s*Triggers\s*:", description, maxsplit=1)[0].strip()
