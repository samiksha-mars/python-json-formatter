import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from json_formatter import JsonError, format_json, main, parse


class ParseTest(unittest.TestCase):

    def test_valid(self):
        self.assertEqual(parse('{"a": [1, true, null]}'), {"a": [1, True, None]})

    def test_error_location(self):
        with self.assertRaises(JsonError) as ctx:
            parse('{\n  "a": 1,\n}', "data.json")
        self.assertEqual((ctx.exception.lineno, ctx.exception.colno), (3, 1))
        self.assertTrue(str(ctx.exception).startswith("data.json:3:1:"))

    def test_empty_input_is_invalid(self):
        with self.assertRaises(JsonError):
            parse("")


class FormatJsonTest(unittest.TestCase):

    def test_pretty(self):
        self.assertEqual(format_json({"a": [1]}), '{\n  "a": [\n    1\n  ]\n}\n')

    def test_compact(self):
        self.assertEqual(format_json({"a": [1, 2]}, compact=True), '{"a":[1,2]}\n')

    def test_sort_keys(self):
        self.assertEqual(format_json({"b": 1, "a": 2}, compact=True, sort_keys=True), '{"a":2,"b":1}\n')

    def test_unicode(self):
        self.assertEqual(format_json("é", compact=True), '"é"\n')
        self.assertEqual(format_json("é", compact=True, ensure_ascii=True), '"\\u00e9"\n')

    def test_tab_indent(self):
        self.assertEqual(format_json([1], indent="\t"), "[\n\t1\n]\n")


class MainTest(unittest.TestCase):

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def run_main(self, *args, stdin=""):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err), mock.patch("sys.stdin", io.StringIO(stdin)):
            code = main(list(args))
        return code, out.getvalue(), err.getvalue()

    def test_stdin(self):
        code, out, _ = self.run_main("-c", stdin='{ "a" : 1 }')
        self.assertEqual((code, out), (0, '{"a":1}\n'))

    def test_check_valid_prints_nothing(self):
        code, out, err = self.run_main("--check", stdin="[]")
        self.assertEqual((code, out, err), (0, "", ""))

    def test_check_invalid(self):
        code, out, err = self.run_main("--check", stdin="[1,]")
        self.assertEqual(code, 1)
        self.assertIn("<stdin>:1:", err)

    def test_in_place(self):
        path = self.root / "data.json"
        path.write_text('{"b":1,"a":2}', encoding="utf-8")
        code, out, _ = self.run_main("--in-place", "--sort-keys", str(path))
        self.assertEqual((code, out), (0, ""))
        self.assertEqual(path.read_text(encoding="utf-8"), '{\n  "a": 2,\n  "b": 1\n}\n')

    def test_in_place_leaves_invalid_file_untouched(self):
        path = self.root / "bad.json"
        path.write_text("{oops", encoding="utf-8")
        code, _, _ = self.run_main("--in-place", str(path))
        self.assertEqual(code, 1)
        self.assertEqual(path.read_text(encoding="utf-8"), "{oops")

    def test_continues_after_bad_file(self):
        good = self.root / "good.json"
        good.write_text("[1]", encoding="utf-8")
        code, out, err = self.run_main("-c", str(self.root / "missing.json"), str(good))
        self.assertEqual(code, 1)
        self.assertEqual(out, "[1]\n")
        self.assertIn("cannot read", err)

    def test_in_place_rejects_stdin(self):
        with self.assertRaises(SystemExit) as ctx:
            self.run_main("--in-place")
        self.assertEqual(ctx.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
