import json
import re
import pathlib
from datetime import datetime
from typing import Any

DATETIME_FORMAT = "%Y/%m/%d %H:%M:%S"
DATETIME_PATTERN = re.compile(r"^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$")


def _process_value(value: Any) -> Any:
    if isinstance(value, list):
        seen = []
        for item in value:
            if item not in seen:
                seen.append(item)
        return seen
    elif isinstance(value, str):
        if DATETIME_PATTERN.match(value):
            try:
                dt = datetime.strptime(value, DATETIME_FORMAT)
                return dt.replace(year=2021).strftime(DATETIME_FORMAT)
            except ValueError:
                pass
        return re.sub(r"\s+", "", value)[::-1]
    return value


def process_data(data: dict) -> dict:
    return {k: _process_value(v) for k, v in data.items()}


class DataExtractor:
    def __init__(self, path: pathlib.Path):
        self.path = pathlib.Path(path)
        self.data: dict = {}
        self._processed_data: dict = {}
        self._load()

    def _load(self) -> None:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            print("Bad input")
            self.data = {}

    def process(self) -> dict:
        self._processed_data = process_data(self.data)
        return self._processed_data

    def save(self, output_path: pathlib.Path = None) -> pathlib.Path:
        if output_path is None:
            output_path = self.path.parent / (self.path.stem + "_processed" + self.path.suffix)
        output_path = pathlib.Path(output_path)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self._processed_data, f, indent=2)
        return output_path
