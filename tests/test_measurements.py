from helpers import register_member


def test_measurements(client):
    register_member(client)
    assert client.post("/members/Ravi/measurements", json={"weight_kg": 78, "body_fat_pct": 20}).status_code == 201
    assert client.get("/members/Ravi/measurements").status_code == 200
    assert client.get("/members/Nobody/measurements").status_code == 404
