import tempfile
import unittest
from pathlib import Path

from object_scanner.filesystem import scan_tree


class FilesystemScannerTests(unittest.TestCase):
    def test_scans_included_files_and_skips_excluded_directories(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            included = root / "src" / "Job.java"
            excluded = root / "build" / "generated.java"
            included.parent.mkdir()
            excluded.parent.mkdir()
            included.write_text("first\nCUSTOM_REFERENCE\n", encoding="utf-8")
            excluded.write_text("CUSTOM_REFERENCE\n", encoding="utf-8")

            matches = scan_tree(root, "CUSTOM_REFERENCE")

            self.assertEqual(1, len(matches))
            self.assertEqual(str(included), matches[0].path)
            self.assertEqual(2, matches[0].line)

    def test_matching_is_case_insensitive_and_binary_files_are_skipped(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "config.yml"
            binary = root / "binary.json"
            source.write_text("custom_reference\n", encoding="utf-8")
            binary.write_bytes(b"CUSTOM_REFERENCE\x00")

            matches = scan_tree(root, "CUSTOM_REFERENCE")

            self.assertEqual([str(source)], [match.path for match in matches])


if __name__ == "__main__":
    unittest.main()
