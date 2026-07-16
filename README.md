# depth

Deep Examination of Project Trees and History.

`depth` searches user-provided references in service trees and, when a service is
inside a Git repository, throughout its complete history. Historical output
identifies the commit, hash, branches, tags, file, line, and matching content
in both the commit and its first parent.

## Requirements

- Python 3.10 or newer;
- Git available on `PATH` for historical analysis;
- no external Python dependencies.

## Local usage

```bash
python3 scan_objects.py --help
python3 scan_objects.py --no-fetch \
  --pattern CUSTOM_REFERENCE ./service-a ./service-b
```

By default, the tool may update remote references before querying history. Use
`--no-fetch` for an offline execution.

Main options:

- `--verbose` displays all findings in the terminal;
- `--max-current N` limits current occurrences displayed;
- `--max-history N` limits historical commits displayed;
- `--output scan.json` writes a complete, untruncated JSON artifact;
- `--no-fetch` disables remote updates.
- `--pattern ITEM` adds a literal item to search; repeat it for multiple items.
- `--item ITEM` is an alias for `--pattern`.

At least one `--pattern ITEM` (or `--item ITEM`) is required. Items are searched
literally and case-insensitively.

The program returns `0` with no findings, `10` with current findings, `11` with
historical findings, `3` when no valid path is provided, and `2` on a scan
error.

## JSON artifact

```bash
python3 scan_objects.py --no-fetch --pattern CUSTOM_REFERENCE \
  --output scan.json ./service-a
```

The artifact uses the `depth.scan.v1` schema and contains the configuration,
summary, invalid services, current matches, and historical commits with hashes,
authors, branches, tags, commit/parent snapshots, files, lines, and matching
content.

## Tests

```bash
python3 -m unittest discover -s tests -t .
python3 -m compileall -q object_scanner scan_objects.py
```

See [`docs/TESTING.md`](docs/TESTING.md) for the test strategy and test tree.

## Architecture

See [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md)
for the separation between the CLI, scanner, filesystem, Git, models, and
artifacts.

## Deployment and contribution

There is no server or deployment process: this is a CLI tool executed in the
environment containing the services being analyzed. To contribute, run the
tests, preserve the modular separation, and use Conventional Commits.
