from dataclasses import dataclass


INCLUDE_PATTERNS = (
    "*.java", "*.kt", "*.groovy", "*.sql", "*.xml",
    "*.yml", "*.yaml", "*.properties", "*.json", "*.conf",
    "*.sh", "*.py", "*.js", "*.ts",
)
EXCLUDED_DIRECTORIES = frozenset(
    {
        ".git", ".idea", ".settings", ".vscode", ".gradle", ".mvn",
        "target", "build", "dist", "out", "bin", "node_modules",
        "coverage", ".next", ".venv", "venv",
    }
)


@dataclass(frozen=True)
class Settings:
    verbose: bool = False
    max_current: int = 3
    max_history: int = 5
    fetch_enabled: bool = True
    patterns: tuple[str, ...] = ()
