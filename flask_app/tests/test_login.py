import json
import jwt
import pytest
from flask_app.app import SECRET  # same secret used in app.py
import flask_app.app as app

def test_login_success(client):
    data = {"flight_number": "AC450", "ticket_number": "TCK456"}
    response = client.post("/login", json=data)
    assert response.status_code == 200
    assert "token" in response.json

def test_login_invalid(client):
    data = {"flight_number": "WRONG", "ticket_number": "INVALID"}
    response = client.post("/login", json=data)
    assert response.status_code == 401
    assert "error" in response.json

def test_login_missing_fields(client):
    response = client.post("/login", json={"flight_number": "AC123"})
    assert response.status_code == 400

@pytest.mark.parametrize("data,description", [
    ({"flight_number": "AC123"}, "missing ticket_number"),
    ({"ticket_number": "TCK5678"}, "missing flight_number"),
    ({}, "both fields missing"),
    ({"flight_number": "", "ticket_number": ""}, "both fields empty"),
    ({"flight_number": "AC123", "ticket_number": None}, "ticket_number is None"),
    ({"flight_number": None, "ticket_number": "TCK5678"}, "flight_number is None"),
])
def test_login_missing_fields(client, data, description):
    response = client.post("/login", json=data)
    assert response.status_code == 400, f"Expected 400 for case: {description}"
    assert "error" in response.json


def test_login_returns_valid_token(client):
    data = {"flight_number": "AC301", "ticket_number": "TCK456"}
    response = client.post("/login", json=data)
    assert response.status_code == 200
    token = response.json.get("token")
    assert token is not None

    # Try decoding the token
    decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
    assert "flight_no" in decoded
    assert "ticket_no" in decoded
    assert "exp" in decoded
    
def test_login_uses_db_query(monkeypatch, client):

    called = {}

    # Mock DB function
    def fake_check_db(flight_no, ticket_no):
        called["used"] = True
        return True  # simulate found record

    # Temporarily replace real function
    monkeypatch.setattr(app, "check_db_for_ticket", fake_check_db)

    response = client.post("/login", json={
        "flight_number": "AC450",
        "ticket_number": "TCK456"
    })

    assert called.get("used"), "Expected DB query to be used"
    assert response.status_code == 200
    assert "token" in response.json




def test_missing_token_returns_401(client):
    res = client.get("/protected-test")  # dummy route for testing
    assert res.status_code == 401
    assert "error" in res.json


def test_invalid_token_returns_401(client):
    headers = {"Authorization": "Bearer invalid_token"}
    res = client.get("/protected-test", headers=headers)
    assert res.status_code == 401


def test_valid_token_allows_access(client):
    token = jwt.encode({"ticket_no": "TCK123", "flight_no": "AC123"}, SECRET, algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/protected-test", headers=headers)
    assert res.status_code == 200
    assert res.json == {"message": "Access granted"}