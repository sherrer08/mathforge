from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def post(body):
    return client.post("/differentiate", json=body)

def test_power_rule():
    r = post({"expression": "x^2"})
    assert r.status_code == 200
    assert r.json()["result"] == "2*x"

def test_second_derivative():
    r = post({"expression": "3x^3 - 2x", "order": 2})
    assert r.status_code == 200
    assert r.json()["result"] == "18*x"

def test_other_variable():
    r = post({"expression": "t^3", "variable": "t"})
    assert r.json()["result"] == "3*t**2"

def test_unbalanced_parentheses_returns_400():
    assert post({"expression": "sin(x"}).status_code == 400

def test_injection_returns_400():
    r = post({"expression": "__import__('builtins').print('pwned')"})
    assert r.status_code == 400

def test_empty_expression_returns_422():
    assert post({"expression": ""}).status_code == 422

def test_order_too_high_returns_422():
    assert post({"expression": "x", "order": 50}).status_code == 422

def test_multi_letter_variable_returns_422():
    assert post({"expression": "x", "variable": "xy"}).status_code == 422

def test_e_is_eulers_number():
    assert post({"expression": "e^x"}).json()["result"] == "exp(x)"
