import argparse
import sys
from pathlib import Path

from .artifact import write_artifact
from .config import Settings
from .output import print_result, print_usage
from .scanner import Scanner


def non_negative_integer(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("deve ser inteiro >= 0") from error
    if parsed < 0:
        raise argparse.ArgumentTypeError("deve ser inteiro >= 0")
    return parsed


def build_parser(program: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False, prog=program)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--max-current", type=non_negative_integer, default=3)
    parser.add_argument("--max-history", type=non_negative_integer, default=5)
    parser.add_argument("--no-fetch", action="store_true")
    parser.add_argument("--pattern", "--item", dest="patterns", action="append", default=[],
                        metavar="ITEM", help="Item literal a pesquisar; pode ser repetido")
    parser.add_argument("--output", metavar="CAMINHO", help="Grava um artefato JSON com todos os detalhes")
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("services", nargs="*")
    return parser


def main(argv: list[str] | None = None) -> int:
    program = "scan_objects.py"
    parser = build_parser(program)
    args = parser.parse_args(argv)
    if args.help:
        print_usage(program)
        return 0
    if not args.patterns:
        print("Erro: informe ao menos um item com --pattern ITEM (ou --item ITEM).", file=sys.stderr)
        print_usage(program, sys.stderr)
        return 1
    if not args.services:
        print_usage(program, sys.stdout)
        return 1
    settings = Settings(args.verbose, args.max_current, args.max_history, not args.no_fetch, tuple(args.patterns))
    scanner = Scanner(settings)
    total = len(args.services)
    print(f"Varredura: {total} serviço(s), {len(settings.patterns)} objeto(s)")
    scanned = current = history = invalid = errors = 0
    invalid_services: list[str] = []
    results = []
    for service in args.services:
        result = scanner.scan_service(service)
        if result is None:
            print(f"ERRO  {service:<28} caminho inválido ou ilegível")
            invalid += 1
            invalid_services.append(service)
            continue
        scanned += 1
        results.append(result)
        print_result(result, settings)
        current += int(result.has_current)
        history += int(result.has_history)
        errors += result.errors
    print(f"\nResumo: analisados={scanned} atuais={current} históricos={history} inválidos={invalid} erros={errors}")
    if args.output:
        try:
            write_artifact(
                Path(args.output), settings, results, invalid_services,
                {"analisados": scanned, "atuais": current, "históricos": history,
                 "inválidos": invalid, "erros": errors},
            )
            print(f"Artefato: {args.output}")
        except OSError as error:
            print(f"Erro: não foi possível gravar o artefato: {error}", file=sys.stderr)
            errors += 1
    if scanned == 0:
        return 3
    if current > 0:
        return 10
    if history > 0:
        return 11
    if errors > 0:
        return 2
    return 0
