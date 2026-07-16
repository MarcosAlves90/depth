# Testing Strategy

## Test pyramid

The project uses a small pyramid focused on deterministic behavior:

- **Unit:** data models and filesystem scanning rules; fast and isolated.
- **Integration:** real temporary Git repositories and the public CLI; these
  validate Git history, parent snapshots, branches, and exit codes.
- **E2E:** not currently applicable because the project has no deployed service,
  network endpoint, or external user interface.

## Running tests

```bash
python3 -m unittest discover -s tests -t .
```

The suite uses only Python's standard library. Git must be available for the
integration tests.

## Quality gate

Before delivery, run the test command above and compile the package:

```bash
python3 -m compileall -q object_scanner scan_objects.py
```

There is no `package.json`, CI configuration, or coverage tool in this minimal
repository. A coverage percentage is therefore not enforced yet; all critical
paths currently have explicit unit or integration coverage.

## Output artifact

Use `--output` to write a complete, structured JSON artifact. Terminal limits
do not truncate this file:

```bash
python3 scan_objects.py --no-fetch --pattern ITEM \
  --output scan.json ./service-a ./service-b
```

The artifact uses schema `depth.scan.v1` and contains the configuration,
summary, invalid services, current matches, historical commits, branches, tags,
commit snapshots, parent snapshots, files, lines, and matching content.

## Flaky tests

Tests create isolated temporary directories and repositories and do not depend
on network access, wall-clock timing, or external services.
