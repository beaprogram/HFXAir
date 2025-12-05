"""
Test suite for Flight Details API endpoints.
"""
from flask_app.tests.test_constants import HTTP_OK, TEST_FLIGHT_ID


def test_get_flight_details(client, monkeypatch):
    sample_flight = {
        "flight_number": "AC123",
        "airline": "Air Canada",
        "status": "On Time",
        "departure_time": "2025-11-06T15:30:00",
        "gate": "A5"
    }

    def fake_get_flight_by_id(flight_id):
        assert flight_id == TEST_FLIGHT_ID
        return sample_flight

    import flask_app.app as app
    monkeypatch.setattr(app, "get_flight_by_id", fake_get_flight_by_id)

    response = client.get(f"/flights/{TEST_FLIGHT_ID}")
    assert response.status_code == HTTP_OK
    assert response.json == sample_flight