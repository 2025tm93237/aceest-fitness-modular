from helpers import login_as


def test_movement_create_list_duplicate(client):
    login_as(client, "trainer")
    assert client.post("/movements", json={"title": "Squat", "muscle_group": "Legs"}).status_code == 201
    assert client.get("/movements").get_json()[0]["title"] == "Squat"
    assert client.post("/movements", json={"title": "Squat"}).status_code == 409
