from pathlib import Path

from .config import Settings
from .filesystem import scan_tree
from .git import GitRepository, repository_root
from .models import ScanResult


class Scanner:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._updated_repositories: set[Path] = set()

    def scan_service(self, provided_path: str) -> ScanResult | None:
        path = Path(provided_path)
        if not path.is_dir() or not os_accessible(path):
            return None
        resolved = path.resolve()
        repository_path = repository_root(resolved)
        repository = GitRepository(repository_path) if repository_path else None
        fetch_warning = False
        branch = "sem-git"
        if repository:
            branch = repository.branch()
            if self.settings.fetch_enabled and repository.root not in self._updated_repositories:
                fetch_warning = not repository.update_history()
                self._updated_repositories.add(repository.root)
        result = ScanResult(str(resolved), resolved.name, branch, fetch_warning)
        for pattern in self.settings.patterns:
            result.current[pattern] = scan_tree(resolved, pattern)
            if repository:
                try:
                    commits = repository.history(pattern)
                    result.history[pattern] = [repository.enrich(commit, pattern) for commit in commits]
                except RuntimeError:
                    result.errors += 1
        return result


def os_accessible(path: Path) -> bool:
    import os
    return os.access(path, os.R_OK)
