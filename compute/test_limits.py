import time
from fastapi.testclient import TestClient

import sandbox
from main import app

client = TestClient(app)

def post(body):
    return client.post("/differentiate", json=body)

def test_normal_problem_still_works():
    assert post({"expression": "x^2 * sin(x)"}).status_code == 200

def test_huge_power_times_out(monkeypatch):
    monkeypatch.setattr(sandbox, "TIMEOUT_SECONDS", 1)
    start = time.monotonic()
    r = post({"expression": "9^9^9^9"})
    assert r.status_code == 422
    assert time.monotonic() - start < 3

def test_injection_still_rejected_inside_sandbox():
    assert post({"expression": "__import__('os')"}).status_code == 400