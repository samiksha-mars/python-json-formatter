# Python JSON Formatter

A command-line tool to pretty-print, minify, and validate JSON files.
Uses only the Python standard library.

## Features

- Pretty-print with a configurable indent (default 2, or `--tab`)
- Minify to a single compact line (`--compact`)
- Sort object keys (`--sort-keys`)
- Validate without printing (`--check`), with the line and column of any syntax error
- Rewrite files in place (`--in-place`)
- Reads from stdin when no file (or `-`) is given
- Keeps non-ASCII characters as-is by default (`--ascii` to escape them)

## Usage

```bash
# Pretty-print a file
python3 json_formatter.py data.json

# Pretty-print from a pipe with sorted keys and 4-space indent
curl -s https://api.example.com/items | python3 json_formatter.py -s -i 4

# Minify
python3 json_formatter.py -c data.json > data.min.json

# Validate several files (exit code 1 if any is invalid)
python3 json_formatter.py --check config/*.json

# Reformat files in place
python3 json_formatter.py --in-place --sort-keys package.json
```

Errors point at the exact location:

```
$ python3 json_formatter.py --check broken.json
error: broken.json:3:1: Illegal trailing comma before end of object
```

Invalid files are never overwritten by `--in-place`, and processing continues with the next file.

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | All input was valid |
| 1 | At least one file was invalid or unreadable |
| 2 | Bad command-line arguments |

## Tests

```bash
python3 -m unittest
```
