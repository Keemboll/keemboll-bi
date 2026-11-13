#!/usr/bin/env python3
"""powerbi-lean — read-only analysis of a PBIP project (TMDL + PBIR).

Usage:
  python lean.py audit <PBIP folder | *.SemanticModel | .pbip file> [--changed] [--json]
  python lean.py usage <PBIP folder> [--field "'Table'[Name]" | --field "[Measure]"] [--json]
  python lean.py debt <PBIP folder> [--json]      # state of DEBT.md + CHANGES.md
  python lean.py catalog <PBIP folder> [--json]   # data dictionary (Markdown, standard output)

No file is modified. Python 3.8+; standard library only.
"""
import json
import os
import re
import subprocess
import sys
from collections import deque

if hasattr(sys.stdout, "reconfigure"):  # Windows console: force UTF-8
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

SKIP_DIRS = {".pbi", ".git", "node_modules", "__pycache__"}


# ───────────────────────── utilities ─────────────────────────
def read(path):
    with open(path, encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


def walk(root, pred):
    out = []
    if not os.path.isdir(root):
        return out
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            p = os.path.join(dirpath, name)
            if pred(p):
                out.append(p)
    return sorted(out)


def unquote(s):
    if s and len(s) >= 2 and s.startswith("'") and s.endswith("'"):
        return s[1:-1].replace("''", "'")
    return s


def key(table, name):
    return f"{table}[{name}]"


def is_simple_name(name):
    return re.fullmatch(r"[A-Za-z_]\w*", name) is not None


# ───────────────────────── locating the project ─────────────────────────
def locate(arg):
    p = os.path.abspath(arg or ".")
    sm = None
    if p.endswith(".SemanticModel"):
        sm = p
    elif p.endswith(".pbip"):
        p = os.path.dirname(p)
    if not sm:
        cands = sorted(d for d in os.listdir(p) if d.endswith(".SemanticModel"))
        if not cands:
            raise SystemExit(f"✖  No *.SemanticModel folder in {p}")
        sm = os.path.join(p, cands[0])
    parent = os.path.dirname(sm)
    prefix = os.path.basename(sm)[: -len(".SemanticModel")]
    reports = sorted(d for d in os.listdir(parent) if d.endswith(".Report"))
    rep = f"{prefix}.Report" if f"{prefix}.Report" in reports else (reports[0] if reports else None)
    return {
        "root": parent,
        "model": os.path.join(sm, "definition"),
        "report": os.path.join(parent, rep, "definition") if rep else None,
    }


# ───────────────────────── TMDL parser ─────────────────────────
NAME = r"'(?:[^']|'')+'|[^\s=:'][^=:]*?"
OBJ = re.compile(rf"^([A-Za-z]+)\s+({NAME})\s*(?:=\s*(.*))?$")
PROP_EXPR = re.compile(r"^([A-Za-z]+)\s*=\s*(.*)$")
PROP = re.compile(r"^([A-Za-z]+)\s*:\s*(.*)$")
BARE = re.compile(r"^([A-Za-z]+)$")
QUOTED = re.compile(r"'(?:[^']|'')+'")
OBJECT_KINDS = {
    "table", "column", "measure", "partition", "hierarchy", "level", "calculationGroup",
    "calculationItem", "role", "tablePermission", "relationship", "expression", "annotation",
    "extendedProperty", "perspective", "culture", "model", "database", "ref", "dataSource",
    "linguisticMetadata", "columnPermission",
}


def indent_of(line):
    return len(line) - len(line.lstrip("\t"))


def parse_tmdl(text):
    lines = text.split("\n")
    root = {"kind": "root", "children": [], "level": -1, "props": {}}
    stack = [root]
    desc = []
    i = 0
    n = len(lines)

    def collect(first, lvl):
        nonlocal i
        buf = []
        if first == "```":
            i += 1
            while i < n and lines[i].strip() != "```":
                buf.append(lines[i])
                i += 1
            return "\n".join(buf)
        if first:
            buf.append(first)
        while i + 1 < n:
            nxt = lines[i + 1]
            if nxt.strip() == "":
                buf.append("")
                i += 1
                continue
            if indent_of(nxt) >= lvl + 2:
                buf.append(nxt)
                i += 1
            else:
                break
        return "\n".join(buf).strip()

    while i < n:
        raw = lines[i]
        t = raw.strip()
        if not t:
            i += 1
            continue
        lvl = indent_of(raw)
        if t.startswith("///"):
            desc.append(t[3:].strip())
            i += 1
            continue
        while len(stack) > 1 and stack[-1]["level"] >= lvl:
            stack.pop()
        parent = stack[-1]
        m = OBJ.match(t)
        if m and m.group(1) in OBJECT_KINDS and not PROP.match(QUOTED.sub("x", t)):
            node = {"kind": m.group(1), "name": unquote(m.group(2).strip()), "level": lvl,
                    "props": {}, "children": [], "desc": "\n".join(desc)}
            if m.group(3) is not None:
                node["expr"] = collect(m.group(3).strip(), lvl)
            parent["children"].append(node)
            stack.append(node)
            desc = []
            i += 1
            continue
        desc = []
        m = PROP_EXPR.match(t)
        if m and ":" not in t:
            parent["props"][m.group(1)] = collect(m.group(2).strip(), lvl)
        elif PROP.match(t):
            m = PROP.match(t)
            parent["props"][m.group(1)] = m.group(2).strip()
        elif BARE.match(t):
            word = BARE.match(t).group(1)
            if word in OBJECT_KINDS:
                node = {"kind": word, "name": "", "level": lvl, "props": {}, "children": []}
                parent["children"].append(node)
                stack.append(node)
            else:
                parent["props"][word] = True
        elif m:
            parent["props"][m.group(1)] = collect(m.group(2).strip(), lvl)
        i += 1
    return root


def split_col_ref(s):
    m = re.match(r"^('(?:[^']|'')+'|[^.]+)\.(.+)$", s or "")
    return (unquote(m.group(1)), unquote(m.group(2))) if m else (None, None)


def load_model(model_dir):
    model = {"tables": {}, "measures": {}, "relationships": [], "roles": []}
    for f in walk(model_dir, lambda p: p.endswith(".tmdl")):
        tree = parse_tmdl(read(f))
        for nd in tree["children"]:
            if nd["kind"] == "table":
                tb = {"name": nd["name"], "desc": nd.get("desc", ""), "props": nd["props"], "file": f,
                      "columns": {}, "measures": {}, "hierarchies": [], "partitions": [], "calc_group": None}
                for c in nd["children"]:
                    if c["kind"] == "column":
                        tb["columns"][c["name"]] = {"name": c["name"], "expr": c.get("expr"),
                                                    "props": c["props"], "desc": c.get("desc", "")}
                    elif c["kind"] == "measure":
                        ms = {"name": c["name"], "table": nd["name"], "expr": c.get("expr", ""),
                              "props": c["props"], "desc": c.get("desc", ""), "file": f}
                        tb["measures"][c["name"]] = ms
                        model["measures"][c["name"].lower()] = ms
                    elif c["kind"] == "hierarchy":
                        tb["hierarchies"].append({"name": c["name"], "levels": [
                            {"name": l["name"], "column": unquote(l["props"].get("column"))}
                            for l in c["children"] if l["kind"] == "level"]})
                    elif c["kind"] == "partition":
                        tb["partitions"].append({"name": c["name"], "type": (c.get("expr") or "").strip(),
                                                 "source": c["props"].get("source", "")})
                    elif c["kind"] == "calculationGroup":
                        tb["calc_group"] = [{"name": x["name"], "expr": x.get("expr", "")}
                                            for x in c["children"] if x["kind"] == "calculationItem"]
                model["tables"][nd["name"]] = tb
            elif nd["kind"] == "relationship":
                model["relationships"].append({"name": nd["name"], "props": nd["props"], "file": f,
                                               "from": split_col_ref(nd["props"].get("fromColumn")),
                                               "to": split_col_ref(nd["props"].get("toColumn"))})
            elif nd["kind"] == "role":
                model["roles"].append({"name": nd["name"], "file": f, "perms": [
                    {"table": c["name"], "expr": c.get("expr", "")}
                    for c in nd["children"] if c["kind"] == "tablePermission"]})
    return model


# ───────────────────────── DAX ─────────────────────────
def strip_dax(expr, keep_strings=False):
    """Strip comments (// -- /* */); replace strings with "" unless keep_strings."""
    out, i, n = [], 0, len(expr or "")
    expr = expr or ""
    while i < n:
        c = expr[i]
        nx = expr[i + 1] if i + 1 < n else ""
        if c in ('"', "'"):
            j = i + 1
            while j < n:
                if expr[j] == c and j + 1 < n and expr[j + 1] == c:
                    j += 2
                elif expr[j] == c:
                    break
                else:
                    j += 1
            if c == '"' and not keep_strings:
                out.append('""')
            else:
                out.append(expr[i:j + 1])
            i = j + 1
            continue
        if c == "[":
            j = expr.find("]", i)
            j = n - 1 if j < 0 else j
            out.append(expr[i:j + 1])
            i = j + 1
            continue
        if (c == "/" and nx == "/") or (c == "-" and nx == "-"):
            j = expr.find("\n", i)
            i = n if j < 0 else j
            continue
        if c == "/" and nx == "*":
            j = expr.find("*/", i + 2)
            i = n if j < 0 else j + 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


TBL = r"'(?:[^']|'')+'|[A-Za-z_][A-Za-z0-9_]*"
QUALIFIED = re.compile(rf"({TBL})\s*\[([^\]]+)\]")


def table_pattern(tn):
    quoted = "'" + re.escape(tn.replace("'", "''")) + "'"
    return quoted + ("|" + re.escape(tn) if is_simple_name(tn) else "")


def dax_refs(expr, model):
    code = strip_dax(expr or "")
    cols, measures, tables = set(), set(), set()

    def on_qualified(m):
        tn, name = unquote(m.group(1)), m.group(2)
        tb = model["tables"].get(tn)
        if tb:
            tables.add(tn)
            if name in tb["columns"]:
                cols.add(key(tn, name))
            elif name.lower() in model["measures"]:
                measures.add(name.lower())
        return " "

    rest = QUALIFIED.sub(on_qualified, code)
    for m in re.finditer(r"\[([^\]]+)\]", rest):
        if m.group(1).lower() in model["measures"]:
            measures.add(m.group(1).lower())
    for tn in model["tables"]:
        if re.search(rf"(^|[^\w'])({table_pattern(tn)})(?![\w\[])", rest):
            tables.add(tn)
    return {"cols": cols, "measures": measures, "tables": tables, "code": code}


# ───────────────────────── PBIR ─────────────────────────
def load_report(report_dir, model):
    refs, pages = [], {}
    if not report_dir:
        return {"refs": refs, "pages": pages}
    for f in walk(os.path.join(report_dir, "pages"), lambda p: os.path.basename(p) == "page.json"):
        try:
            j = json.loads(read(f))
            folder = os.path.basename(os.path.dirname(f))
            pages[folder] = j.get("displayName") or folder
        except (ValueError, OSError):
            pass
    for f in walk(report_dir, lambda p: p.endswith(".json")):
        try:
            j = json.loads(read(f))
        except (ValueError, OSError):
            continue
        rel = os.path.relpath(f, report_dir).split(os.sep)
        page = "(report)"
        if "pages" in rel:
            pi = rel.index("pages")
            if pi + 1 < len(rel) and rel[pi + 1] != "pages.json":
                page = pages.get(rel[pi + 1], rel[pi + 1])
        if "visuals" in rel:
            vi = rel.index("visuals")
            vtype = (j.get("visual") or {}).get("visualType", "visual") if isinstance(j, dict) else "visual"
            visual = f"{vtype} {rel[vi + 1]}"
        else:
            visual = os.path.basename(f)

        def entity(expr, aliases):
            sr = (expr or {}).get("SourceRef") or {}
            return sr.get("Entity") or aliases.get(sr.get("Source"))

        def visit(node, aliases):
            if isinstance(node, list):
                for x in node:
                    visit(x, aliases)
                return
            if not isinstance(node, dict):
                return
            al = aliases
            if isinstance(node.get("From"), list):
                al = dict(aliases)
                for fr in node["From"]:
                    if isinstance(fr, dict) and fr.get("Name") and fr.get("Entity"):
                        al[fr["Name"]] = fr["Entity"]
            for kind in ("Measure", "Column"):
                v = node.get(kind)
                if isinstance(v, dict) and v.get("Property") and v.get("Expression"):
                    t = entity(v["Expression"], al)
                    if t:
                        refs.append({"table": t, "name": v["Property"], "kind": kind,
                                     "page": page, "visual": visual, "file": f})
            hl = node.get("HierarchyLevel")
            if isinstance(hl, dict) and isinstance((hl.get("Expression") or {}).get("Hierarchy"), dict):
                h = hl["Expression"]["Hierarchy"]
                t = entity(h.get("Expression"), al)
                if t:
                    col = hl.get("Level")
                    tb = model["tables"].get(t)
                    if tb:
                        for hh in tb["hierarchies"]:
                            if hh["name"] == h.get("Hierarchy"):
                                for lv in hh["levels"]:
                                    if lv["name"] == hl.get("Level") and lv["column"]:
                                        col = lv["column"]
                    refs.append({"table": t, "name": col, "kind": "Column",
                                 "page": page, "visual": visual, "file": f})
            for v in node.values():
                visit(v, al)

        visit(j, {})
    return {"refs": refs, "pages": pages}


# ───────────────────────── usage graph ─────────────────────────
def compute_usage(model, report):
    used_m, used_c, why = set(), set(), {}
    queue = deque()

    def note(k, reason):
        why.setdefault(k, []).append(reason)

    def use_m(name, reason):
        k = name.lower()
        if k not in model["measures"]:
            return
        note("M:" + k, reason)
        if k not in used_m:
            used_m.add(k)
            queue.append(("M", k))

    def use_c(t, name, reason):
        tb = model["tables"].get(t)
        if not tb or name not in tb["columns"]:
            return
        k = key(t, name)
        note("C:" + k, reason)
        if k not in used_c:
            used_c.add(k)
            queue.append(("C", (t, name)))

    def from_dax(expr, reason):
        d = dax_refs(expr, model)
        for m in sorted(d["measures"]):
            use_m(model["measures"][m]["name"], reason)
        for c in sorted(d["cols"]):
            t, name = re.match(r"^(.*)\[(.*)\]$", c).groups()
            use_c(t, name, reason)

    for r in report["refs"]:
        label = f"report: {r['page']} / {r['visual']}"
        if r["kind"] == "Measure":
            use_m(r["name"], label)
        else:
            use_c(r["table"], r["name"], label)
    for rel in model["relationships"]:
        for t, c in (rel["from"], rel["to"]):
            if t:
                use_c(t, c, "relationship")
    for ro in model["roles"]:
        for p in ro["perms"]:
            from_dax(p["expr"], f"role {ro['name']}")
    for tb in model["tables"].values():
        for p in tb["partitions"]:
            if p["type"].lower().startswith("calculated"):
                from_dax(p["source"], f"calculated table {tb['name']}")
        for ci in tb["calc_group"] or []:
            from_dax(ci["expr"], f"calculation group {tb['name']}")
        if tb["props"].get("dataCategory") == "Time":
            for c in tb["columns"].values():
                if c["props"].get("isKey"):
                    use_c(tb["name"], c["name"], "date table key")
    while queue:
        kind, k = queue.popleft()
        if kind == "M":
            m = model["measures"][k]
            from_dax(m["expr"], f"measure [{m['name']}]")
            if m["props"].get("formatStringDefinition"):
                from_dax(m["props"]["formatStringDefinition"], f"format of [{m['name']}]")
        else:
            t, name = k
            c = model["tables"][t]["columns"][name]
            if c.get("expr"):
                from_dax(c["expr"], f"calculated column {key(t, name)}")
            if c["props"].get("sortByColumn"):
                use_c(t, unquote(c["props"]["sortByColumn"]), f"sort order of {key(t, name)}")
    return used_m, used_c, why


# ───────────────────────── audit ─────────────────────────
RULES = [
    ("dateDure", re.compile(r"\bDATE\s*\(\s*\d{4}\s*,", re.I), "Hardcoded date (DATE(yyyy, ...))", 3),
    ("dateSysteme", re.compile(r"\b(TODAY|NOW|UTCTODAY|UTCNOW)\s*\(\s*\)", re.I),
     "System date (TODAY/NOW): result is not reproducible", 2),
    ("iferror", re.compile(r"\b(IFERROR|ISERROR)\s*\(", re.I), "IFERROR / ISERROR", 2),
    ("division", re.compile(r"[\w\])]\s*/\s*[A-Za-z_(\[']"),
     "Division with \"/\" by an expression instead of DIVIDE", 3),
]
COL_CMP = re.compile(rf"({TBL})\s*\[([^\]]+)\]\s*(=|<>|IN)\s*(\{{[^}}]*\}}|\"[^\"]*\"|-?\d+)", re.I)
ID_LIKE = re.compile(r"(^|[\s_])(id|key|code|year|month|quarter|num|no|number|"
                     r"cle|clé|annee|année|mois|trimestre|numero|numéro)([\s_]|$)|(id|key)$", re.I)


def audit(model, report, changed=False, root=None):
    used_m, used_c, _ = compute_usage(model, report)
    findings = []

    def add(prio, cat, obj, detail, file):
        findings.append({"prio": prio, "cat": cat, "obj": obj, "detail": detail, "file": file})

    rel_tables = {t for r in model["relationships"] for t in (r["from"][0], r["to"][0]) if t}
    by_norm = {}
    for m in model["measures"].values():
        obj = f"[{m['name']}] ({m['table']})"
        code = strip_dax(m["expr"])
        with_str = strip_dax(m["expr"], keep_strings=True)
        hidden = bool(m["props"].get("isHidden"))
        if m["name"].lower() not in used_m:
            add(2, "Unused", obj,
                f"{'Hidden measure' if hidden else 'Measure'} never used by the report or by another measure", m["file"])
        for _, rx, label, prio in RULES:
            mm = rx.search(code)
            if mm:
                add(prio, "Hardcoded value / risk", obj, f"{label} — \"{mm.group(0).strip()}\"", m["file"])
        for mm in COL_CMP.finditer(with_str):
            tn, lit = unquote(mm.group(1)), mm.group(4)
            if tn not in model["tables"] or tn not in rel_tables or re.fullmatch(r"-?\d", lit):
                continue
            kind = "Label" if lit.startswith('"') else ("List of values" if lit.startswith("{") else "Numeric value")
            add(3, "Hardcoded value / risk", obj,
                f"Hardcoded {kind.lower()} compared to {tn}[{mm.group(2)}] — \"{mm.group(0)[:80]}\": "
                "use a measure or a reference table", m["file"])
        for tn in model["tables"]:
            if re.search(rf"\bFILTER\s*\(\s*({table_pattern(tn)})\s*,", code, re.I):
                add(2, "DAX", obj, f"FILTER over the whole table {tn}: prefer a column filter "
                                   "or VALUES/ALL on the column", m["file"])
        if not hidden and not m["desc"]:
            add(3, "Documentation", obj, "Visible measure without a description", m["file"])
        if (not hidden and not m["props"].get("formatString") and not m["props"].get("formatStringDefinition")
                and '""' not in code):
            add(3, "Documentation", obj, "Visible measure without a format", m["file"])
        norm = re.sub(r"\s+", "", with_str.lower())
        if len(norm) > 12:
            by_norm.setdefault(norm, []).append(m)
    for grp in by_norm.values():
        if len(grp) > 1:
            add(1, "Duplicate", ", ".join(f"[{m['name']}]" for m in grp),
                "Identical DAX expressions (ignoring comments and whitespace): keep one measure, "
                "make the others reference it", grp[0]["file"])

    rel_cols = {key(*r[side]) for r in model["relationships"] for side in ("from", "to") if r[side][0]}
    fk_cols = {key(*r["from"]) for r in model["relationships"] if r["from"][0]}
    has_date_table = False
    for tb in model["tables"].values():
        if tb["props"].get("dataCategory") == "Time":
            has_date_table = True
        is_measure_table = bool(tb["measures"]) and all(c["props"].get("isHidden") for c in tb["columns"].values())
        if tb["name"] not in rel_tables and not tb["calc_group"] and not is_measure_table:
            add(3, "Structure", tb["name"],
                "Table without a relationship (expected for a parameter / disconnected table; otherwise check it)", tb["file"])
        for c in tb["columns"].values():
            k = key(tb["name"], c["name"])
            if k not in used_c and k not in rel_cols and not is_measure_table:
                add(2, "Unused", k, f"{'Hidden column' if c['props'].get('isHidden') else 'Column'} never used "
                                        "(report, DAX, relationships, sort order): candidate for removal", tb["file"])
            spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", c["name"])
            if str(c["props"].get("summarizeBy", "")).lower() == "sum" and ID_LIKE.search(spaced):
                add(2, "Model", k, "summarizeBy: sum on a column that looks like an identifier / a year: "
                                    "set it to none", tb["file"])
            if k in fk_cols and not c["props"].get("isHidden"):
                add(3, "Model", k, "Visible foreign key: hide it", tb["file"])
    if not has_date_table:
        add(1, "Model", "(model)", "No table marked as a date table (dataCategory: Time + isKey column)", None)

    if changed:
        try:
            def git(*a):
                return subprocess.run(["git", *a], cwd=root, capture_output=True, text=True, check=True).stdout
            top = git("rev-parse", "--show-toplevel").strip()
            files = git("diff", "--name-only", "HEAD").splitlines() + \
                git("ls-files", "--others", "--exclude-standard").splitlines()
            changed_set = {os.path.normcase(os.path.abspath(os.path.join(top, p))) for p in files if p}
            findings = [f for f in findings if f["file"] and os.path.normcase(os.path.abspath(f["file"])) in changed_set]
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠  --changed: Git repository not found, running the full analysis.", file=sys.stderr)

    findings.sort(key=lambda f: (f["prio"], f["cat"]))
    stats = {
        "tables": len(model["tables"]), "measures": len(model["measures"]),
        "columns": sum(len(t["columns"]) for t in model["tables"].values()),
        "relationships": len(model["relationships"]), "reportRefs": len(report["refs"]),
        "usedMeasures": len(used_m), "usedColumns": len(used_c),
    }
    return {"findings": findings, "stats": stats}


# ───────────────────────── output ─────────────────────────
def esc(s):
    return str(s).replace("|", "\\|")


def print_audit(res, loc):
    s = res["stats"]
    print("# powerbi-lean audit\n")
    print(f"Model: {loc['model']}\nReport: {loc['report'] or '(none)'}\n")
    print(f"{s['tables']} tables · {s['measures']} measures ({s['usedMeasures']} used) · {s['columns']} columns "
          f"({s['usedColumns']} used outside relationships) · {s['relationships']} relationships · "
          f"{s['reportRefs']} field references in the report\n")
    if not loc["report"]:
        print("> ⚠ No .Report folder: report usage is not checked.\n")
    print("> \"Unused\" = not referenced by THIS report. Other reports connected to the published model "
          "may use it: check before deleting.\n")
    for p in (1, 2, 3):
        rows = [f for f in res["findings"] if f["prio"] == p]
        if not rows:
            continue
        print(f"## Priority {p} ({len(rows)})\n\n| Category | Object | Finding |\n|---|---|---|")
        for f in rows:
            print(f"| {f['cat']} | {esc(f['obj'])} | {esc(f['detail'])} |")
        print()
    if not res["findings"]:
        print("No findings.")


def print_usage(model, report, field, as_json):
    used_m, used_c, why = compute_usage(model, report)
    if field:
        m = re.match(r"^(?:('(?:[^']|'')+'|[^\[]+))?\[(.+)\]$", field)
        if not m:
            raise SystemExit(f"✖  --field expected as Table[Name] or [Measure] : {field}")
        t = unquote(m.group(1).strip()) if m.group(1) else None
        name = m.group(2)
        is_col = bool(t and model["tables"].get(t) and name in model["tables"][t]["columns"])
        used_by = list(dict.fromkeys(why.get("M:" + name.lower(), []) + (why.get("C:" + key(t, name), []) if t else [])))
        target = key(t, name) if is_col else name.lower()
        deps = [f"[{x['name']}]" for x in model["measures"].values()
                if target in dax_refs(x["expr"], model)["cols" if is_col else "measures"]]
        out = {"field": field, "usedBy": used_by, "referencedByMeasures": deps}
        if as_json:
            print(json.dumps(out, ensure_ascii=False, indent=2))
            return
        print(f"# Usage of {field}\n")
        if not used_by and not deps:
            print("No usage found (report, DAX, relationships, sort order, roles).")
        for u in used_by:
            print(f"- {u}")
        if deps:
            print(f"\nReferenced in the DAX of: {', '.join(deps)}")
        print("\nBefore a rename: update each of these places "
              "(PBIR report, DAX, relationships, sort order, roles, cultures).")
        return
    rows = [{"page": r["page"], "visual": r["visual"],
             "field": f"[{r['name']}]" if r["kind"] == "Measure" else key(r["table"], r["name"])}
            for r in report["refs"]]
    if as_json:
        print(json.dumps({"refs": rows, "usedMeasures": sorted(used_m), "usedColumns": sorted(used_c)},
                         ensure_ascii=False, indent=2))
        return
    print("# Fields used by the report\n\n| Page | Visual | Field |\n|---|---|---|")
    seen = set()
    for r in rows:
        k = (r["page"], r["visual"], r["field"])
        if k not in seen:
            seen.add(k)
            print(f"| {esc(r['page'])} | {esc(r['visual'])} | {esc(r['field'])} |")



# ───────────────────────── debt & change log ─────────────────────────
DEBT_ID = re.compile(r"\bD-\d{3,}\b")
CHG_ID = re.compile(r"\bC-\d{3,}\b")
DEBT_REF = re.compile(r"\b(D-\d{3,})\b(?:\s*\((partial|in progress)\))?", re.I)
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def field(body, name):
    m = re.search(rf"\*\*{name}\*\*\s*:\s*([^\n·]+)", body, re.I)
    return m.group(1).strip() if m else ""


def parse_debt(path):
    """DEBT.md: sections "## Open" / "## Closed", entries "### D-001 · title"."""
    items, section = [], None
    if not os.path.isfile(path):
        return items
    text = read(path)
    for block in re.split(r"(?m)^(?=#{2,3} )", text):
        head = block.split("\n", 1)[0]
        if head.startswith("## "):
            low = head.lower()
            section = "closed" if "closed" in low else ("open" if "open" in low else section)
            continue
        m = re.match(r"^### (D-\d{3,})\s*[·\-:]\s*(.*)$", head)
        if not m:
            continue
        body = block.split("\n", 1)[1] if "\n" in block else ""
        items.append({
            "id": m.group(1), "title": m.group(2).strip(), "status": section or "open",
            "priority": field(body, "Priority").lower() or "unspecified",
            "due": (DATE.search(field(body, "Due")) or [None])[0] if field(body, "Due") else None,
            "closed": (DATE.search(field(body, "Closed on")) or [None])[0] if field(body, "Closed on") else None,
            "mods": CHG_ID.findall(field(body, "Change")),
        })
    return items


def parse_mods(path):
    """CHANGES.md: entries "## C-001 · 2026-10-20 · title" (newest first)."""
    mods = []
    if not os.path.isfile(path):
        return mods
    for block in re.split(r"(?m)^(?=## )", read(path)):
        head = block.split("\n", 1)[0]
        m = re.match(r"^## (C-\d{3,})\s*[·\-:]\s*(.*)$", head)
        if not m:
            continue
        body = block.split("\n", 1)[1] if "\n" in block else ""
        d = DATE.search(m.group(2))
        mods.append({"id": m.group(1), "date": d.group(0) if d else None,
                     "title": DATE.sub("", m.group(2)).strip(" ·-:"),
                     "debts": [d for d, mark in DEBT_REF.findall(field(body, "Debt")) if not mark],
                     "partial": [d for d, mark in DEBT_REF.findall(field(body, "Debt")) if mark],
                     "type": field(body, "Type")})
    return mods


def debt_report(root, today=None):
    import datetime
    today = today or datetime.date.today().isoformat()
    debts = parse_debt(os.path.join(root, "DEBT.md"))
    mods = parse_mods(os.path.join(root, "CHANGES.md"))
    by_id = {d["id"]: d for d in debts}
    open_ = [d for d in debts if d["status"] == "open"]
    closed = [d for d in debts if d["status"] == "closed"]
    mod_ids = {m["id"] for m in mods}
    debts_in_mods = {x for m in mods for x in m["debts"]}
    issues = []
    for d in open_:
        if d["due"] and d["due"] < today:
            issues.append(f"{d['id']}: overdue ({d['due']})")
        if d["id"] in debts_in_mods:
            issues.append(f"{d['id']}: cited in CHANGES.md but still \"Open\" in DEBT.md")
    for d in closed:
        if not d["mods"] and d["id"] not in debts_in_mods:
            issues.append(f"{d['id']}: closed without a linked change in CHANGES.md")
        for mid in d["mods"]:
            if mid not in mod_ids:
                issues.append(f"{d['id']}: points to {mid}, which is missing from CHANGES.md")
    for m in mods:
        for did in m["debts"] + m["partial"]:
            if did not in by_id:
                issues.append(f"{m['id']}: cites {did}, which is missing from DEBT.md")
    ids = [int(m["id"][2:]) for m in mods]
    if len(ids) != len(set(ids)):
        issues.append("CHANGES.md: duplicate C-xxx identifiers")
    prio = {}
    for d in open_:
        prio[d["priority"]] = prio.get(d["priority"], 0) + 1
    total = len(debts)
    return {
        "today": today, "total": total, "open": len(open_), "closed": len(closed),
        "progress": round(100 * len(closed) / total) if total else None,
        "openByPriority": prio, "changes": len(mods),
        "lastChange": mods[0] if mods else None,
        "nextId": {"debt": f"D-{max([int(d['id'][2:]) for d in debts] or [0]) + 1:03d}",
                   "change": f"C-{max(ids or [0]) + 1:03d}"},
        "openItems": [{k: d[k] for k in ("id", "title", "priority", "due")} for d in open_],
        "issues": issues,
    }


def print_debt(rep, root):
    print("# Debt and changes\n")
    print(f"Project: {root}\n")
    if not rep["total"] and not rep["changes"]:
        print("Neither DEBT.md nor CHANGES.md found at the project root.")
        return
    bar = ""
    if rep["progress"] is not None:
        filled = rep["progress"] // 5
        bar = "█" * filled + "░" * (20 - filled)
    print(f"| Debt | Value |\n|---|---|")
    print(f"| Entries | {rep['total']} |\n| Open | {rep['open']} |\n| Closed | {rep['closed']} |")
    if rep["progress"] is not None:
        print(f"| Progress | {bar} {rep['progress']}% |")
    print(f"| Changes logged | {rep['changes']} |\n")
    if rep["openByPriority"]:
        print("Open by priority: " + ", ".join(f"{k} {v}" for k, v in sorted(rep["openByPriority"].items())) + "\n")
    if rep["lastChange"]:
        lm = rep["lastChange"]
        print(f"Last change: {lm['id']} · {lm['date'] or '?'} · {lm['title']}\n")
    print(f"Next identifiers: {rep['nextId']['debt']} (debt), {rep['nextId']['change']} (change)\n")
    if rep["issues"]:
        print("## Inconsistencies\n")
        for i in rep["issues"]:
            print(f"- {i}")
    else:
        print("No inconsistency between DEBT.md and CHANGES.md.")


# ───────────────────────── catalog ─────────────────────────
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def mask(s):
    """Never put an email address in generated documentation."""
    return EMAIL.sub("(email masked)", s or "")
TABLE_TYPES = (("Fact_", "fact"), ("Dim_", "dimension"), ("_Measures", "measures"),
               ("Param_", "parameter"), ("CG_", "calculation group"))  # prefixes from powerbi-conventions


def catalog(model, report, loc):
    """Data dictionary (JSON structure); nothing is written to disk."""
    import datetime
    used_m, _, _ = compute_usage(model, report)
    has_report = bool(loc["report"])
    tables, undocumented = [], []
    for tn in sorted(model["tables"]):
        tb = model["tables"][tn]
        ttype = "calculation group" if tb["calc_group"] is not None else next(
            (lab for pre, lab in TABLE_TYPES if tn.startswith(pre)), "")
        t_hidden = bool(tb["props"].get("isHidden"))
        cols = []
        for c in tb["columns"].values():
            p = c["props"]
            cols.append({"name": c["name"], "dataType": p.get("dataType", ""), "description": mask(c["desc"]),
                         "hidden": bool(p.get("isHidden")), "calculated": c.get("expr") is not None,
                         "summarizeBy": p.get("summarizeBy", ""),
                         "sortByColumn": unquote(p.get("sortByColumn", "")) or "",
                         "formatString": p.get("formatString", "")})
            if not c["desc"] and not p.get("isHidden") and not t_hidden:
                undocumented.append({"kind": "column", "object": key(tn, c["name"])})
        measures = []
        for m in tb["measures"].values():
            p = m["props"]
            fmt = p.get("formatString", "") or ("(dynamic)" if p.get("formatStringDefinition") else "")
            measures.append({"name": m["name"], "displayFolder": p.get("displayFolder", ""),
                             "description": mask(m["desc"]), "formatString": fmt, "hidden": bool(p.get("isHidden")),
                             "expression": mask(dedent_expr(m["expr"])),
                             "usedByReport": (m["name"].lower() in used_m) if has_report else None})
            if not m["desc"] and not p.get("isHidden"):
                undocumented.append({"kind": "measure", "object": f"[{m['name']}] ({tn})"})
        measures.sort(key=lambda x: (x["displayFolder"].lower(), x["name"].lower()))
        if not tb["desc"] and not t_hidden and ttype != "measures":
            undocumented.append({"kind": "table", "object": tn})
        tables.append({"name": tn, "type": ttype, "description": mask(tb["desc"]), "hidden": t_hidden,
                       "columns": cols, "measures": measures})
    rels = []
    for r in model["relationships"]:
        p = r["props"]
        rels.append({"from": key(*r["from"]) if r["from"][0] else "?", "to": key(*r["to"]) if r["to"][0] else "?",
                     "cardinality": f"{p.get('fromCardinality', 'many')} → {p.get('toCardinality', 'one')}",
                     "crossFiltering": p.get("crossFilteringBehavior", "oneDirection"),
                     "active": str(p.get("isActive", "true")).lower() != "false"})
    rels.sort(key=lambda x: (x["from"], x["to"]))
    roles = []
    for ro in sorted(model["roles"], key=lambda x: x["name"]):
        perms = []
        for pm in ro["perms"]:
            masked = bool(EMAIL.search(pm["expr"] or ""))  # never put personal data in the documentation
            perms.append({"table": pm["table"], "expression": None if masked else pm["expr"], "masked": masked})
        roles.append({"name": ro["name"], "permissions": perms})
    name = os.path.basename(os.path.dirname(loc["model"]))
    return {
        "model": name[: -len(".SemanticModel")] if name.endswith(".SemanticModel") else name,
        "generated": datetime.date.today().isoformat(), "hasReport": has_report,
        "stats": {"tables": len(tables), "columns": sum(len(t["columns"]) for t in tables),
                  "measures": sum(len(t["measures"]) for t in tables), "relationships": len(rels),
                  "roles": len(roles), "undocumented": len(undocumented)},
        "tables": tables, "relationships": rels, "roles": roles, "undocumented": undocumented,
    }


def cell(s):
    return esc(" ".join(str(s or "").split()))


def yn(b):
    return "yes" if b else "no"


def dedent_expr(expr):
    """Multi-line expression: strip the TMDL indentation shared by the lines after the first."""
    lines = expr.strip("\n").split("\n")
    rest = [ln for ln in lines[1:] if ln.strip()]
    pad = min((len(ln) - len(ln.lstrip("\t ")) for ln in rest), default=0)
    return "\n".join([lines[0].strip()] + [ln[pad:] for ln in lines[1:]])


def print_catalog(cat):
    s = cat["stats"]
    print(f"# Data dictionary — {cat['model']}\n")
    print(f"> Generated on {cat['generated']} by `lean.py catalog`. Do not edit this file by hand: "
          "fix the description in the model (TMDL), then regenerate.\n")
    print(f"{s['tables']} tables · {s['columns']} columns · {s['measures']} measures · "
          f"{s['relationships']} relationships · {s['roles']} roles · {s['undocumented']} visible objects without a description\n")
    if not cat["hasReport"]:
        print("> ⚠ No .Report folder: \"used by the report\" is not filled in.\n")
    print("## Tables\n\n| Table | Type | Hidden | Columns | Measures | Description |\n|---|---|---|---|---|---|")
    for t in cat["tables"]:
        print(f"| {esc(t['name'])} | {t['type']} | {yn(t['hidden'])} | {len(t['columns'])} | "
              f"{len(t['measures'])} | {cell(t['description'])} |")
    for t in cat["tables"]:
        print(f"\n## {t['name']}\n")
        if t["description"]:
            print(t["description"] + "\n")
        if t["columns"]:
            print("### Columns\n\n| Column | Type | Description | Hidden | Aggregation | Sorted by | Format |\n"
                  "|---|---|---|---|---|---|---|")
            for c in t["columns"]:
                dtype = c["dataType"] + (" (calculated)" if c["calculated"] else "")
                print(f"| {esc(c['name'])} | {dtype} | {cell(c['description'])} | {yn(c['hidden'])} | "
                      f"{c['summarizeBy']} | {esc(c['sortByColumn'])} | {cell(c['formatString'])} |")
            print()
        folder = None
        for m in t["measures"]:
            if m["displayFolder"] != folder:
                folder = m["displayFolder"]
                print(f"### Measures — {folder or '(no folder)'}\n")
            print(f"#### {m['name']}\n")
            print(m["description"] or "_No description._")
            bits = [f"Format: `{m['formatString']}`" if m["formatString"] else "Format: —",
                    f"Hidden: {yn(m['hidden'])}"]
            if m["usedByReport"] is not None:
                bits.append(f"Used by the report: {yn(m['usedByReport'])}")
            print("\n" + " · ".join(bits) + "\n")
            print("```dax\n" + m["expression"] + "\n```\n")
    print("\n## Relationships\n")
    if cat["relationships"]:
        print("| From | To | Cardinality | Cross-filtering | Active |\n|---|---|---|---|---|")
        for r in cat["relationships"]:
            print(f"| {esc(r['from'])} | {esc(r['to'])} | {r['cardinality']} | {r['crossFiltering']} | "
                  f"{yn(r['active'])} |")
    else:
        print("No relationships.")
    print("\n## Security roles (RLS)\n")
    if cat["roles"]:
        print("| Role | Filtered table | Filter |\n|---|---|---|")
        for ro in cat["roles"]:
            for pm in ro["permissions"] or [{"table": "(none)", "expression": "", "masked": False}]:
                expr = "(masked: contains an email address)" if pm["masked"] else (
                    f"`{cell(pm['expression'])}`" if pm["expression"] else "(no row filter)")
                print(f"| {esc(ro['name'])} | {esc(pm['table'])} | {expr} |")
    else:
        print("No roles.")
    print("\n## Without a description\n")
    if cat["undocumented"]:
        print("Visible objects to document **in the model** (ask for the business definition, do not invent it):\n")
        for u in cat["undocumented"]:
            print(f"- {u['kind']} {u['object']}")
    else:
        print("All visible objects have a description.")


# ───────────────────────── main ─────────────────────────
def main(argv):
    if not argv or argv[0] not in ("audit", "usage", "debt", "catalog"):
        print('Usage: python lean.py audit|usage|debt|catalog <PBIP folder> [--changed] [--field "Table[Name]"] [--json]')
        return 0 if not argv else 1
    cmd, rest = argv[0], argv[1:]
    target = rest[0] if rest and not rest[0].startswith("--") else "."
    if cmd == "debt":
        root = os.path.dirname(os.path.abspath(target)) if target.endswith(".pbip") else os.path.abspath(target)
        if root.endswith((".SemanticModel", ".Report")):
            root = os.path.dirname(root)
        rep = debt_report(root)
        if "--json" in rest:
            print(json.dumps(rep, ensure_ascii=False, indent=2))
        else:
            print_debt(rep, root)
        return 0
    field = rest[rest.index("--field") + 1] if "--field" in rest and rest.index("--field") + 1 < len(rest) else None
    loc = locate(target)
    model = load_model(loc["model"])
    report = load_report(loc["report"], model)
    if cmd == "audit":
        res = audit(model, report, changed="--changed" in rest, root=loc["root"])
        if "--json" in rest:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print_audit(res, loc)
    elif cmd == "catalog":
        cat = catalog(model, report, loc)
        if "--json" in rest:
            print(json.dumps(cat, ensure_ascii=False, indent=2))
        else:
            print_catalog(cat)
    else:
        print_usage(model, report, field, "--json" in rest)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001
        print(f"✖  {exc}", file=sys.stderr)
        sys.exit(1)
