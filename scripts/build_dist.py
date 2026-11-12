#!/usr/bin/env python3
"""Build the distributable archives in dist/ (folder ignored by Git).

Usage: python scripts/build_dist.py [--out <folder>] [--plugin <name>]

For each plugin:
  dist/<skill>.zip                 a single skill (upload to an app that accepts a skill .zip)
  dist/<plugin>-<version>.zip      all skills + subagents (unzip into .agents/skills/, etc.)
  dist/<plugin>-<version>.md       all skills in one Markdown file, for an agent without file
                                   access (web chat, project, custom instructions)
"""
import os
import sys
import zipfile

from common import ROOT, load_plugin, plugin_names, read_text, strip_frontmatter, utf8_console, write_text

SKIP = {"__pycache__", ".gitkeep"}
FIXED_DATE = (2020, 1, 1, 0, 0, 0)  # reproducible archives


def files_of(folder):
    out = []
    for dirpath, dirnames, filenames in os.walk(folder):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP)
        for name in sorted(filenames):
            if name not in SKIP and not name.endswith(".pyc"):
                out.append(os.path.join(dirpath, name))
    return out


def add(zf, path, arcname):
    info = zipfile.ZipInfo(arcname.replace(os.sep, "/"), FIXED_DATE)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    with open(path, "rb") as f:
        zf.writestr(info, f.read())


def single_file(plugin):
    """All skills in a single Markdown file: SKILL.md then the text references."""
    out = [f"# {plugin['name']} {plugin['version']} — Power BI skills in a single file", "",
           "Power BI working rules. Before acting, find the relevant skill section and apply it.",
           "The Python scripts (`scripts/`) are not included: they need an agent with file access.", ""]
    for s in plugin["skills"]:
        out += ["", "---", "", f"<!-- skill: {s['name']} -->", f"> **When to use it** : {s['description']}", "",
                strip_frontmatter(read_text(os.path.join(s["dir"], "SKILL.md"))).strip(), ""]
        for path in files_of(os.path.join(s["dir"], "references")):
            rel = os.path.relpath(path, s["dir"]).replace(os.sep, "/")
            ext = os.path.splitext(path)[1].lower()
            if ext == ".md":
                out += ["", f"<!-- {s['name']}/{rel} -->", read_text(path).strip(), ""]
            elif ext in (".json", ".html", ".svg", ".dax", ".tmdl", ".yml", ".yaml"):
                out += ["", f"<!-- {s['name']}/{rel} -->", f"```{ext[1:]}", read_text(path).strip(), "```", ""]
    return "\n".join(out) + "\n"


def main(argv):
    utf8_console()
    out_dir = os.path.join(ROOT, "dist")
    only = None
    it = iter(argv)
    for a in it:
        if a == "--out":
            out_dir = os.path.abspath(next(it))
        elif a == "--plugin":
            only = next(it)
        else:
            print(__doc__)
            return 0 if a in ("-h", "--help") else 2
    os.makedirs(out_dir, exist_ok=True)
    for name in plugin_names():
        if only and name != only:
            continue
        plugin = load_plugin(name)
        base = f"{name}-{plugin['version']}"
        with zipfile.ZipFile(os.path.join(out_dir, base + ".zip"), "w") as bundle:
            for s in plugin["skills"]:
                with zipfile.ZipFile(os.path.join(out_dir, s["name"] + ".zip"), "w") as zf:
                    for path in files_of(s["dir"]):
                        rel = os.path.join(s["name"], os.path.relpath(path, s["dir"]))
                        add(zf, path, rel)
                        add(bundle, path, os.path.join("skills", rel))
            for a in plugin["agents"]:
                add(bundle, a["path"], os.path.join("agents", a["name"] + ".md"))
        write_text(os.path.join(out_dir, base + ".md"), single_file(plugin))
        print(f"✔  {name} {plugin['version']}: {len(plugin['skills'])} skill .zip file(s), {base}.zip, {base}.md "
              f"→ {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
