import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from profile_proof_audit.cli import build_report, main, markdown_links


GOOD_README = """# Manuel Sampedro

## Current Focus

- Agent reliability.

## Selected Work

| Repo | What it proves | Why it matters |
| --- | --- | --- |
| [repo-one](https://github.com/example/repo-one) | Proof | Useful. |
| [repo-two](https://github.com/example/repo-two) | Proof | Useful. |
| [repo-three](https://github.com/example/repo-three) | Proof | Useful. |

## How I Work With Codex

- Evidence first.

## Public Workbench

- [Recipe](./recipes/example.md)

## Latest Proof

- [Recipe](./recipes/example.md)
- [Lab](./labs/example.md)

## Principles

- Ship useful proof.
"""


class ProfileProofAuditTests(unittest.TestCase):
    def test_markdown_links(self) -> None:
        links = markdown_links("See [A](./a.md) and [B](https://example.com).")

        self.assertEqual(links, [("A", "./a.md"), ("B", "https://example.com")])

    def test_good_readme_scores_high(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "recipes").mkdir()
            (root / "labs").mkdir()
            (root / "recipes" / "example.md").write_text("# Recipe\n", encoding="utf-8")
            (root / "labs" / "example.md").write_text("# Lab\n", encoding="utf-8")
            readme = root / "README.md"
            readme.write_text(GOOD_README, encoding="utf-8")
            report = build_report(readme)

        self.assertEqual(report.issues, [])
        self.assertGreaterEqual(report.score, 90)
        self.assertEqual(report.selected_work_rows, 3)

    def test_missing_relative_link_is_issue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            readme = Path(tmp) / "README.md"
            readme.write_text(GOOD_README, encoding="utf-8")
            report = build_report(readme)

        self.assertTrue(any("Broken link" in issue for issue in report.issues))

    def test_missing_sections_are_issues(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            readme = Path(tmp) / "README.md"
            readme.write_text("# Thin Profile\n\nNo proof.\n", encoding="utf-8")
            report = build_report(readme)

        self.assertIn("Current Focus", report.sections_missing)
        self.assertTrue(any("Missing required section" in issue for issue in report.issues))

    def test_cli_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "recipes").mkdir()
            (root / "labs").mkdir()
            (root / "recipes" / "example.md").write_text("# Recipe\n", encoding="utf-8")
            (root / "labs" / "example.md").write_text("# Lab\n", encoding="utf-8")
            readme = root / "README.md"
            readme.write_text(GOOD_README, encoding="utf-8")
            stream = StringIO()

            with redirect_stdout(stream):
                exit_code = main([str(readme), "--format", "json"])

            payload = json.loads(stream.getvalue())

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["schema_version"], "profile-proof-audit.v1")
        self.assertEqual(payload["issues"], [])


if __name__ == "__main__":
    unittest.main()
