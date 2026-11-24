import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def post(body):
    return client.post("/limit", json=body)


@pytest.mark.parametrize("expression, point, direction, expected", [
    ("sin(x)/x", "0", "+-", "1"),
    ("(1+1/x)^x", "oo", "-", "E"),
    ("x^2", "2", "+-", "4"),
    ("1/x", "0", "+", "oo"),
    ("1/x", "0", "-", "-oo"),
])
def test_limit_exists(expression, point, direction, expected):
    r = post({"expression": expression, "point": point, "direction": direction})
    assert r.status_code == 200
    assert r.json()["result"] == expected


@pytest.mark.parametrize("expression, point", [
    ("1/x", "0"),       # zoo: different infinities from each side
    ("sin(1/x)", "0"),  # AccumBounds: oscillates
    ("sin(x)", "oo"),   # AccumBounds: oscillates forever
    ("abs(x)/x", "0"),  # ValueError: left = -1, right = 1
])
def test_limit_does_not_exist(expression, point):
    r = post({"expression": expression, "point": point})
    assert r.status_code == 422
    assert "does not exist" in r.json()["detail"]


def test_missing_point_returns_422():
    assert post({"expression": "x"}).status_code == 422


def test_invalid_direction_returns_422():
    assert post({"expression": "x", "point": "0", "direction": "up"}).status_code == 422


def test_injection_in_point_returns_400():
    assert post({"expression": "x", "point": "__import__('os')"}).status_code == 400