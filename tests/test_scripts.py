"""Tests for the repository scripts and lean.py — usage: python -m unittest discover -s tests"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
LEAN = os.path.join(ROOT, "plugins", "keemboll-powerbi", "skills", "powerbi-lean", "scripts", "lean.py")
FIXTURE = os.path.join(ROOT, "tests", "fixture", "Demo")


def run(script, *args):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run([sys.executable, script, *args], cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", env=env)


class Repository(unittest.TestCase):
    def test_validate(self):
        r = run(os.path.join(SCRIPTS, "validate.py"))
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_marketplace_in_sync(self):
        r = run(os.path.join(SCRIPTS, "generate_marketplace.py"), "--check")
        self.assertEqual(r.returncode, 0, r.stderr)


class Installation(unittest.TestCase):
    def install(self, target, *args):
        return run(os.path.join(SCRIPTS, "install.py"), "--target", target, *args)

    def test_codex_then_uninstall(self):
        with tempfile.TemporaryDirectory() as t:
            with open(os.path.join(t, "AGENTS.md"), "w", encoding="utf-8") as f:
                f.write("# My project\n\nLocal rule.\n")
            for _ in range(2):  # twice: installation is idempotent
                r = self.install(t, "--agent", "codex")
                self.assertEqual(r.returncode, 0, r.stderr)
            skills = os.path.join(t, ".agents", "skills")
            self.assertTrue(os.path.isfile(os.path.join(skills, "powerbi-lean", "scripts", "lean.py")))
            with open(os.path.join(t, "AGENTS.md"), encoding="utf-8") as f:
                text = f.read()
            self.assertIn("Local rule.", text)
            self.assertEqual(text.count("keemboll-powerbi:begin"), 1)
            self.assertIn(".agents/skills/powerbi-conventions/SKILL.md", text)

            r = self.install(t, "--agent", "codex", "--uninstall")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertFalse(os.path.exists(os.path.join(skills, "powerbi-lean")))
            with open(os.path.join(t, "AGENTS.md"), encoding="utf-8") as f:
                self.assertEqual(f.read(), "# My project\n\nLocal rule.\n")

    def test_folder_per_agent(self):
        for agent, folder in (("grok", ".grok/skills"), ("copilot", ".github/skills"), ("claude", ".claude/skills")):
            with tempfile.TemporaryDirectory() as t:
                r = self.install(t, "--agent", agent, "--skills", "powerbi-tmdl")
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertTrue(os.path.isfile(os.path.join(t, *folder.split("/"), "powerbi-tmdl", "SKILL.md")))
                self.assertEqual(os.path.isfile(os.path.join(t, "AGENTS.md")), agent != "claude")
                self.assertEqual(os.path.isdir(os.path.join(t, ".claude", "agents")), agent == "claude")

    def test_refuses_to_overwrite_a_foreign_skill(self):
        with tempfile.TemporaryDirectory() as t:
            mine = os.path.join(t, ".agents", "skills", "powerbi-tmdl")
            os.makedirs(mine)
            with open(os.path.join(mine, "SKILL.md"), "w", encoding="utf-8") as f:
                f.write("mine")
            r = self.install(t, "--agent", "generic")
            self.assertEqual(r.returncode, 1)
            with open(os.path.join(mine, "SKILL.md"), encoding="utf-8") as f:
                self.assertEqual(f.read(), "mine")
            self.assertFalse(os.path.exists(os.path.join(t, ".agents", "skills", "powerbi-lean")))

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as t:
            r = self.install(t, "--agent", "gemini", "--dry-run")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(os.listdir(t), [])


class Distribution(unittest.TestCase):
    def test_archives(self):
        with tempfile.TemporaryDirectory() as t:
            r = run(os.path.join(SCRIPTS, "build_dist.py"), "--out", t)
            self.assertEqual(r.returncode, 0, r.stderr)
            names = os.listdir(t)
            self.assertIn("powerbi-lean.zip", names)
            with zipfile.ZipFile(os.path.join(t, "powerbi-lean.zip")) as zf:
                self.assertIn("powerbi-lean/SKILL.md", zf.namelist())
                self.assertIn("powerbi-lean/scripts/lean.py", zf.namelist())
            bundle = [n for n in names if n.startswith("keemboll-powerbi-") and n.endswith(".md")]
            self.assertEqual(len(bundle), 1)
            with open(os.path.join(t, bundle[0]), encoding="utf-8") as f:
                self.assertIn("<!-- skill: powerbi-conventions -->", f.read())


class Lean(unittest.TestCase):
    def lean(self, *args):
        r = run(LEAN, *args)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_audit(self):
        res = json.loads(self.lean("audit", FIXTURE, "--json"))
        unused = [f["obj"] for f in res["findings"] if f["cat"] == "Unused"]
        self.assertIn("[Customer Count] (_Measures)", unused)
        self.assertNotIn("[Net Sales] (_Measures)", unused)  # used by the report

    def test_usage(self):
        self.assertIn("Net Sales", self.lean("usage", FIXTURE))

    def test_debt(self):
        rep = json.loads(self.lean("debt", FIXTURE, "--json"))
        self.assertEqual((rep["open"], rep["nextId"]["debt"]), (1, "D-002"))

    def test_catalog(self):
        md = self.lean("catalog", FIXTURE)
        self.assertIn("# Data dictionary", md)
        self.assertIn("Fact_Sales", md)
        self.assertNotIn("@example.com", md)  # an RLS filter containing an email is never copied
        json.loads(self.lean("catalog", FIXTURE, "--json"))

    def test_project_not_found(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertNotEqual(run(LEAN, "audit", t).returncode, 0)


if __name__ == "__main__":
    unittest.main()
