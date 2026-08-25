# tallyhoe

Tally the values in one column of a CSV file from the command line — sorted counts, an optional JSON output, and a "top N" filter.

## Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Command reference](#command-reference)
- [Limitations](#limitations)
- [Roadmap](#roadmap)
- [License](#license)
- [Why "tallyhoe"?](#why-tallyhoe)

## Requirements

- Python 3.11 or newer (`pyproject.toml` sets `requires-python = ">=3.11"`)

## Installation

tallyhoe is not currently published to a package index. Install it from a local checkout:

```bash
pip install -e .
```

This registers the `tally` command, defined by the `tally = "tallyhoe.cli:main"` entry point in `pyproject.toml`. tallyhoe declares no runtime dependencies.

> [!NOTE]
> To try the CLI without installing anything, run it straight from the source tree: `PYTHONPATH=src python -m tallyhoe.cli ...` (or the `set`/`$env:` equivalent on Windows).

## Usage

Given `sample.csv`:

```csv
name,team,role
ana,red,scout
bo,blue,scout
cy,red,medic
di,red,scout
```

```bash
tally sample.csv -c team
```

Output:

```
     3  red
     1  blue
```

Counts are sorted from most to least common; ties keep the order the values first appeared in the file.

Pass `--json` for machine-readable output:

```bash
tally sample.csv -c team --json
```

```
{"red": 3, "blue": 1}
```

Use `--top` to limit how many rows are shown:

```bash
tally sample.csv -c role --top 1
```

```
     3  scout
```

## Command reference

```
usage: tally [-h] -c COLUMN [--json] [--top TOP] path

positional arguments:
  path                 path to a CSV file with a header row

options:
  -h, --help           show this help message and exit
  -c, --column COLUMN  column name to tally (required)
  --json               emit JSON instead of a text table
  --top TOP            show only the N most common values (0 = all, default)
```

Errors and exit codes:

| Situation | Message | Exit code |
| --- | --- | --- |
| File not found | `tally: no such file: <path>` | 2 |
| Column missing from the CSV header | `tally: no such column: <column>` | 3 |

## Limitations

- The CSV must have a header row; `-c/--column` is matched against that header exactly (case-sensitive).
- The whole file is read into memory before counting (`csv.DictReader` plus `collections.Counter`) — there is no streaming path for very large files.
- The file is read as UTF-8; other encodings are not handled.

## Roadmap

> [!NOTE]
> Everything below is planned only — `ROADMAP.md` states plainly that "nothing here is implemented yet." None of it exists in the current CLI.

- Watch mode: re-run the tally when the file changes
- Excel (`.xlsx`) input
- Parallel tallying for files over 1 GB

## License

This repository does not include a `LICENSE` file, so no license terms are confirmed. Treat the code as all-rights-reserved until the maintainer adds one.

## Why "tallyhoe"?

The name is a pun on "tally-ho," the cry used to signal that the quarry has been sighted. The author's cat is also named Ho.
