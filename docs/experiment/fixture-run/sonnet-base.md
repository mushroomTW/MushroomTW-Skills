# tallyhoe

A small CLI tool that tallies the values in one column of a CSV file, most common first.

## Requirements

- Python 3.11 or newer

## Install

`tallyhoe` is a Python package built with hatchling; there is no published package to install yet, so install it from source in editable mode:

```bash
git clone <this-repo-url>
cd tallyhoe
pip install -e .
```

This installs the `tally` command.

## Usage

```bash
tally sample.csv -c team
```

Given `sample.csv`:

```
name,team,role
ana,red,scout
bo,blue,scout
cy,red,medic
di,red,scout
```

Output:

```
     3  red
     1  blue
```

### Options

```
usage: tally [-h] -c COLUMN [--json] [--top TOP] path

positional arguments:
  path                 path to a CSV file with a header row

options:
  -h, --help           show this help message and exit
  -c, --column COLUMN  column name to tally
  --json               emit JSON instead of a text table
  --top TOP            show only the N most common values (0 = all)
```

Examples:

```bash
# JSON output
tally sample.csv -c team --json
# {"red": 3, "blue": 1}

# Only the most common value
tally sample.csv -c team --top 1
#      3  red
```

If the file doesn't exist or the column isn't in the header row, `tally` prints an error to stderr and exits with a non-zero status (2 for a missing file, 3 for an unknown column).

## Features

- Tallies any column in a CSV file with a header row
- Sorts results by count, most common first
- Optional JSON output (`--json`)
- Optional limit to the top N results (`--top`)

Watch mode, Excel input/output, and parallel tallying for large files are planned but not implemented yet — see [ROADMAP.md](ROADMAP.md).

## Why "tallyhoe"?

The name is a pun on "tally-ho", the cry used to signal that the quarry has been sighted. The author's cat is also named Ho.

## License

No `LICENSE` file is currently included in this repository, so no license terms are granted. If you plan to reuse this code, contact the maintainer or add a license file first.
