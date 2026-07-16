# Architecture

## Overview

The [`scan_objects.py`](../../scan_objects.py) entrypoint delegates execution
to `object_scanner.cli`. The package does not keep persistent state: each run
receives paths, scans their current state, and queries Git when available.

## Modules

- `config.py` — patterns, extensions, excluded directories, and immutable
  options;
- `models.py` — current matches, historical commits, and service results;
- `filesystem.py` — current-tree scanning without external subprocesses;
- `git.py` — repository discovery, optional fetch, history, refs, and
  commit/parent snapshots;
- `scanner.py` — coordinates scanning per service;
- `output.py` — human-readable limited or verbose output;
- `artifact.py` — complete serialization using the `depth.scan.v1` schema;
- `cli.py` — argument parsing, summary, and exit codes.

## Flow

```text
CLI → Scanner → filesystem.py
            └→ git.py → history + snapshots
       ├→ output.py   → terminal
       └→ artifact.py → complete JSON
```

## Decisions

- The Python standard library is sufficient; there are no external
  dependencies.
- Terminal output may be limited for quick reading.
- The JSON artifact never uses those display limits and preserves complete
  evidence.
- The first parent is used to identify references removed by a commit.
- Remote updates remain available by default for historical accuracy, while
  `--no-fetch` enables offline execution.

## Boundaries

The project exposes no HTTP API, has no database, and does not implement a
long-running service. Therefore, it has no OpenAPI specification, migrations,
deployment process, or production runbooks.
