from helpers import register_member


def test_targets(client):
    register_member(client)
    assert client.post("/members/Ravi/targets", json={}).status_code == 400
    assert client.post("/members/Ravi/targets", json={"target_type": "Weight", "target_value": 70}).status_code == 201
    assert client.get("/members/Ravi/targets").get_json()[0]["target_type"] == "Weight"
    assert client.get("/members/Nobody/targets").status_code == 404
