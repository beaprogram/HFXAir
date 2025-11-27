import jwt
from flask_app.app import SECRET

def test_subscribe_requires_auth(client):
    # no token
    res = client.post("/subscribe", json={"flight_id": 1, "expo_token": "token123"})
    assert res.status_code == 401
    assert "error" in res.json


def test_subscribe_success(client, monkeypatch):
    called = {}

    def fake_save_subscription(ticket_no, flight_id, expo_token):
        called["used"] = True

    import flask_app.app as app
    monkeypatch.setattr(app, "save_subscription", fake_save_subscription)

    token = jwt.encode({"ticket_no": "TCK123", "flight_no": "AC123"}, SECRET, algorithm="HS256")
    headers = {"Authorization": f"Bearer {token}"}

    data = {"flight_id": 1, "expo_token": "token123"}
    res = client.post("/subscribe", headers=headers, json=data)

    assert res.status_code == 200
    assert res.json == {"message": "Subscribed"}
    assert called.get("used"), "save_subscription should be called"