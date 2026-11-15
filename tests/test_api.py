"""Automated API tests using pytest and FastAPI TestClient."""

import csv

import pytest
from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def isolate_request_log(tmp_path, monkeypatch):
    """Keep test requests out of the real API monitoring log."""
    monkeypatch.setattr(main, "LOG_FILE", tmp_path / "test_api_requests.csv")


@pytest.mark.parametrize(
    ("endpoint", "payload", "expected_operation", "expected_result"),
    [
        ("/add", {"num1": 10, "num2": 5}, "addition", 15.0),
        ("/subtract", {"num1": 10, "num2": 5}, "subtraction", 5.0),
        ("/multiply", {"num1": 10, "num2": 5}, "multiplication", 50.0),
        ("/divide", {"num1": 10, "num2": 5}, "division", 2.0),
    ],
)
def test_arithmetic_endpoints(
    endpoint, payload, expected_operation, expected_result
):
    response = client.post(endpoint, json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["operation"] == expected_operation
    assert body["num1"] == payload["num1"]
    assert body["num2"] == payload["num2"]
    assert body["result"] == pytest.approx(expected_result)


def test_division_by_zero_returns_bad_request():
    response = client.post("/divide", json={"num1": 10, "num2": 0})

    assert response.status_code == 400
    assert response.json() == {"detail": "Division by zero is not allowed."}


def test_missing_number_is_rejected():
    response = client.post("/add", json={"num1": 10})

    assert response.status_code == 422


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_successful_requests_are_logged():
    response = client.post("/add", json={"num1": 7, "num2": 3})
    assert response.status_code == 200

    with main.LOG_FILE.open("r", newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert len(rows) == 1
    assert rows[0]["operation"] == "addition"
    assert float(rows[0]["result"]) == pytest.approx(10.0)
