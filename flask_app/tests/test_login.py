import json

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
    
