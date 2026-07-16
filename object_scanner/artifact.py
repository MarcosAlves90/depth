import json
from datetime import datetime, timezone
from pathlib import Path

from .models import HistoryCommit, Match, ScanResult


def _match(match: Match) -> dict:
    return {"arquivo": match.path, "linha": match.line, "conteúdo": match.content}


def _commit(commit: HistoryCommit) -> dict:
    return {
        "hash_curto": commit.short_hash,
        "hash_completo": commit.full_hash,
        "data": commit.date,
        "autor": commit.author,
        "assunto": commit.subject,
        "branches": list(commit.branches),
        "tags": list(commit.tags),
        "commit": [_match(match) for match in commit.commit_matches],
        "pai": commit.parent,
        "parent": [_match(match) for match in commit.parent_matches],
    }


def _service(result: ScanResult) -> dict:
    return {
        "diretório": result.directory,
        "serviço": result.service,
        "branch_atual": result.branch,
        "fetch_warning": result.fetch_warning,
        "erros": result.errors,
        "atuais": {
            pattern: {"ocorrências": len(matches), "matches": [_match(match) for match in matches]}
            for pattern, matches in result.current.items()
        },
        "histórico": {
            pattern: {"commits": len(commits), "matches": [_commit(commit) for commit in commits]}
            for pattern, commits in result.history.items()
        },
    }


def write_artifact(path: Path, settings, results: list[ScanResult], invalid_services: list[str], summary: dict) -> None:
    document = {
        "schema": "depth.scan.v1",
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "configuração": {
            "verbose": settings.verbose,
            "max_current": settings.max_current,
            "max_history": settings.max_history,
            "fetch_enabled": settings.fetch_enabled,
            "padrões": list(settings.patterns),
        },
        "resumo": summary,
        "serviços_inválidos": invalid_services,
        "serviços": [_service(result) for result in results],
    }
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
