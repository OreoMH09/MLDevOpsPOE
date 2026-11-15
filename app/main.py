"""FastAPI arithmetic API with CSV request logging for Evidently monitoring."""

from __future__ import annotations

import csv
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_FILE = PROJECT_ROOT / "logs" / "api_requests.csv"
LOG_COLUMNS = ["timestamp", "operation", "num1", "num2", "result"]
_LOG_LOCK = threading.Lock()


class NumberRequest(BaseModel):
    """Two numbers supplied by the API caller."""

    num1: float = Field(..., description="First number")
    num2: float = Field(..., description="Second number")


app = FastAPI(
    title="Arithmetic Operations API",
    description=(
        "A simple FastAPI project providing addition, subtraction, "
        "multiplication and division, with pytest and Evidently integration."
    ),
    version="1.0.0",
)


def log_successful_request(
    operation: str, num1: float, num2: float, result: float
) -> None:
    """Append one successful API request to the monitoring CSV file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "operation": operation,
        "num1": num1,
        "num2": num2,
        "result": result,
    }

    with _LOG_LOCK:
        file_exists = LOG_FILE.exists() and LOG_FILE.stat().st_size > 0
        with LOG_FILE.open("a", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=LOG_COLUMNS)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)


def calculate(
    operation: str,
    request: NumberRequest,
    calculation: Callable[[float, float], float],
) -> dict[str, float | str]:
    """Run a calculation, log the successful request and return the response."""
    result = calculation(request.num1, request.num2)
    log_successful_request(operation, request.num1, request.num2, result)
    return {
        "operation": operation,
        "num1": request.num1,
        "num2": request.num2,
        "result": result,
    }


@app.get("/", tags=["Information"])
def home() -> dict[str, str]:
    return {
        "message": "Arithmetic Operations API is running.",
        "documentation": "/docs",
        "available_operations": "/operations",
    }


@app.get("/health", tags=["Information"])
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/operations", tags=["Information"])
def operations() -> dict[str, list[str]]:
    return {"operations": ["add", "subtract", "multiply", "divide"]}


@app.post("/add", tags=["Arithmetic"])
def add_numbers(request: NumberRequest) -> dict[str, float | str]:
    """Return the sum of two numbers."""
    return calculate("addition", request, lambda a, b: a + b)


@app.post("/subtract", tags=["Arithmetic"])
def subtract_numbers(request: NumberRequest) -> dict[str, float | str]:
    """Return the difference between two numbers (num1 - num2)."""
    return calculate("subtraction", request, lambda a, b: a - b)


@app.post("/multiply", tags=["Arithmetic"])
def multiply_numbers(request: NumberRequest) -> dict[str, float | str]:
    """Return the product of two numbers."""
    return calculate("multiplication", request, lambda a, b: a * b)


@app.post("/divide", tags=["Arithmetic"])
def divide_numbers(request: NumberRequest) -> dict[str, float | str]:
    """Return num1 divided by num2; reject division by zero."""
    if request.num2 == 0:
        raise HTTPException(status_code=400, detail="Division by zero is not allowed.")
    return calculate("division", request, lambda a, b: a / b)
