def test_get_flight_details(client, monkeypatch):
    sample_flight = {
        "flight_number": "AC123",
        "airline": "Air Canada",
        "status": "On Time",
        "departure_time": "2025-11-06T15:30:00",
        "gate": "A5"
    }

    def fake_get_flight_by_id(flight_id):
        assert flight_id == 1
        return sample_flight

    import app
    monkeypatch.setattr(app, "get_flight_by_id", fake_get_flight_by_id)

    response = client.get("/flights/1")
    assert response.status_code == 200
    assert response.json == sample_flight