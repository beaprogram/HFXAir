"""
Test suite for Flights API endpoints.
"""
from flask_app.tests.test_constants import HTTP_OK


def test_get_flights_returns_list(client, monkeypatch):
    sample_flights = [
        {"flight_number": "AC123", "status": "On Time", "destination": "Toronto"},
        {"flight_number": "WS456", "status": "Delayed", "destination": "Vancouver"}
    ]

    # Mock DB call
    def fake_get_all_flights():
        return sample_flights

    import flask_app.app as app
    monkeypatch.setattr(app, "get_all_flights", fake_get_all_flights)

    response = client.get("/flights")
    assert response.status_code == HTTP_OK
    assert response.json == sample_flights