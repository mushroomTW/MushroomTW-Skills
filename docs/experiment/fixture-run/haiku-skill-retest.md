# tallyhoe

A tool for tallying values in CSV columns.

## Quick Start

```bash
tally sample.csv -c team
```

Output:

```
     3  red
     1  blue
```

## Installation

Requires Python 3.11 or newer.

```bash
pip install -e .
```

## Usage

Count occurrences of values in a specified column:

```bash
tally <csv-file> -c <column-name>
```

### Options

- `--json` — emit JSON instead of a text table
- `--top N` — show only the N most common values (0 = all, default: 0)

Example with JSON output:

```bash
tally sample.csv -c team --json
```

Output:

```json
{"red": 3, "blue": 1}
```

Limit results to the top 1 value:

```bash
tally sample.csv -c team --top 1
```

Output:

```
     3  red
```

## Features

- Counts occurrences of values in a CSV column
- Supports JSON output via `--json`
- Filters results with `--top` to show only the most common values

## Roadmap

Planned features are documented in [ROADMAP.md](ROADMAP.md).

## Why "tallyhoe"?

The name is a pun on "tally-ho", the cry used to signal that the quarry has been sighted. The author's cat is also named Ho.
