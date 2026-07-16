import subprocess
from dataclasses import dataclass
from pathlib import Path

from .config import EXCLUDED_DIRECTORIES, INCLUDE_PATTERNS
from .models import HistoryCommit, Match


def _run(repository: Path, *args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repository), *args],
        text=True,
        capture_output=True,
        check=check,
    )


def repository_root(directory: Path) -> Path | None:
    result = _run(directory, "rev-parse", "--show-toplevel")
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip())


@dataclass
class GitRepository:
    root: Path
    _updated: bool = False

    def branch(self) -> str:
        result = _run(self.root, "branch", "--show-current")
        return result.stdout.strip() or "detached"

    def update_history(self) -> bool:
        if self._updated:
            return True
        shallow = _run(self.root, "rev-parse", "--is-shallow-repository").stdout.strip() == "true"
        args = ("fetch", "--unshallow", "--all", "--tags", "--prune") if shallow else (
            "fetch", "--all", "--tags", "--prune"
        )
        result = _run(self.root, *args)
        if result.returncode == 0:
            self._updated = True
        return result.returncode == 0

    def history(self, pattern: str) -> list[HistoryCommit]:
        result = _run(
            self.root,
            "log", "--all", "--full-history", "--regexp-ignore-case",
            f"-G{pattern}", "--date=short", "--format=%H|%h|%ad|%an|%s",
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "falha ao consultar histórico Git")
        commits: list[HistoryCommit] = []
        for line in result.stdout.splitlines():
            parts = line.split("|", 4)
            if len(parts) == 5:
                commits.append(HistoryCommit(parts[1], parts[2], parts[3], parts[4], full_hash=parts[0]))
        return commits

    def _pathspecs(self) -> list[str]:
        excluded = [f":(exclude){directory}/**" for directory in EXCLUDED_DIRECTORIES]
        return [*INCLUDE_PATTERNS, *excluded]

    def snapshot_matches(self, revision: str, pattern: str) -> list[Match]:
        result = _run(
            self.root, "grep", "--no-color", "--ignore-case", "--line-number",
            "--fixed-strings", "--", pattern, revision, "--", *self._pathspecs(),
        )
        if result.returncode not in (0, 1):
            return []
        matches: list[Match] = []
        for line in result.stdout.splitlines():
            revision_prefix = f"{revision}:"
            if line.startswith(revision_prefix):
                line = line[len(revision_prefix):]
            path, separator, remainder = line.partition(":")
            line_number, separator, content = remainder.partition(":")
            if not separator:
                continue
            try:
                matches.append(Match(path, int(line_number), content))
            except ValueError:
                continue
        return matches

    def first_parent(self, revision: str) -> str | None:
        result = _run(self.root, "rev-list", "--parents", "-n", "1", revision)
        parts = result.stdout.split()
        return parts[1] if len(parts) > 1 else None

    def containing_branches(self, revision: str) -> tuple[str, ...]:
        result = _run(self.root, "branch", "-a", "--contains", revision)
        return tuple(line.lstrip("* ") for line in result.stdout.splitlines() if line.strip())

    def containing_tags(self, revision: str) -> tuple[str, ...]:
        result = _run(self.root, "tag", "--contains", revision)
        return tuple(line.strip() for line in result.stdout.splitlines() if line.strip())

    def enrich(self, commit: HistoryCommit, pattern: str) -> HistoryCommit:
        parent = self.first_parent(commit.short_hash)
        return HistoryCommit(
            commit.short_hash, commit.date, commit.author, commit.subject,
            self.containing_branches(commit.short_hash),
            self.containing_tags(commit.short_hash),
            tuple(self.snapshot_matches(commit.short_hash, pattern)),
            parent,
            tuple(self.snapshot_matches(parent, pattern)) if parent else (),
            commit.full_hash,
        )
