import fnmatch
import os
from pathlib import Path

from .config import EXCLUDED_DIRECTORIES, INCLUDE_PATTERNS
from .models import Match


def _is_included(filename: str) -> bool:
    return any(fnmatch.fnmatch(filename, pattern) for pattern in INCLUDE_PATTERNS)


def scan_tree(directory: Path, pattern: str) -> list[Match]:
    matches: list[Match] = []
    for root, directories, filenames in os.walk(directory, onerror=lambda _error: None):
        directories[:] = [name for name in directories if name not in EXCLUDED_DIRECTORIES]
        for filename in filenames:
            if not _is_included(filename):
                continue
            path = Path(root) / filename
            try:
                data = path.read_bytes()
            except OSError:
                continue
            if b"\x00" in data:
                continue
            for line_number, line in enumerate(data.decode("utf-8", errors="replace").splitlines(), 1):
                if pattern.casefold() in line.casefold():
                    matches.append(Match(str(path), line_number, line))
    return matches
