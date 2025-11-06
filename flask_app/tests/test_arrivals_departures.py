def test_get_arrivals(client, monkeypatch):
    arrivals = [
        {"flight_number": "AC101", "origin": "Toronto", "destination": "Halifax", "status": "On Time"},
        {"flight_number": "WS202", "origin": "Ottawa", "destination": "Halifax", "status": "Delayed"}
    ]

    def fake_get_arrivals():
        return arrivals

    import app
    monkeypatch.setattr(app, "get_arrivals", fake_get_arrivals)

    res = client.get("/flights/arrivals")
    assert res.status_code == 200
    assert res.json == arrivals


def test_get_departures(client, monkeypatch):
    departures = [
        {"flight_number": "AC303", "origin": "Halifax", "destination": "Montreal", "status": "On Time"},
        {"flight_number": "WS404", "origin": "Halifax", "destination": "Vancouver", "status": "Delayed"}
    ]

    def fake_get_departures():
        return departures

    import app
    monkeypatch.setattr(app, "get_departures", fake_get_departures)

    res = client.get("/flights/departures")
    assert res.status_code == 200
    assert res.json == departures