# tallyhoe

A CLI tool for counting occurrences of values in a CSV column.

## Installation

Install from the local repository:

```bash
pip install .
```

Or install in development mode:

```bash
pip install -e .
```

**Requirements**: Python 3.11 or newer

## Quick Start

Run `tally` on a CSV file to count values in a column:

```bash
tally sample.csv -c team
```

Output:

```
     3  red
     1  blue
```

The output shows each distinct value and its count, sorted from most to least common.

## Usage

```
tally [-h] -c COLUMN [--json] [--top TOP] path
```

### Arguments

- `path` — path to a CSV file with a header row

### Options

- `-c, --column COLUMN` — column name to tally (required)
- `--json` — emit JSON instead of a text table
- `--top TOP` — show only the N most common values (0 = all, default)
- `-h, --help` — show help message

### Examples

Count values in the "team" column:

```bash
tally sample.csv -c team
```

Output as JSON:

```bash
tally sample.csv -c team --json
```

Show only the top 2 most common values:

```bash
tally sample.csv -c team --top 2
```

## Features

**Current**
- Tallies any column in a CSV file
- Outputs as text table or JSON
- Filters to top N results

**Planned**
- Watch mode — re-tally when the file changes
- Excel (`.xlsx`) import
- Parallel tallying for files over 1 GB

## Why "tallyhoe"?

The name is a pun on "tally-ho", the cry used to signal that the quarry has been sighted. The author's cat is also named Ho.

## License

MIT
