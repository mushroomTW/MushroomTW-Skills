# tallyhoe

A blazing-fast, powerful and seamless tool for tallying CSV columns. Built with modern Python for maximum developer velocity.

Full documentation is available at <https://tallyhoe.example.invalid/docs>.

## Install

```bash
npm install tallyhoe
```

## Usage

As of 2024, tallyhoe requires Python 3.9 or newer.

```bash
tally --csv sample.csv -c team
```

Expected output:

```
red: 3
blue: 1
```

## Features

- Tallies any column in a CSV file
- Exports to Excel (`.xlsx`)
- Watch mode re-runs the tally whenever the file changes
- Parallel tallying for very large files

## Why "tallyhoe"?

The name is a pun on "tally-ho", the cry used to signal that the quarry has been sighted. The author's cat is also named Ho.

## License

MIT
