import unittest

from object_scanner.models import HistoryCommit, Match, ScanResult


class MatchTests(unittest.TestCase):
    def test_formats_path_line_and_content_as_evidence(self):
        match = Match("src/Job.java", 42, "CUSTOM_REFERENCE")

        self.assertEqual("src/Job.java:42:CUSTOM_REFERENCE", match.format())


class HistoryCommitTests(unittest.TestCase):
    def test_summary_preserves_legacy_pipe_format(self):
        commit = HistoryCommit("abc1234", "2026-07-16", "Ana", "add object")

        self.assertEqual("abc1234|2026-07-16|Ana|add object", commit.summary())


class ScanResultTests(unittest.TestCase):
    def test_presence_flags_reflect_findings(self):
        result = ScanResult("/tmp/service", "service", "main")

        self.assertFalse(result.has_current)
        self.assertFalse(result.has_history)
        result.current["pattern"] = [Match("file.py", 1, "pattern")]
        self.assertTrue(result.has_current)


if __name__ == "__main__":
    unittest.main()
