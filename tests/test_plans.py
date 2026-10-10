from helpers import register_member


def test_plans(client):
    register_member(client)
    assert client.post("/members/Ravi/plan", json={"plan_type": "Muscle Gain"}).status_code == 201
    assert client.get("/members/Ravi/plans").get_json()[0]["plan_type"] == "Muscle Gain"
    assert client.post("/members/Ravi/plan", json={"plan_type": "Bad"}).status_code == 400
    assert client.get("/members/Nobody/plans").status_code == 404
