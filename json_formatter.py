#!/usr/bin/env python3
"""Pretty-print, minify, and validate JSON."""

import json


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
