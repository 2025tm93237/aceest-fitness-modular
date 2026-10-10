from helpers import login_as, register_member


def test_sessions(client):
    register_member(client)
    login_as(client, "trainer")
    assert client.post("/movements", json={"title": "Squat"}).status_code == 201
    client.post("/logout")
    assert client.post("/members/Ravi/sessions", json={"movement_title": "Squat", "minutes": 45}).status_code == 201
    assert client.get("/members/Ravi/sessions").get_json()[0]["movement_title"] == "Squat"
    assert client.post("/members/Ravi/sessions", json={"movement_title": "Missing"}).status_code == 404
    assert client.get("/members/Nobody/sessions").status_code == 404
