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
