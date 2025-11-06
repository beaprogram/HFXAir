import json
import jwt
import pytest
from app import SECRET  # same secret used in app.py


def test_login_success(client):
    data = {"flight_number": "AC123", "ticket_number": "TCK5678"}
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
    data = {"flight_number": "AC123", "ticket_number": "TCK5678"}
    response = client.post("/login", json=data)
    assert response.status_code == 200
    token = response.json.get("token")
    assert token is not None

    # Try decoding the token
    decoded = jwt.decode(token, SECRET, algorithms=["HS256"])
    assert "flight_no" in decoded
    assert "ticket_no" in decoded
    assert "exp" in decoded
    
