from helpers import register_member


def test_progress_and_chart(client):
    register_member(client)
    chart = client.get("/members/Ravi/progress/chart")
    assert chart.status_code == 200
    assert client.post("/members/Ravi/progress", json={"weight_kg": 0}).status_code == 400
    assert client.post("/members/Ravi/progress", json={"logged_at": "2026-01-01", "weight_kg": 78}).status_code == 201
    assert client.post("/members/Ravi/progress", json={"logged_at": "2026-02-01", "weight_kg": 76}).status_code == 201
    assert len(client.get("/members/Ravi/progress").get_json()) == 2
    chart = client.get("/members/Ravi/progress/chart")
    assert chart.status_code == 200
    assert chart.headers["Content-Type"].startswith("image/svg+xml")
    assert client.get("/members/Nobody/progress").status_code == 404
