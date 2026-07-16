# Local setup

## Prerequisites

1. Install Python 3.10 or newer.
2. Install Git if historical analysis is required.
3. Clone the repository and enter the project directory.

There are no external dependencies or package installation steps.

## Verification

Run:

```bash
python3 scan_objects.py --help
python3 -m unittest discover -s tests -t .
python3 -m compileall -q object_scanner scan_objects.py
```

## Execution

For an analysis without remote updates:

```bash
python3 scan_objects.py --no-fetch --pattern ITEM /path/to/service
```

To generate complete evidence:

```bash
python3 scan_objects.py --no-fetch --pattern ITEM \
  --output scan.json /path/to/service
```

The path may be a regular tree or any subdirectory inside a Git repository.
Invalid paths are reported in the summary and do not stop other services from
being scanned.

Use `--pattern` more than once to search multiple items. `--item` is an alias;
at least one item is required.
