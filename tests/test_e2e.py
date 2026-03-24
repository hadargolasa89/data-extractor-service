"""
End-to-end tests for the Data Extractor HTTP service (pytest).
These tests spin up the FastAPI app via TestClient and exercise the /process endpoint.
"""
import pytest
from fastapi.testclient import TestClient

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app

client = TestClient(app)


EXAMPLE_INPUT = {
    "value1": "1999/10/10 10:15:15",
    "value2": "sdfg fgfgf ffgfgrrrt sdfgsdf bmbmbmbp",
    "value3": ["bar", "baz", "foo", "bar", "baz", 5],
    "value4": "1997/10/10 10:15:15z",
}


class TestHealthEndpoint:
    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_ok(self):
        response = client.get("/health")
        assert response.json() == {"status": "ok"}


class TestProcessEndpoint:
    def test_returns_200_for_valid_json(self):
        response = client.post("/process", json=EXAMPLE_INPUT)
        assert response.status_code == 200

    def test_datetime_year_changed_to_2021(self):
        response = client.post("/process", json={"v": "1999/10/10 10:15:15"})
        assert response.json()["v"] == "2021/10/10 10:15:15"

    def test_datetime_preserves_date_and_time(self):
        response = client.post("/process", json={"v": "2000/03/25 08:30:00"})
        assert response.json()["v"] == "2021/03/25 08:30:00"

    def test_datetime_already_2021_unchanged(self):
        response = client.post("/process", json={"v": "2021/06/15 12:00:00"})
        assert response.json()["v"] == "2021/06/15 12:00:00"

    def test_string_whitespace_removed_and_reversed(self):
        response = client.post("/process", json={"v": "hello world"})
        assert response.json()["v"] == "dlrowolleh"

    def test_string_only_reversal_when_no_spaces(self):
        response = client.post("/process", json={"v": "abcde"})
        assert response.json()["v"] == "edcba"

    def test_invalid_datetime_treated_as_string(self):
        # Has trailing "z" — not a valid datetime format
        response = client.post("/process", json={"v": "1997/10/10 10:15:15z"})
        result = response.json()["v"]
        assert "1997" not in result  # year was NOT replaced

    def test_list_duplicates_removed(self):
        response = client.post("/process", json={"v": ["bar", "baz", "foo", "bar", "baz", 5]})
        assert response.json()["v"] == ["bar", "baz", "foo", 5]

    def test_list_order_preserved(self):
        response = client.post("/process", json={"v": ["c", "a", "b", "a", "c"]})
        assert response.json()["v"] == ["c", "a", "b"]

    def test_list_no_duplicates_unchanged(self):
        response = client.post("/process", json={"v": [1, 2, 3]})
        assert response.json()["v"] == [1, 2, 3]

    def test_numeric_value_unchanged(self):
        response = client.post("/process", json={"v": 42})
        assert response.json()["v"] == 42

    def test_full_example_input(self):
        response = client.post("/process", json=EXAMPLE_INPUT)
        result = response.json()
        assert result["value1"] == "2021/10/10 10:15:15"
        assert result["value3"] == ["bar", "baz", "foo", 5]
        assert "value2" in result
        assert "value4" in result

    def test_empty_object_returns_empty(self):
        response = client.post("/process", json={})
        assert response.json() == {}

    def test_invalid_json_returns_400(self):
        response = client.post(
            "/process",
            content=b"not valid json{{{",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 400
        assert response.json()["error"] == "Bad input"

    def test_non_object_json_returns_400(self):
        response = client.post("/process", json=["a", "b"])
        assert response.status_code == 400
        assert response.json()["error"] == "Bad input"
