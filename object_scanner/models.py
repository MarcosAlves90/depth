from dataclasses import dataclass, field


@dataclass(frozen=True)
class Match:
    path: str
    line: int
    content: str

    def format(self) -> str:
        return f"{self.path}:{self.line}:{self.content}"


@dataclass(frozen=True)
class HistoryCommit:
    short_hash: str
    date: str
    author: str
    subject: str
    branches: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    commit_matches: tuple[Match, ...] = ()
    parent: str | None = None
    parent_matches: tuple[Match, ...] = ()
    full_hash: str = ""

    def summary(self) -> str:
        return f"{self.short_hash}|{self.date}|{self.author}|{self.subject}"


@dataclass
class ScanResult:
    directory: str
    service: str
    branch: str
    fetch_warning: bool = False
    current: dict[str, list[Match]] = field(default_factory=dict)
    history: dict[str, list[HistoryCommit]] = field(default_factory=dict)
    errors: int = 0

    @property
    def has_current(self) -> bool:
        return any(self.current.values())

    @property
    def has_history(self) -> bool:
        return any(self.history.values())
