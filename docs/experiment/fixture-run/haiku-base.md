# tallyhoe

A blazing-fast, powerful and seamless tool for tallying CSV columns. Built with modern Python for maximum developer velocity.

## Installation

```bash
pip install tallyhoe
```

### Requirements

tallyhoe requires Python 3.11 or newer.

## Usage

### Basic Tally

```bash
tally sample.csv -c team
```

Output:

```
     3  red
     1  blue
```

### JSON Output

Use the `--json` flag to output results as JSON:

```bash
tally sample.csv -c team --json
```

Output:

```json
{"red": 3, "blue": 1}
```

### Show Only Top N Results

Use the `--top` flag to limit results:

```bash
tally sample.csv -c team --top 1
```

Output:

```
     3  red
```

## Features

- Tallies any column in a CSV file
- JSON output support
- Filter to show only top N values

## Planned Features

- [ ] Watch mode — re-tally when the file changes
- [ ] Excel (`.xlsx`) export
- [ ] Parallel tallying for files over 1 GB

## Why "tallyhoe"?

The name is a pun on "tally-ho", the cry used to signal that the quarry has been sighted. The author's cat is also named Ho.

## License

MIT
