import subprocess
import tempfile
import unittest
from pathlib import Path

from object_scanner.git import GitRepository, repository_root


def run_git(repository: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repository), *args], check=True, capture_output=True, text=True)


class GitScannerIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.repository = Path(self.temporary.name)
        run_git(self.repository, "init", "-q")
        run_git(self.repository, "config", "user.email", "test@example.com")
        run_git(self.repository, "config", "user.name", "Test User")

    def tearDown(self):
        self.temporary.cleanup()

    def commit(self, message: str) -> None:
        run_git(self.repository, "add", ".")
        run_git(self.repository, "commit", "-qm", message)

    def test_history_enriches_commit_and_parent_evidence(self):
        source = self.repository / "Job.java"
        source.write_text("CUSTOM_REFERENCE\n", encoding="utf-8")
        self.commit("add object reference")
        source.write_text("removed\n", encoding="utf-8")
        self.commit("remove object reference")

        git = GitRepository(self.repository)
        commits = git.history("CUSTOM_REFERENCE")
        enriched = [git.enrich(commit, "CUSTOM_REFERENCE") for commit in commits]

        self.assertEqual(2, len(enriched))
        removal = enriched[0]
        addition = enriched[1]
        self.assertTrue(removal.branches)
        self.assertEqual("Job.java", removal.parent_matches[0].path)
        self.assertEqual(1, removal.parent_matches[0].line)
        self.assertEqual("Job.java", addition.commit_matches[0].path)
        self.assertEqual(1, addition.commit_matches[0].line)

    def test_repository_root_is_detected_from_nested_directory(self):
        nested = self.repository / "src" / "main"
        nested.mkdir(parents=True)

        self.assertEqual(self.repository, repository_root(nested))


if __name__ == "__main__":
    unittest.main()
