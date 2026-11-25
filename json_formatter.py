#!/usr/bin/env python3
"""Pretty-print, minify, and validate JSON."""

import argparse
import json
import sys
from pathlib import Path


class JsonError(ValueError):
    """Invalid JSON, with a human-friendly location."""

    def __init__(self, source, error):
        self.source = source
        self.lineno = error.lineno
        self.colno = error.colno
        super().__init__(f"{source}:{error.lineno}:{error.colno}: {error.msg}")


def parse(text, source="<stdin>"):
    """Parse JSON text, raising JsonError with the location of any syntax error."""
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise JsonError(source, error) from None


def format_json(data, indent=2, compact=False, sort_keys=False, ensure_ascii=False):
    """Serialize data as pretty-printed (or compact) JSON text with a trailing newline."""
    if compact:
        text = json.dumps(data, separators=(",", ":"), sort_keys=sort_keys, ensure_ascii=ensure_ascii)
    else:
        text = json.dumps(data, indent=indent, sort_keys=sort_keys, ensure_ascii=ensure_ascii)
    return text + "\n"


def build_parser():
    parser = argparse.ArgumentParser(description="Pretty-print, minify, and validate JSON.")
    parser.add_argument("files", nargs="*", default=["-"], help="JSON files to process (default: stdin)")
    layout = parser.add_mutually_exclusive_group()
    layout.add_argument("-i", "--indent", type=int, default=2, help="spaces per indent level (default: 2)")
    layout.add_argument("--tab", action="store_true", help="indent with tabs")
    layout.add_argument("-c", "--compact", action="store_true", help="minify to a single line")
    parser.add_argument("-s", "--sort-keys", action="store_true", help="sort object keys")
    parser.add_argument("--ascii", action="store_true", help="escape non-ASCII characters")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="only validate; print nothing for valid input")
    mode.add_argument("--in-place", action="store_true", help="rewrite files instead of printing")
    return parser


def read_source(name):
    if name == "-":
        return sys.stdin.read(), "<stdin>"
    return Path(name).read_text(encoding="utf-8"), name


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.indent < 0:
        parser.error("--indent must not be negative")
    if args.in_place and "-" in args.files:
        parser.error("--in-place cannot be used with stdin")

    options = dict(
        indent="\t" if args.tab else args.indent,
        compact=args.compact,
        sort_keys=args.sort_keys,
        ensure_ascii=args.ascii,
    )
    status = 0
    for name in args.files:
        try:
            text, source = read_source(name)
            data = parse(text, source)
        except (OSError, UnicodeDecodeError) as error:
            print(f"error: cannot read {name}: {getattr(error, 'strerror', None) or error}", file=sys.stderr)
            status = 1
            continue
        except JsonError as error:
            print(f"error: {error}", file=sys.stderr)
            status = 1
            continue

        if args.check:
            continue
        output = format_json(data, **options)
        if args.in_place:
            if output != text:
                Path(name).write_text(output, encoding="utf-8")
        else:
            sys.stdout.write(output)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
