"""
Test suite for Subscribe API endpoints.
"""
import jwt
from flask_app.app import SECRET
from flask_app.tests.test_constants import (
    HTTP_OK,
    HTTP_UNAUTHORIZED,
    TEST_FLIGHT_NUMBER_ALT,
    TEST_TICKET_NUMBER_ALT,
    TEST_SHOP_ID
)


def test_subscribe_requires_auth(client):
    # no token
    res = client.post("/subscribe", json={"flight_id": TEST_SHOP_ID, "expo_token": "token123"})
    assert res.status_code == HTTP_UNAUTHORIZED
    assert "error" in res.json


def test_subscribe_success(client, monkeypatch):
    called = {}

    def fake_save_subscription(ticket_no, flight_id, expo_token):
        called["used"] = True

    import flask_app.app as app
    monkeypatch.setattr(app, "save_subscription", fake_save_subscription)

    token = jwt.encode(
        {"ticket_no": TEST_TICKET_NUMBER_ALT, "flight_no": TEST_FLIGHT_NUMBER_ALT},
        SECRET,
        algorithm="HS256"
    )
    headers = {"Authorization": f"Bearer {token}"}

    data = {"flight_id": TEST_SHOP_ID, "expo_token": "token123"}
    res = client.post("/subscribe", headers=headers, json=data)

    assert res.status_code == HTTP_OK
    assert res.json == {"message": "Subscribed"}
    assert called.get("used"), "save_subscription should be called"