import argparse
import json
import sys

from .core import tally


def main(argv=None):
    parser = argparse.ArgumentParser(prog="tally", description="Tally values in a CSV column.")
    parser.add_argument("path", help="path to a CSV file with a header row")
    parser.add_argument("-c", "--column", required=True, help="column name to tally")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a text table")
    parser.add_argument("--top", type=int, default=0, help="show only the N most common values (0 = all)")
    args = parser.parse_args(argv)

    try:
        rows = tally(args.path, args.column)
    except FileNotFoundError:
        print(f"tally: no such file: {args.path}", file=sys.stderr)
        return 2
    except KeyError as exc:
        print(f"tally: no such column: {exc.args[0]}", file=sys.stderr)
        return 3

    if args.top:
        rows = rows[: args.top]
    if args.json:
        print(json.dumps(dict(rows), ensure_ascii=False))
    else:
        for value, count in rows:
            print(f"{count:>6}  {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
