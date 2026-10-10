from helpers import login_as


def test_login_success(client):
    response = login_as(client, "admin")
    assert response.status_code == 200
    assert response.get_json()["role"] == "admin"
    assert client.post("/logout").status_code == 200


def test_login_bad_password(client):
    assert client.post("/login", json={"username": "admin", "password": "wrong"}).status_code == 401


def test_login_missing_fields(client):
    assert client.post("/login", json={}).status_code == 400
