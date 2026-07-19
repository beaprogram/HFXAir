"""
Test suite for Login API endpoints.
"""
import json
import jwt
import pytest
from flask_app.app import SECRET  # same secret used in app.py
import flask_app.app as app
from flask_app.tests.test_constants import (
    HTTP_OK,
    HTTP_BAD_REQUEST,
    HTTP_UNAUTHORIZED,
    TEST_FLIGHT_NUMBER,
    TEST_FLIGHT_NUMBER_ALT,
    TEST_FLIGHT_NUMBER_INVALID,
    TEST_TICKET_NUMBER,
    TEST_TICKET_NUMBER_ALT,
    TEST_TICKET_NUMBER_INVALID
)


def test_login_success(client, monkeypatch):
    monkeypatch.setattr(app, "check_db_for_ticket", lambda *_: True)
    data = {"flight_number": TEST_FLIGHT_NUMBER, "ticket_number": TEST_TICKET_NUMBER}
    response = client.post("/login", json=data)
    assert response.status_code == HTTP_OK
    assert "token" in response.json


def test_login_invalid(client, monkeypatch):
    monkeypatch.setattr(app, "check_db_for_ticket", lambda *_: False)
    data = {
        "flight_number": TEST_FLIGHT_NUMBER_INVALID,
        "ticket_number": TEST_TICKET_NUMBER_INVALID
    }
    response = client.post("/login", json=data)
    assert response.status_code == HTTP_UNAUTHORIZED
    assert "error" in response.json


def test_login_missing_fields(client):
    response = client.post("/login", json={"flight_number": TEST_FLIGHT_NUMBER_ALT})
    assert response.status_code == HTTP_BAD_REQUEST


@pytest.mark.parametrize("data,description", [
    ({"flight_number": TEST_FLIGHT_NUMBER_ALT}, "missing ticket_number"),
    ({"ticket_number": "TCK5678"}, "missing flight_number"),
    ({}, "both fields missing"),
    ({"flight_number": "", "ticket_number": ""}, "both fields empty"),
    ({"flight_number": TEST_FLIGHT_NUMBER_ALT, "ticket_number": None}, "ticket_number is None"),
    ({"flight_number": None, "ticket_number": "TCK5678"}, "flight_number is None"),
])
def test_login_missing_fields(client, data, description):
    response = client.post("/login", json=data)
    assert response.status_code == HTTP_BAD_REQUEST, f"Expected {HTTP_BAD_REQUEST} for case: {description}"
    assert "error" in response.json


def test_login_returns_valid_token(client, monkeypatch):
    monkeypatch.setattr(app, "check_db_for_ticket", lambda *_: True)
    data = {"flight_number": TEST_FLIGHT_NUMBER, "ticket_number": TEST_TICKET_NUMBER}
    response = client.post("/login", json=data)
    assert response.status_code == HTTP_OK
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
        "flight_number": TEST_FLIGHT_NUMBER,
        "ticket_number": TEST_TICKET_NUMBER
    })

    assert called.get("used"), "Expected DB query to be used"
    assert response.status_code == HTTP_OK
    assert "token" in response.json


def test_missing_token_returns_401(client):
    res = client.get("/protected-test")  # dummy route for testing
    assert res.status_code == HTTP_UNAUTHORIZED
    assert "error" in res.json


def test_invalid_token_returns_401(client):
    headers = {"Authorization": "Bearer invalid_token"}
    res = client.get("/protected-test", headers=headers)
    assert res.status_code == HTTP_UNAUTHORIZED


def test_valid_token_allows_access(client):
    token = jwt.encode(
        {"ticket_no": TEST_TICKET_NUMBER_ALT, "flight_no": TEST_FLIGHT_NUMBER_ALT},
        SECRET,
        algorithm="HS256"
    )
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/protected-test", headers=headers)
    assert res.status_code == HTTP_OK
    assert res.json == {"message": "Access granted"}
