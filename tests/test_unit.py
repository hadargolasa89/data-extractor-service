"""
Unit tests for DataExtractor class using the unittest module.
"""
import json
import pathlib
import tempfile
import unittest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data_extractor import DataExtractor, process_data


def _write_json(data: dict, path: pathlib.Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f)


class TestDataExtractorLoad(unittest.TestCase):
    def test_loads_valid_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = pathlib.Path(tmpdir) / "input.json"
            _write_json({"key": "value"}, p)
            extractor = DataExtractor(p)
            self.assertEqual(extractor.data, {"key": "value"})

    def test_bad_json_prints_and_empties_data(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = pathlib.Path(tmpdir) / "bad.json"
            p.write_text("not valid json {{{", encoding="utf-8")
            from io import StringIO
            import sys as _sys
            captured = StringIO()
            _sys.stdout = captured
            extractor = DataExtractor(p)
            _sys.stdout = _sys.__stdout__
            self.assertIn("Bad input", captured.getvalue())
            self.assertEqual(extractor.data, {})

    def test_accepts_pathlib_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = pathlib.Path(tmpdir) / "input.json"
            _write_json({}, p)
            extractor = DataExtractor(p)
            self.assertIsInstance(extractor.path, pathlib.Path)

    def test_accepts_string_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = pathlib.Path(tmpdir) / "input.json"
            _write_json({}, p)
            extractor = DataExtractor(str(p))
            self.assertEqual(extractor.data, {})


class TestDataExtractorProcess(unittest.TestCase):
    def _make_extractor(self, data: dict) -> DataExtractor:
        with tempfile.TemporaryDirectory() as tmpdir:
            p = pathlib.Path(tmpdir) / "input.json"
            _write_json(data, p)
            extractor = DataExtractor(p)
        return extractor

    def test_datetime_year_changed_to_2021(self):
        extractor = self._make_extractor({"v": "1999/10/10 10:15:15"})
        result = extractor.process()
        self.assertEqual(result["v"], "2021/10/10 10:15:15")

    def test_datetime_preserves_month_day_time(self):
        extractor = self._make_extractor({"v": "2000/03/25 08:30:00"})
        result = extractor.process()
        self.assertEqual(result["v"], "2021/03/25 08:30:00")

    def test_string_reversed_and_whitespace_removed(self):
        extractor = self._make_extractor({"v": "hello world"})
        result = extractor.process()
        self.assertEqual(result["v"], "dlrowolleh")

    def test_string_tabs_removed(self):
        extractor = self._make_extractor({"v": "a\tb"})
        result = extractor.process()
        self.assertEqual(result["v"], "ba")

    def test_invalid_datetime_treated_as_string(self):
        extractor = self._make_extractor({"v": "1997/10/10 10:15:15z"})
        result = extractor.process()
        self.assertNotIn("1997", result["v"])

    def test_list_removes_duplicates(self):
        extractor = self._make_extractor({"v": ["bar", "baz", "foo", "bar", "baz", 5]})
        result = extractor.process()
        self.assertEqual(result["v"], ["bar", "baz", "foo", 5])

    def test_list_preserves_order(self):
        extractor = self._make_extractor({"v": ["c", "a", "b", "a"]})
        result = extractor.process()
        self.assertEqual(result["v"], ["c", "a", "b"])

    def test_numeric_value_unchanged(self):
        extractor = self._make_extractor({"v": 99})
        result = extractor.process()
        self.assertEqual(result["v"], 99)

    def test_process_returns_dict(self):
        extractor = self._make_extractor({"v": "hello"})
        result = extractor.process()
        self.assertIsInstance(result, dict)

    def test_full_example(self):
        data = {
            "value1": "1999/10/10 10:15:15",
            "value2": "sdfg fgfgf ffgfgrrrt sdfgsdf bmbmbmbp",
            "value3": ["bar", "baz", "foo", "bar", "baz", 5],
            "value4": "1997/10/10 10:15:15z",
        }
        extractor = self._make_extractor(data)
        result = extractor.process()
        self.assertEqual(result["value1"], "2021/10/10 10:15:15")
        self.assertEqual(result["value3"], ["bar", "baz", "foo", 5])


class TestDataExtractorSave(unittest.TestCase):
    def test_save_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = pathlib.Path(tmpdir) / "input.json"
            with open(p, "w") as f:
                json.dump({"v": "hello world"}, f)
            extractor = DataExtractor(p)
            extractor.process()
            out = extractor.save()
            self.assertTrue(out.exists())

    def test_save_default_filename(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = pathlib.Path(tmpdir) / "input.json"
            with open(p, "w") as f:
                json.dump({"v": "hello"}, f)
            extractor = DataExtractor(p)
            extractor.process()
            out = extractor.save()
            self.assertEqual(out.name, "input_processed.json")

    def test_save_custom_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = pathlib.Path(tmpdir) / "input.json"
            custom = pathlib.Path(tmpdir) / "custom_output.json"
            with open(p, "w") as f:
                json.dump({"v": "hello"}, f)
            extractor = DataExtractor(p)
            extractor.process()
            out = extractor.save(custom)
            self.assertEqual(out, custom)
            self.assertTrue(custom.exists())

    def test_save_content_is_valid_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = pathlib.Path(tmpdir) / "input.json"
            with open(p, "w") as f:
                json.dump({"v": "hello world"}, f)
            extractor = DataExtractor(p)
            extractor.process()
            out = extractor.save()
            with open(out) as f:
                saved = json.load(f)
            self.assertEqual(saved["v"], "dlrowolleh")


class TestProcessDataFunction(unittest.TestCase):
    def test_empty_dict(self):
        self.assertEqual(process_data({}), {})

    def test_multiple_keys(self):
        result = process_data({"a": "hi", "b": [1, 1, 2]})
        self.assertEqual(result["a"], "ih")
        self.assertEqual(result["b"], [1, 2])


if __name__ == "__main__":
    unittest.main()
