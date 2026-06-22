import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "src")
    return subprocess.run(
        [sys.executable, "-m", "aure"] + list(args),
        cwd=str(ROOT),
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


class AureCliTests(unittest.TestCase):
    def test_cli_eval_prints_output(self):
        proc = run_cli("-e", "print(1 + 2)")

        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, "3\n")
        self.assertEqual(proc.stderr, "")

    def test_cli_runs_source_file(self):
        with tempfile.NamedTemporaryFile("w", suffix=".aure", delete=False) as handle:
            handle.write('print("hello from file")')
            path = handle.name

        try:
            proc = run_cli(path)
        finally:
            os.unlink(path)

        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, "hello from file\n")

    def test_examples_run_successfully(self):
        for example in sorted((ROOT / "examples").glob("*.aure")):
            with self.subTest(example=example.name):
                proc = run_cli(str(example))

                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertEqual(proc.stderr, "")
                self.assertNotEqual(proc.stdout, "")

    def test_cli_version(self):
        proc = run_cli("--version")

        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, "Aure 1.0.0\n")

    def test_cli_reports_errors_to_stderr(self):
        proc = run_cli("-e", "print(missing)")

        self.assertEqual(proc.returncode, 1)
        self.assertEqual(proc.stdout, "")
        self.assertIn("Undefined name 'missing'.", proc.stderr)


if __name__ == "__main__":
    unittest.main()
