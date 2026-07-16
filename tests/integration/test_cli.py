import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from object_scanner.cli import main


class CliIntegrationTests(unittest.TestCase):
    def test_invalid_service_returns_exit_code_three(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = main(["--no-fetch", "--pattern", "CUSTOM_REFERENCE", "/path/that/does/not/exist"])

        self.assertEqual(3, status)
        self.assertIn("caminho inválido", output.getvalue())

    def test_current_match_returns_exit_code_ten_and_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "Job.py"
            source.write_text("CUSTOM_REFERENCE\n", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = main(["--no-fetch", "--pattern", "CUSTOM_REFERENCE", str(Path(temporary))])

        self.assertEqual(10, status)
        self.assertIn("Job.py:1:CUSTOM_REFERENCE", output.getvalue())

    def test_output_artifact_contains_unlimited_structured_details(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "Job.py"
            artifact = root / "out" / "scan.json"
            artifact.parent.mkdir()
            source.write_text("CUSTOM_REFERENCE\n", encoding="utf-8")

            status = main(["--no-fetch", "--pattern", "CUSTOM_REFERENCE", "--max-current", "0", "--output", str(artifact), str(root)])
            document = json.loads(artifact.read_text(encoding="utf-8"))

        self.assertEqual(10, status)
        self.assertEqual("depth.scan.v1", document["schema"])
        self.assertEqual(1, document["resumo"]["atuais"])
        match = document["serviços"][0]["atuais"]["CUSTOM_REFERENCE"]["matches"][0]
        self.assertEqual(str(source), match["arquivo"])
        self.assertEqual(1, match["linha"])

    def test_item_alias_and_missing_item_are_supported(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "Job.py"
            source.write_text("CUSTOM_REFERENCE\n", encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = main(["--no-fetch", "--item", "CUSTOM_REFERENCE", str(Path(temporary))])

        self.assertEqual(10, status)
        self.assertIn("CUSTOM_REFERENCE", output.getvalue())

        with contextlib.redirect_stderr(io.StringIO()):
            status_without_item = main(["--no-fetch", str(Path(temporary))])
        self.assertEqual(1, status_without_item)


if __name__ == "__main__":
    unittest.main()
