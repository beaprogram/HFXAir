import json
import jwt
import json
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