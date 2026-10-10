from helpers import login_as, register_member


def test_membership(client):
    register_member(client)
    assert client.get("/members/Ravi/membership").get_json()["membership_state"] == "active"
    assert client.patch("/members/Ravi/membership", json={"state": "suspended"}).status_code == 403
    login_as(client, "trainer")
    assert client.patch("/members/Ravi/membership", json={"state": "suspended"}).status_code == 200
    assert client.patch("/members/Ravi/membership", json={"state": "bad"}).status_code == 400
    assert client.get("/members/Nobody/membership").status_code == 404
