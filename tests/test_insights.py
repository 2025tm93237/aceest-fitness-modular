from helpers import login_as, register_member


def test_dashboard(client):
    assert client.get("/dashboard").status_code == 403
    login_as(client, "trainer")
    assert client.get("/dashboard").status_code == 200


def test_analytics_summary(client):
    assert client.get("/analytics/summary").status_code == 403
    login_as(client, "trainer")
    register_member(client)
    assert client.get("/analytics/summary").status_code == 200


def test_member_overview(client):
    register_member(client)
    overview = client.get("/members/Ravi/overview")
    assert overview.status_code == 200
    assert overview.get_json()["counts"]["sessions"] == 0
    assert client.get("/members/Nobody/overview").status_code == 404
