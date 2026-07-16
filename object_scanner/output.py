import sys
from typing import TextIO

from .models import HistoryCommit, Match, ScanResult


def _limited(items: list, limit: int):
    return items[:limit] if limit > 0 else []


def _print_match(match: Match, prefix: str, stream: TextIO) -> None:
    print(f"{prefix}{match.format()}", file=stream)


def print_usage(program: str, stream: TextIO | None = None) -> None:
    stream = stream or sys.stdout
    print(f"Uso:\n  {program} [opções] <serviço> [serviço...]\n\n"
          "Opções:\n  -v, --verbose          Exibe metadados e resultados completos\n"
          "  --max-current N        Máximo de ocorrências atuais por objeto (padrão: 3)\n"
          "  --max-history N        Máximo de commits por objeto (padrão: 5)\n"
          "  --no-fetch             Não atualiza referências remotas\n"
          "  --pattern ITEM        Item literal a pesquisar; pode ser repetido\n"
          "  --output CAMINHO       Grava um artefato JSON com todos os detalhes\n"
          "  -h, --help             Exibe esta ajuda", file=stream)


def _print_history_entry(commit: HistoryCommit, stream: TextIO) -> None:
    print(f"    {commit.summary()}", file=stream)
    branches = ",".join(commit.branches) or "(nenhuma branch encontrada)"
    tags = ",".join(commit.tags) or "(nenhuma tag encontrada)"
    print(f"      branches: {branches}", file=stream)
    print(f"      tags: {tags}", file=stream)
    for match in commit.commit_matches:
        _print_match(match, "      commit: ", stream)
    for match in commit.parent_matches:
        _print_match(match, "      parent: ", stream)


def print_result(result: ScanResult, settings, stream: TextIO | None = None) -> None:
    stream = stream or sys.stdout
    suffix = " fetch-falhou" if result.fetch_warning else ""
    print(f"\n{result.service} [{result.branch}]{suffix}", file=stream)
    for pattern, matches in result.current.items():
        if matches:
            print(f"  ATUAL     {pattern:<38} {len(matches)} ocorrência(s)", file=stream)
            shown = matches if settings.verbose else _limited(matches, settings.max_current)
            for match in shown:
                _print_match(match, "    ", stream)
            if not settings.verbose and len(matches) > settings.max_current:
                print(f"    ... +{len(matches) - settings.max_current} ocorrência(s)", file=stream)
    for pattern, commits in result.history.items():
        if commits:
            print(f"  HISTÓRICO {pattern:<38} {len(commits)} commit(s)", file=stream)
            shown = commits if settings.verbose else _limited(commits, settings.max_history)
            for commit in shown:
                _print_history_entry(commit, stream)
            if not settings.verbose and len(commits) > settings.max_history:
                print(f"    ... +{len(commits) - settings.max_history} commit(s)", file=stream)
    if not result.has_current and not result.has_history:
        print("  OK        nenhuma referência encontrada", file=stream)
