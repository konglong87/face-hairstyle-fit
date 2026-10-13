from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.contracts import ROOT

CLI = ROOT / "scripts" / "skill_tools.py"
EXAMPLE = ROOT / "examples" / "provisional-report.json"


class CliTests(unittest.TestCase):
    def run_cli(self, *args, cwd=None):
        return subprocess.run([sys.executable, str(CLI), *map(str, args)],
                              cwd=cwd, capture_output=True, text=True)

    def test_catalog_command_works_outside_root(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_cli("check-catalog", cwd=directory)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_list_and_show(self):
        result = self.run_cli("list")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("sweet", result.stdout)
        self.assertEqual(0, self.run_cli("show", "cool").returncode)
        self.assertNotEqual(0, self.run_cli("show", "missing").returncode)

    def test_report_command(self):
        result = self.run_cli("check-report", EXAMPLE)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_missing_and_malformed_inputs_fail(self):
        self.assertNotEqual(0, self.run_cli("check-report", "not-found.json").returncode)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text("{not json}")
            self.assertNotEqual(0, self.run_cli("check-report", path).returncode)

    def test_render_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested" / "report.html"
            first = self.run_cli("render", EXAMPLE, "--output", output)
            self.assertEqual(0, first.returncode, first.stderr)
            content = output.read_text(encoding="utf-8")
            second = self.run_cli("render", EXAMPLE, "--output", output)
            self.assertNotEqual(0, second.returncode)
            self.assertEqual(content, output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
